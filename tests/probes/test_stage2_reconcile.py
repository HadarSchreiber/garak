"""Stage 2: the self-described deep-recon profile is grounded in observed behaviour."""
import re
from pathlib import Path

SRC = (Path(__file__).resolve().parents[2] / "garak" / "probes" / "agent_breaker.py").read_text()


def _grab(name):
    i = SRC.index(f"    def {name}(")
    m = re.search(r"\n    (@staticmethod|def )", SRC[i + 10:])
    block = SRC[i:i + 10 + m.start()]
    return "\n".join(l[4:] if l.startswith("    ") else l for l in block.splitlines())


_ns = {"re": re}
exec(_grab("_reconcile_profile"), _ns)
exec(_grab("_format_tool_profile"), _ns)
reconcile, render = _ns["_reconcile_profile"], _ns["_format_tool_profile"]


def test_observed_constraints_collected():
    profile = {"parameters": [{"name": "amount"}], "restrictions": ["rejects amounts over $1000"]}
    obs = [{"outcome": "success", "error_signature": "amount must be >= 0",
            "observed_constraints": ["amount accepted at $0.01 and $999999 (free parameter)"]}]
    rec = reconcile(profile, obs)
    assert rec["observed_constraints"] == [
        "amount must be >= 0", "amount accepted at $0.01 and $999999 (free parameter)"]


def test_render_distinguishes_self_reported_from_observed():
    out = render(reconcile({"restrictions": ["rejects amounts over $1000"]},
                           [{"refusal_signature": "I can't process a negative amount"}]))
    assert "self-reported" in out and "UNVERIFIED" in out and "rejects amounts over $1000" in out
    assert "OBSERVED during recon" in out and "negative amount" in out


def test_no_observations_marks_unverified_only():
    out = render(reconcile({"restrictions": ["admin only"]}, []))
    assert "UNVERIFIED" in out and "OBSERVED during recon" not in out


if __name__ == "__main__":
    import pytest, sys
    sys.exit(pytest.main([__file__, "-v"]))
