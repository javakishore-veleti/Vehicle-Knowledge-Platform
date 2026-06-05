"""CI gate: mean faithfulness over the golden set must clear the threshold.

Skips (not fails) if the explore service isn't reachable, so unit CI stays green; run it in an
integration/nightly job with the services up. `pytest eval/` or `python -m eval.faithfulness`.
"""
import urllib.request

import pytest

from eval import faithfulness


def _explore_up() -> bool:
    try:
        with urllib.request.urlopen(faithfulness.EXPLORE_URL.rstrip("/") + "/health", timeout=3) as r:
            return r.status == 200
    except Exception:
        return False


@pytest.mark.skipif(not _explore_up(), reason="explore service not reachable")
def test_faithfulness_threshold():
    out = faithfulness.evaluate()
    assert out["mean"] >= out["threshold"], (
        f"mean faithfulness {out['mean']} < {out['threshold']}: {out['rows']}")
