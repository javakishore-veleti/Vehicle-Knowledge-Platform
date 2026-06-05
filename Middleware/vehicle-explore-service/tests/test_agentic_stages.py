"""Unit tests for the explore-side agentic stages (collect/index for the classic frameworks): the
tolerant JSON parsers, the chunk fallback, the fetch_page tool, and that all four classic frameworks
register collect+index. No live services / SDK calls (SDK imports stay lazy inside functions)."""
import json

from app import agentic_stages, tools
# importing the agent modules registers their collect/index stages
from app import crewai_agent, haystack_agent, langgraph_agent, llamaindex_agent  # noqa: F401

CLASSIC = {"crewai", "haystack", "langgraph", "llamaindex"}


def test_all_classic_frameworks_register_collect_and_index():
    assert CLASSIC.issubset(set(agentic_stages.collect_frameworks()))
    assert CLASSIC.issubset(set(agentic_stages.index_frameworks()))


def test_parse_links_objects():
    out = agentic_stages.parse_links('[{"url":"http://x/a","type":"page","title":"A"}]')
    assert out == [{"url": "http://x/a", "type": "page", "title": "A"}]


def test_parse_links_array_of_json_strings():
    # the Groq-llama quirk: items are JSON-encoded strings rather than objects
    payload = json.dumps([json.dumps({"url": "http://y/b", "type": "image"})])
    out = agentic_stages.parse_links(payload)
    assert out and out[0]["url"] == "http://y/b" and out[0]["type"] == "image"


def test_parse_links_garbage():
    assert agentic_stages.parse_links("no json") == []
    assert agentic_stages.parse_links("") == []


def test_parse_chunks():
    assert agentic_stages.parse_chunks('["one", "two"]') == ["one", "two"]
    assert agentic_stages.parse_chunks("nope") == []


def test_naive_chunks_bounded():
    chunks = agentic_stages._naive_chunks("word " * 5000)
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
    assert "https://www.toyota.com/rav4/" in urls
    assert all("other.com" not in u for u in urls)
