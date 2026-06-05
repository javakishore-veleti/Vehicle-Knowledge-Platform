"""RAGAS-style faithfulness eval for the search pipeline.

Faithfulness = fraction of the answer's atomic factual claims that are SUPPORTED by the retrieved
context (the same metric RAGAS computes via claim decomposition + NLI). Runs a search against the
live explore service, then judges the answer with an LLM (Groq by default — free).

Run:  ./.venv/bin/python -m eval.faithfulness        (exit 1 if mean < threshold — CI-gateable)
Env:  VKP_EXPLORE_URL (default :8090), VKP_EVAL_LLM_BASE_URL/_API_KEY/_MODEL (default Groq),
      VKP_EVAL_FAITHFULNESS_MIN (default 0.6).
"""
import json
import os
import re
import sys
import urllib.request

EXPLORE_URL = os.getenv("VKP_EXPLORE_URL", "http://localhost:8090")
JUDGE_BASE = os.getenv("VKP_EVAL_LLM_BASE_URL", "https://api.groq.com/openai/v1")
JUDGE_KEY = os.getenv("VKP_EVAL_LLM_API_KEY") or os.getenv("GROQ_API_KEY", "")
JUDGE_MODEL = os.getenv("VKP_EVAL_LLM_MODEL", "llama-3.3-70b-versatile")
THRESHOLD = float(os.getenv("VKP_EVAL_FAITHFULNESS_MIN", "0.6"))

JUDGE_SYS = (
    "You are a strict RAG faithfulness judge. Given CONTEXT (retrieved sources) and an ANSWER, "
    "decompose the ANSWER into atomic factual claims and decide, for each, whether it is SUPPORTED "
    "by the context. Respond ONLY with JSON: "
    '{"claims":[{"claim":"...","supported":true|false}]}.'
)


def _search(query: str, company_id=None) -> dict:
    body = json.dumps({"query": query, "companyId": company_id, "providers": ["groq-70b"]}).encode()
    req = urllib.request.Request(EXPLORE_URL.rstrip("/") + "/api/vehicle-explore/langgraph/search",
                                 data=body, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def _faithfulness(answer: str, context: str) -> float:
    from openai import OpenAI
    client = OpenAI(api_key=JUDGE_KEY, base_url=JUDGE_BASE, timeout=40)
    r = client.chat.completions.create(
        model=JUDGE_MODEL, temperature=0, max_tokens=700,
        messages=[{"role": "system", "content": JUDGE_SYS},
                  {"role": "user", "content": f"CONTEXT:\n{context}\n\nANSWER:\n{answer}"}])
    raw = r.choices[0].message.content or ""
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    data = json.loads(m.group(0)) if m else {"claims": []}
    claims = data.get("claims", [])
    if not claims:
        return 0.0
    supported = sum(1 for c in claims if c.get("supported"))
    return round(supported / len(claims), 3)


def evaluate() -> dict:
    golden = json.load(open(os.path.join(os.path.dirname(__file__), "golden.json")))
    rows, scores = [], []
    for g in golden:
        res = _search(g["query"], g.get("companyId"))
        results = res.get("results", [])
        if not results:
            rows.append({"query": g["query"], "faithfulness": None, "note": "no results"})
            continue
        context = "\n".join(f"[{i + 1}] {r['snippet']}" for i, r in enumerate(results[:6]))
        score = _faithfulness(res.get("answer", ""), context)
        rows.append({"query": g["query"], "faithfulness": score})
        scores.append(score)
    mean = round(sum(scores) / len(scores), 3) if scores else 0.0
    return {"mean": mean, "threshold": THRESHOLD, "rows": rows, "passed": mean >= THRESHOLD}


def main() -> int:
    out = evaluate()
    for r in out["rows"]:
        print(f"  {r['query'][:44]:44} faithfulness={r.get('faithfulness')}{'  ('+r['note']+')' if r.get('note') else ''}")
    print(f"MEAN faithfulness: {out['mean']}  (threshold {out['threshold']}) -> {'PASS' if out['passed'] else 'FAIL'}")
    return 0 if out["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
