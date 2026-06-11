"""Tiny in-memory vehicle tools so pattern cells run offline. Swap for real APIs/DAOs in production."""
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
