"""In-memory vehicle tools so ReAct/ReWOO cells run offline. Swap for real APIs/crawlers in production."""
_SPECS = {
    "rav4 prime": {"type": "plug-in hybrid SUV", "electric_range_mi": 42, "mpge": 94, "base_price_usd": 43690, "seats": 5},
    "camry": {"type": "midsize sedan (hybrid avail.)", "mpg": 51, "base_price_usd": 28400, "seats": 5},
    "f-150": {"type": "full-size pickup", "towing_lb": 13500, "mpg": 25, "base_price_usd": 38565, "seats": 6},
    "tacoma": {"type": "mid-size pickup", "towing_lb": 6500, "mpg": 21, "base_price_usd": 31500, "seats": 5},
    "model 3": {"type": "battery electric sedan", "electric_range_mi": 272, "base_price_usd": 38990, "seats": 5},
    "civic": {"type": "compact car", "mpg": 36, "base_price_usd": 24650, "seats": 5},
}
_BRANDS = {"toyota", "ford", "tesla", "honda", "chevrolet", "gmc"}
_FIELD_ALIASES = {"price": "base_price_usd", "base_price": "base_price_usd", "msrp": "base_price_usd",
                  "cost": "base_price_usd", "range": "electric_range_mi", "electric_range": "electric_range_mi",
                  "towing": "towing_lb", "tow": "towing_lb", "towing_capacity": "towing_lb", "mileage": "mpg"}

# --- mock web/crawl/recall/dealer tools for the ReAct use cases ---
_SITEMAP = {
    "toyota.com": ["/rav4-prime", "/camry", "/trucks/tacoma", "/about", "/dealers", "/contact"],
    "toyota.com/rav4-prime": ["/rav4-prime/specs", "/rav4-prime/trims", "/rav4-prime/pricing", "/rav4-prime/gallery"],
    "ford.com": ["/f-150", "/about", "/dealers"],
}
_RECALLS = {
    "rav4 prime|2021": ["NHTSA 21V-XXX: fuel pump may stop running, increasing crash risk"],
    "f-150|2022": ["NHTSA 22V-YYY: windshield wiper motor may fail"],
}


def _norm_model(model: str) -> str:
    return " ".join(w for w in (model or "").strip().lower().replace("-", " ").split() if w not in _BRANDS).replace("f 150", "f-150")


def vehicle_spec(model: str, field: str = "") -> dict:
    """Look up specs for a known model (brand words + casing tolerated). `field` optional."""
    key = _norm_model(model)
    rec = _SPECS.get(key) or next((v for k, v in _SPECS.items() if k in key or key in k), None)
    if rec is None:
        return {"model": model, "error": "unknown model", "known": known_models()}
    if field:
        f = _FIELD_ALIASES.get(field.strip().lower(), field.strip().lower())
        return {"model": key, f: rec.get(f, "unknown")}
    return {"model": key, **rec}


def known_models() -> list:
    return sorted(_SPECS)


def _norm_url(url: str) -> str:
    return (url or "").lower().replace("https://", "").replace("http://", "").replace("www.", "").rstrip("/")


def crawl_page(url: str) -> dict:
    """Fetch a web page; returns the outbound links found on it (mock site map)."""
    key = _norm_url(url)
    links = _SITEMAP.get(key) or _SITEMAP.get(key.split("/")[0], [])
    return {"url": url, "links": links or ["(no links found)"]}


def find_moved(url: str) -> dict:
    """Given a 404 URL, search the site for the page's likely new location (mock)."""
    slug = _norm_url(url).split("/")[-1]
    for base, links in _SITEMAP.items():
        for l in links:
            if slug and slug in l.lower():
                return {"old": url, "found": base + l}
    return {"old": url, "found": "not found — try the on-site search"}


def nhtsa_recalls(model: str, year: str = "") -> dict:
    """Look up NHTSA safety recalls for a vehicle model / year (mock)."""
    key = f"{_norm_model(model)}|{(year or '').strip()}"
    return {"model": model, "year": year,
            "recalls": _RECALLS.get(key, ["No open recalls found for this model/year (mock NHTSA)"])}


def dealer_inventory(model: str, zip_code: str = "") -> dict:
    """Find local dealer inventory/stock for a model near a ZIP code (mock)."""
    return {"model": model, "zip": zip_code,
            "stock": [{"dealer": "City Motors", "distance_mi": 4, "units": 3},
                      {"dealer": "Metro Auto", "distance_mi": 11, "units": 1}]}
