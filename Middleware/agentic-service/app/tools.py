"""Framework-agnostic tools the collect-stage agents call. The headline tool is `fetch_page` —
fetch a URL and return its title + outbound links + image URLs — so an agent can discover and curate
resource links (this platform's 'collection' = link discovery only; content extraction is ingestion).
"""
import urllib.request
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

_DOC_EXT = (".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".csv")
_IMG_EXT = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg")


class _Parser(HTMLParser):
    def __init__(self, base: str):
        super().__init__()
        self.base, self.title, self._in_title = base, "", False
        self.links: list[str] = []
        self.images: list[str] = []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "a" and d.get("href"):
            self.links.append(urljoin(self.base, d["href"]))
        elif tag == "img" and d.get("src"):
            self.images.append(urljoin(self.base, d["src"]))
        elif tag == "title":
            self._in_title = True

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def classify(url: str) -> str:
    low = url.lower().split("?")[0]
    if low.endswith(_IMG_EXT):
        return "image"
    if low.endswith(_DOC_EXT):
        return "document"
    return "page"


def fetch_page(url: str, max_links: int = 50, same_domain: bool = True) -> dict:
    """Fetch a URL; return {url, title, links:[{url,type}], images:[...]}. Links are de-duped and
    (by default) restricted to the seed's domain, so an agent gets a clean candidate set."""
    req = urllib.request.Request(url, headers={"User-Agent": "VKP-Agent/0.1 (+vehicle-knowledge-platform)"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read(3_000_000).decode("utf-8", "ignore")
    p = _Parser(url)
    p.feed(html)

    host = urlparse(url).netloc
    seen, links = set(), []
    for href in p.links:
        h = href.split("#")[0]
        if not h.startswith("http") or h in seen:
            continue
        if same_domain and urlparse(h).netloc != host:
            continue
        seen.add(h)
        links.append({"url": h, "type": classify(h)})
        if len(links) >= max_links:
            break
    images = []
    for src in p.images:
        if src.startswith("http") and src not in seen:
            seen.add(src)
            images.append(src)
        if len(images) >= 20:
            break
    return {"url": url, "title": p.title.strip()[:200], "links": links, "images": images}
