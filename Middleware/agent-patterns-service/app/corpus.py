"""In-memory document corpus + keyword retriever (with brand / brochure / snapshot scoping) so RAG-style
cells run offline. Swap retrieve() for pgVector/Mongo later — same (query, k, ...) -> [{text,score,source}]."""
import re

_DOCS = [
    {"source": "toyota/rav4-prime", "text": "The Toyota RAV4 Prime is a plug-in hybrid SUV with an EPA-rated 42 miles of electric range and ~94 MPGe; combined output is about 302 hp."},
    {"source": "toyota/camry", "text": "The Toyota Camry is a midsize sedan; the hybrid returns up to 51 mpg city, base price around $28,400."},
    {"source": "toyota/rav4-prime/brochure", "text": "RAV4 Prime brochure: 0-60 mph in 5.7 s, available electronic on-demand AWD, 42-mile EV range, Toyota Safety Sense 2.5+ standard."},
    {"source": "ford/f-150", "text": "The Ford F-150 is a full-size pickup with a maximum towing capacity up to 13,500 lb depending on configuration."},
    {"source": "ford/f-150/brochure", "text": "F-150 brochure: available Pro Power Onboard generator, BlueCruise hands-free highway driving, up to 13,500 lb towing."},
    {"source": "tesla/model-3", "text": "The Tesla Model 3 is a battery-electric sedan with EPA range starting around 272 miles on the base rear-wheel-drive trim."},
    {"source": "tesla/model-3/safety", "text": "The Tesla Model 3 includes Autopilot with adaptive cruise control and automatic emergency braking as standard safety features."},
    {"source": "safety/recalls", "text": "Vehicle recalls are tracked by NHTSA; owners can look up open recalls by VIN on the NHTSA website."},
    {"source": "honda/civic", "text": "The Honda Civic is a fuel-efficient compact car returning up to ~36 mpg combined on many trims, with Honda Sensing safety features."},
]


def retrieve(query: str, k: int = 3, source_prefix: str = None, contains: str = None) -> list:
    docs = _DOCS
    if source_prefix:
        docs = [d for d in docs if d["source"].lower().startswith(source_prefix.lower())]
    if contains:
        docs = [d for d in docs if contains.lower() in d["source"].lower()]
    terms = set(re.findall(r"[a-z0-9]+", (query or "").lower()))
    scored = []
    for d in docs:
        words = set(re.findall(r"[a-z0-9]+", d["text"].lower()))
        score = len(terms & words)
        if score:
            scored.append({**d, "score": score})
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:k] or ([{**docs[0], "score": 0}] if docs else [])
