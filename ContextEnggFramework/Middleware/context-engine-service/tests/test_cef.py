"""Unit tests for the Context Engineering Framework pipeline pieces — the Permission Layer scoping,
the Assembly Layer (the 5 strategies), and the in-process Memory fallback. No DB/LLM needed."""
import os

os.environ.setdefault("CEF_MEMORY_ENABLED", "false")  # exercise the in-process memory path

from app import assembly, memory, permission


def test_permission_scope_admin_vs_user():
    assert permission.scope({"role": "ADMIN", "companyId": "c1"})["companyBoundary"] is None
    user = permission.scope({"role": "USER", "companyId": "c1"})
    assert user["companyBoundary"] == "c1" and user["policy"] == "customer:company-scoped"


def test_assembly_dedupe_and_rank():
    chunks = [
        {"sourceUrl": "u1", "snippet": "low", "score": 0.1},
        {"sourceUrl": "u2", "snippet": "high", "score": 0.9},
        {"sourceUrl": "u1", "snippet": "low", "score": 0.1},  # duplicate
    ]
    ranked = assembly._dedupe_rank(chunks)
    assert len(ranked) == 2 and ranked[0]["sourceUrl"] == "u2"  # highest score first, deduped


def test_assembly_ordering_rules_first_task_last():
    block, used = assembly.assemble(
        "What MPG?", [{"sourceUrl": "u1", "snippet": "RAV4 44/38", "score": 0.8}],
        [], {"policy": "customer:company-scoped"}, "RULE-X")
    # Strategy 3: RULES before TASK; Strategy 5: structured markdown sections
    assert block.index("## RULES") < block.index("## TASK")
    assert "RULE-X" in block and block.rstrip().endswith("What MPG?")
    assert len(used) == 1


def test_assembly_compression_summarises_old_turns():
    turns = [{"role": "user", "text": f"q{i}"} for i in range(8)]
    out = assembly._compress(turns, keep=4)
    assert out[0]["role"] == "summary" and len(out) == 5  # 1 summary + 4 recent


def test_memory_in_process_roundtrip():
    memory.append_turn("sX", "user", "hello")
    memory.append_turn("sX", "assistant", "hi")
    turns = memory.recent_turns("sX")
    assert [t["role"] for t in turns][-2:] == ["user", "assistant"]
    assert memory.recent_turns(None) == []
