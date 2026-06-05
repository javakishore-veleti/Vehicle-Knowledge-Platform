"""Unit tests for the agentic-service — registry coverage, the tolerant JSON parsers, the chunk
fallback, and the fetch_page tool (mocked HTML). No live services / SDK calls needed: each framework
module registers on import while its heavy SDK imports stay lazy (inside functions)."""
import json

from app import registry, tools
from app import frameworks as _frameworks  # noqa: F401 — registers all frameworks
from app.frameworks import _base

NEW_SDKS = {"openai-agents", "strands", "google-adk", "msagent"}


def test_registry_covers_all_stages_for_all_new_sdks():
    m = registry.matrix()
    for stage in ("search", "collect", "index"):
        assert NEW_SDKS.issubset(set(m[stage])), f"{stage} missing: {NEW_SDKS - set(m[stage])}"


def test_parse_links_objects():
    out = _base.parse_links('[{"url":"http://x/a","type":"page","title":"A"}]')
    assert out == [{"url": "http://x/a", "type": "page", "title": "A"}]


def test_parse_links_array_of_json_strings():
    # the Groq-llama quirk: an array whose items are JSON-encoded strings, not objects
    payload = json.dumps([json.dumps({"url": "http://y/b", "type": "image"})])
    out = _base.parse_links(payload)
    assert out and out[0]["url"] == "http://y/b" and out[0]["type"] == "image"


def test_parse_links_garbage():
    assert _base.parse_links("no json here") == []
    assert _base.parse_links("") == []


def test_parse_chunks():
    assert _base.parse_chunks('["one", "two"]') == ["one", "two"]
    assert _base.parse_chunks("nope") == []


def test_naive_chunks_bounded():
    chunks = _base._naive_chunks("word " * 5000)
    assert 1 <= len(chunks) <= 12


def test_classify():
    assert tools.classify("http://x/brochure.pdf") == "document"
    assert tools.classify("http://x/hero.png") == "image"
    assert tools.classify("http://x/rav4/") == "page"


def test_fetch_page_parses_and_filters(monkeypatch):
    html = ('<html><head><title>Toyota</title></head><body>'
            '<a href="/rav4/">RAV4</a><a href="http://other.com/x">off</a>'
            '<img src="/img/hero.png"></body></html>')

    class _Resp:
        def __enter__(self):
            return self
        def __exit__(self, *a):
            return False
        def read(self, n=None):
            return html.encode()

    monkeypatch.setattr("urllib.request.urlopen", lambda *a, **k: _Resp())
    r = tools.fetch_page("https://www.toyota.com/")
    assert r["title"] == "Toyota"
    urls = [l["url"] for l in r["links"]]
    assert "https://www.toyota.com/rav4/" in urls      # same-domain kept
    assert all("other.com" not in u for u in urls)      # cross-domain dropped
