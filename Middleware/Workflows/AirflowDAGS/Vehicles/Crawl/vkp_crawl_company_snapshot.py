"""vkp_crawl_company_snapshot — Vehicles / Crawl.

Recursively crawls a company's root links with a real (Playwright/Chromium) headless
browser so JavaScript-rendered automaker sites yield real content, and stores everything
as a FILESYSTEM SNAPSHOT (not Postgres) so dropping the DB never forces a re-crawl.

Layout (per company), under VKP_CRAWL_SNAPSHOT_DIR (host-mounted):
  <Company Name>/
    crawl-00001.json        # a list of <= 250 page elements
    crawl-00002.json
    images/<uuid>.<ext>      # each downloaded image, named by UUID
    __COMPLETED__/manifest.json   # marker: presence => skip re-crawl

Each element: {url, depth, title, text, images:[{image_id, src, file}], links_count, fetched_at}.

Idempotency: if <Company>/__COMPLETED__ exists, the run is skipped.

Storage toggle (conf.storage_backend, or env VKP_SNAPSHOT_STORAGE_BACKEND): "local" (default) writes
to the mounted folder; "s3" | "azure" | "gcs" write to AWS S3 / Azure Blob / Google Cloud Storage —
so the same DAG deployed in AWS/Azure/GCP persists snapshots to object storage. The target bucket/
container is conf.storage_location (or env VKP_SNAPSHOT_STORAGE_LOCATION):
  - s3:    's3://my-bucket/vkp-snapshots'   (creds via IAM role / AWS_* env; region via AWS_REGION)
  - azure: 'my-container/vkp-snapshots'     (AZURE_STORAGE_CONNECTION_STRING, or *_ACCOUNT_URL + MI)
  - gcs:   'gs://my-bucket/vkp-snapshots'   (GOOGLE_APPLICATION_CREDENTIALS / ADC)
The SDKs (boto3 / azure-storage-blob / google-cloud-storage) ship in the Airflow image; each is
imported lazily, so a missing SDK only errors if you actually select that backend.

Expected conf:
  { "company_id": "<uuid>",
    "company_base_url": "http://host.docker.internal:8081",   # company-service (roots source)
    "max_pages": 1000, "max_depth": 100, "max_images_per_page": 8,
    "storage_backend": "local", "storage_location": null,     # e.g. "s3" + "s3://bucket/prefix"
    # Responsible-crawling controls:
    "respect_robots": true,            # obey robots.txt (default on)
    "request_delay_seconds": 1.0,      # polite delay between page fetches (honors robots Crawl-delay)
    "user_agent": null }               # honest UA override (used for robots + the browser)
"""
from __future__ import annotations

import json
import logging
import os
import re
import time
import urllib.request
from collections import deque
from datetime import datetime, timezone
from urllib.parse import urlparse
from uuid import uuid4

from airflow import DAG
from airflow.operators.python import PythonOperator

log = logging.getLogger(__name__)

MAX_TEXT = 50_000
MAX_IMG_BYTES = 5_000_000
BATCH = 250
COMPANY_PATH = "/admin/company/service/v1/crud/companies/{cid}"
RESOURCES_PATH = "/admin/company/service/v1/crud/companies/{cid}/resources"

# Look like a real browser to reduce anti-bot (Akamai etc.) blocks. Not guaranteed.
REAL_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
           "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
BLOCK_MARKERS = ("access denied", "pardon our interruption", "unusual traffic",
                 "are you a human", "verify you are human", "request unsuccessful")
# Masks the most obvious automation tells before any page script runs.
STEALTH_JS = """
Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
window.chrome = window.chrome || { runtime: {} };
const _q = window.navigator.permissions && window.navigator.permissions.query;
if (_q) { window.navigator.permissions.query = (p) =>
  p && p.name === 'notifications' ? Promise.resolve({state: Notification.permission}) : _q(p); }
"""

_CT_EXT = {
    "image/jpeg": ".jpg", "image/jpg": ".jpg", "image/png": ".png", "image/gif": ".gif",
    "image/webp": ".webp", "image/svg+xml": ".svg", "image/avif": ".avif", "image/bmp": ".bmp",
}


# ----------------------------- storage backends -----------------------------
class LocalFsStorage:
    def __init__(self, base: str):
        self.base = base

    def _p(self, rel: str) -> str:
        return os.path.join(self.base, rel)

    def exists(self, rel: str) -> bool:
        return os.path.exists(self._p(rel))

    def write_text(self, rel: str, text: str) -> None:
        path = self._p(rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)

    def write_bytes(self, rel: str, data: bytes) -> None:
        path = self._p(rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as fh:
            fh.write(data)


JSON_CT = "application/json; charset=utf-8"


def _parse_bucket(location, scheme: str):
    """'s3://bucket/prefix' | 'gs://bucket/prefix' | 'bucket/prefix' | 'bucket' -> (bucket, prefix/)."""
    if not location:
        raise RuntimeError(
            f"storage_location is required for the '{scheme}' backend "
            f"(e.g. '{scheme}://my-bucket/vkp-snapshots' or 'my-bucket')")
    s = str(location)
    for p in (f"{scheme}://", "s3://", "gs://"):
        if s.startswith(p):
            s = s[len(p):]
            break
    s = s.strip("/")
    parts = s.split("/", 1)
    bucket = parts[0]
    prefix = (parts[1].rstrip("/") + "/") if len(parts) > 1 and parts[1] else ""
    return bucket, prefix


class S3Storage:
    """AWS S3 backend. storage_location: 's3://bucket/prefix' or 'bucket'. Credentials come from the
    standard AWS chain (IAM role / AWS_ACCESS_KEY_ID env / profile); region from AWS_REGION."""

    def __init__(self, location):
        try:
            import boto3  # noqa: F401  (lazy: only this backend needs it)
        except ImportError as e:
            raise RuntimeError("S3 backend needs boto3 — add it to the Airflow image (pip install boto3).") from e
        import boto3
        self.bucket, self.prefix = _parse_bucket(location, "s3")
        self._c = boto3.client("s3")

    def _key(self, rel: str) -> str:
        return f"{self.prefix}{rel}"

    def exists(self, rel: str) -> bool:
        from botocore.exceptions import ClientError
        try:
            self._c.head_object(Bucket=self.bucket, Key=self._key(rel))
            return True
        except ClientError:
            return False

    def write_text(self, rel: str, text: str) -> None:
        self._c.put_object(Bucket=self.bucket, Key=self._key(rel), Body=text.encode("utf-8"), ContentType=JSON_CT)

    def write_bytes(self, rel: str, data: bytes) -> None:
        self._c.put_object(Bucket=self.bucket, Key=self._key(rel), Body=data)


class AzureBlobStorage:
    """Azure Blob backend. storage_location: 'container' or 'container/prefix'. Auth via
    AZURE_STORAGE_CONNECTION_STRING, or AZURE_STORAGE_ACCOUNT_URL + DefaultAzureCredential (managed identity)."""

    def __init__(self, location):
        try:
            from azure.storage.blob import ContainerClient
        except ImportError as e:
            raise RuntimeError("Azure backend needs azure-storage-blob (pip install azure-storage-blob).") from e
        if not location:
            raise RuntimeError("storage_location is required for 'azure' (e.g. 'my-container' or 'my-container/vkp').")
        s = str(location).strip("/")
        parts = s.split("/", 1)
        container = parts[0]
        self.prefix = (parts[1].rstrip("/") + "/") if len(parts) > 1 and parts[1] else ""
        conn = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
        if conn:
            self._c = ContainerClient.from_connection_string(conn, container_name=container)
        else:
            acct = os.environ.get("AZURE_STORAGE_ACCOUNT_URL")
            if not acct:
                raise RuntimeError("Azure backend needs AZURE_STORAGE_CONNECTION_STRING or AZURE_STORAGE_ACCOUNT_URL.")
            from azure.identity import DefaultAzureCredential
            self._c = ContainerClient(account_url=acct, container_name=container, credential=DefaultAzureCredential())

    def _name(self, rel: str) -> str:
        return f"{self.prefix}{rel}"

    def exists(self, rel: str) -> bool:
        return self._c.get_blob_client(self._name(rel)).exists()

    def write_text(self, rel: str, text: str) -> None:
        self._c.upload_blob(self._name(rel), text.encode("utf-8"), overwrite=True)

    def write_bytes(self, rel: str, data: bytes) -> None:
        self._c.upload_blob(self._name(rel), data, overwrite=True)


class GcsStorage:
    """Google Cloud Storage backend. storage_location: 'gs://bucket/prefix' or 'bucket'. Auth via
    GOOGLE_APPLICATION_CREDENTIALS (service-account JSON) or Application Default Credentials."""

    def __init__(self, location):
        try:
            from google.cloud import storage
        except ImportError as e:
            raise RuntimeError("GCS backend needs google-cloud-storage (pip install google-cloud-storage).") from e
        bucket, self.prefix = _parse_bucket(location, "gs")
        self._bucket = storage.Client().bucket(bucket)

    def _name(self, rel: str) -> str:
        return f"{self.prefix}{rel}"

    def exists(self, rel: str) -> bool:
        return self._bucket.blob(self._name(rel)).exists()

    def write_text(self, rel: str, text: str) -> None:
        self._bucket.blob(self._name(rel)).upload_from_string(text, content_type=JSON_CT)

    def write_bytes(self, rel: str, data: bytes) -> None:
        self._bucket.blob(self._name(rel)).upload_from_string(data)


def make_storage(conf: dict):
    """Feature toggle: conf.storage_backend (or env VKP_SNAPSHOT_STORAGE_BACKEND) selects the backend;
    conf.storage_location (or env VKP_SNAPSHOT_STORAGE_LOCATION) is the bucket/container target."""
    backend = (conf.get("storage_backend") or os.environ.get("VKP_SNAPSHOT_STORAGE_BACKEND") or "local").lower()
    location = conf.get("storage_location") or os.environ.get("VKP_SNAPSHOT_STORAGE_LOCATION")
    if backend == "local":
        return LocalFsStorage(os.environ.get("VKP_CRAWL_SNAPSHOT_DIR", "/opt/airflow/crawl-snapshot"))
    if backend == "s3":
        return S3Storage(location)
    if backend == "azure":
        return AzureBlobStorage(location)
    if backend == "gcs":
        return GcsStorage(location)
    raise ValueError(f"Unknown storage_backend '{backend}' (use: local | s3 | azure | gcs).")


# ------------------------------- helpers ------------------------------------
def _get_text(url: str, timeout: int = 15) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "VKP-Crawler/0.1"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read(2_000_000).decode(resp.headers.get_content_charset() or "utf-8", "replace")


def _host(url: str) -> str:
    return urlparse(url).netloc.lower().removeprefix("www.")


def _reg_domain(url_or_host: str) -> str:
    """Registered domain (eTLD+1 heuristic): last two labels, e.g.
    automobiles.honda.com -> honda.com. Lets a root on one subdomain crawl its siblings."""
    host = url_or_host if "/" not in url_or_host else urlparse(url_or_host).netloc
    parts = host.split(":")[0].lower().split(".")
    return ".".join(parts[-2:]) if len(parts) >= 2 else host


def _folder(name: str) -> str:
    return re.sub(r"[^\w .\-]", "_", name).strip() or "company"


def _looks_blocked(page) -> bool:
    try:
        title = (page.title() or "").lower()
        body = (page.inner_text("body") or "")[:400].lower()
    except Exception:  # noqa: BLE001
        return False
    return any(m in title or m in body for m in BLOCK_MARKERS)


def _ext(content_type: str, url: str) -> str:
    ext = _CT_EXT.get((content_type or "").split(";")[0].strip().lower())
    if ext:
        return ext
    path_ext = os.path.splitext(urlparse(url).path)[1].lower()
    return path_ext if 1 < len(path_ext) <= 5 else ".img"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ------------------------------- crawl --------------------------------------
class RobotsGate:
    """Per-host robots.txt gate + polite rate-limit (the responsible-crawling controls).

    Honors Disallow rules and Crawl-delay for the configured user-agent. Permissive on errors
    (unreachable robots.txt -> allow), strict on explicit Disallow. When disabled, allows all but
    still applies the configured delay.
    """

    def __init__(self, enabled: bool, user_agent: str, default_delay: float):
        self.enabled = enabled
        self.user_agent = user_agent
        self.default_delay = max(0.0, default_delay)
        self._parsers: dict = {}

    def _parser(self, url: str):
        from urllib.parse import urlsplit
        from urllib.robotparser import RobotFileParser
        parts = urlsplit(url)
        key = (parts.scheme, parts.netloc)
        if key in self._parsers:
            return self._parsers[key]
        rp = RobotFileParser()
        try:
            rp.set_url(f"{parts.scheme}://{parts.netloc}/robots.txt")
            rp.read()
        except Exception as exc:  # noqa: BLE001 — unreachable robots.txt -> be permissive
            log.warning("robots.txt unreadable for %s://%s (%s) — allowing", parts.scheme, parts.netloc, exc)
            rp = None
        self._parsers[key] = rp
        return rp

    def allowed(self, url: str) -> bool:
        if not self.enabled:
            return True
        rp = self._parser(url)
        if rp is None:
            return True
        try:
            return rp.can_fetch(self.user_agent, url)
        except Exception:  # noqa: BLE001
            return True

    def delay(self, url: str) -> float:
        d = self.default_delay
        if self.enabled:
            rp = self._parser(url)
            if rp is not None:
                try:
                    cd = rp.crawl_delay(self.user_agent)
                    if cd:
                        d = max(d, float(cd))
                except Exception:  # noqa: BLE001
                    pass
        return d


def _crawl(company_name, roots, conf, storage):
    from playwright.sync_api import sync_playwright  # lazy: keeps DAG parseable without playwright

    folder = _folder(company_name)
    if storage.exists(f"{folder}/__COMPLETED__"):
        log.info("Snapshot for '%s' already completed — skipping.", company_name)
        return {"skipped": True, "company": company_name}

    max_pages = int(conf.get("max_pages") or 100000)
    max_depth = int(conf.get("max_depth") or 10000)
    max_img = int(conf.get("max_images_per_page") or 100000)
    # Stay within each root's registered domain (e.g. honda.com), across subdomains.
    allowed = {_reg_domain(r) for r in roots}

    # Responsible crawling: honest UA + robots.txt + polite rate-limit (all configurable).
    user_agent = conf.get("user_agent") or REAL_UA
    gate = RobotsGate(bool(conf.get("respect_robots", True)), user_agent,
                      float(conf.get("request_delay_seconds") or 0.0))
    robots_skipped = 0

    visited: set[str] = set()
    queue: deque[tuple[str, int]] = deque((r, 0) for r in roots)
    elements: list[dict] = []
    file_idx = 0
    img_total = 0
    page_count = 0

    def flush():
        nonlocal file_idx, elements
        if not elements:
            return
        file_idx += 1
        storage.write_text(f"{folder}/crawl-{file_idx:05d}.json",
                           json.dumps(elements, ensure_ascii=False))
        elements = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, args=[
            "--no-sandbox", "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled",
        ])
        context = browser.new_context(
            user_agent=user_agent,
            locale="en-US",
            timezone_id="America/New_York",
            viewport={"width": 1366, "height": 900},
            extra_http_headers={"Accept-Language": "en-US,en;q=0.9"},
        )
        context.add_init_script(STEALTH_JS)
        page = context.new_page()
        try:
            while queue and page_count < max_pages:
                url, depth = queue.popleft()
                if url in visited:
                    continue
                visited.add(url)
                if not gate.allowed(url):
                    robots_skipped += 1
                    log.info("robots.txt disallows — skipping %s", url)
                    continue
                wait = gate.delay(url)   # polite rate-limit (honors robots Crawl-delay)
                if wait:
                    time.sleep(wait)
                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=15000)
                    page.wait_for_timeout(1200)  # let SPA + any anti-bot sensor run
                    if _looks_blocked(page):
                        # Akamai-style: first hit denied, then the sensor cookie is set —
                        # a reload often passes.
                        page.wait_for_timeout(2500)
                        page.reload(wait_until="domcontentloaded", timeout=15000)
                        page.wait_for_timeout(1500)
                except Exception as exc:  # noqa: BLE001
                    log.warning("goto failed %s: %s", url, exc)
                    continue
                page_count += 1
                blocked = _looks_blocked(page)
                log.info("[%d/%d] depth=%d queued=%d%s  %s",
                         page_count, max_pages, depth, len(queue), " BLOCKED" if blocked else "", url)

                title = (page.title() or "")[:250]
                text = (page.inner_text("body") or "")[:MAX_TEXT]
                links = page.eval_on_selector_all("a[href]", "els => els.map(e => e.href)")
                img_srcs = page.eval_on_selector_all("img[src]", "els => els.map(e => e.currentSrc || e.src)")

                images = []
                seen_src = set()
                for src in img_srcs:
                    if len(images) >= max_img:
                        break
                    if not src or not src.startswith("http") or src in seen_src:
                        continue
                    seen_src.add(src)
                    try:
                        resp = context.request.get(src, timeout=8000)
                        if not resp.ok:
                            continue
                        ctype = (resp.headers.get("content-type") or "").lower()
                        if not ctype.startswith("image/"):
                            continue  # skip HTML redirects / bot-block pages returned for an img src
                        data = resp.body()
                        if not data or len(data) > MAX_IMG_BYTES:
                            continue
                        uid = uuid4().hex
                        rel = f"{folder}/images/{uid}{_ext(ctype, src)}"
                        storage.write_bytes(rel, data)
                        images.append({"image_id": uid, "src": src, "file": rel.split('/', 1)[1]})
                        img_total += 1
                    except Exception:  # noqa: BLE001
                        continue

                elements.append({
                    "url": url, "depth": depth, "title": title, "text": text,
                    "images": images, "links_count": len(links), "fetched_at": _now(),
                })
                if len(elements) >= BATCH:
                    flush()

                if depth < max_depth:
                    for href in links:
                        nxt = (href or "").split("#")[0]
                        if nxt.startswith("http") and _reg_domain(nxt) in allowed and nxt not in visited:
                            queue.append((nxt, depth + 1))
        finally:
            browser.close()

    flush()
    manifest = {
        "company": company_name, "roots": roots,
        "pages": page_count, "files": file_idx, "images": img_total,
        "robots_skipped": robots_skipped, "user_agent": user_agent,
        "respect_robots": gate.enabled, "request_delay_seconds": gate.default_delay,
        "completed_at": _now(),
    }
    storage.write_text(f"{folder}/__COMPLETED__/manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    log.info("Crawl complete for '%s': %s", company_name, manifest)
    return manifest


def crawl_company(**context):
    conf = (context.get("dag_run").conf or {}) if context.get("dag_run") else {}
    company_id = conf.get("company_id")
    company_base_url = (conf.get("company_base_url") or "http://host.docker.internal:8081").rstrip("/")
    if not company_id:
        raise ValueError("conf.company_id is required")

    company = json.loads(_get_text(company_base_url + COMPANY_PATH.format(cid=company_id)))["company"]
    company_name = company["name"]
    resources = json.loads(_get_text(company_base_url + RESOURCES_PATH.format(cid=company_id))).get("resources", [])
    roots = [r["resourceLink"] for r in resources if r.get("resourceLink")]
    if not roots:
        log.warning("Company '%s' has no root resources — nothing to crawl.", company_name)
        return {"skipped": True, "reason": "no roots"}

    log.info("Crawling '%s' from %d root(s)", company_name, len(roots))
    return _crawl(company_name, roots, conf, make_storage(conf))


with DAG(
    dag_id="vkp_crawl_company_snapshot",
    description="Headless-browser recursive crawl of a company's sites into a filesystem snapshot.",
    schedule=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["vkp", "vehicles", "crawl", "playwright"],
) as dag:
    PythonOperator(task_id="crawl_company", python_callable=crawl_company)
