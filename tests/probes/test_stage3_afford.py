"""Stage 3: candidate free (unvalidated, caller-controlled) parameters - the exploitable surface."""
import re
from pathlib import Path

SRC = (Path(__file__).resolve().parents[2] / "garak" / "probes" / "agent_breaker.py").read_text()
i = SRC.index("    def _free_parameters(")
j = SRC.index("    def _profile_for_render(", i)
_ns = {"re": re}
exec("\n".join(l[4:] if l.startswith("    ") else l for l in SRC[i:j].splitlines()), _ns)
free = _ns["_free_parameters"]


def test_unvalidated_required_param_flagged():
    profile = {"parameters": [{"name": "amount", "required": True}, {"name": "order_id", "required": True}]}
    obs = [{"error_signature": "order_id not found"}]  # order_id IS validated; amount never pushed back on
    assert free(profile, obs) == ["amount"]


def test_validated_param_not_flagged():
    profile = {"parameters": [{"name": "quantity", "required": True}]}
    obs = [{"observed_constraints": ["quantity must be a positive integer"]}]
    assert free(profile, obs) == []


def test_no_observations_all_required_are_candidates():
    profile = {"parameters": [{"name": "resource", "required": True}, {"name": "note", "required": False}]}
    assert free(profile, []) == ["resource"]  # only required params are candidates


def test_novel_param_names_no_vocab():
    profile = {"parameters": [{"name": "widget_ref", "required": True}, {"name": "custodian", "required": True}]}
    obs = [{"error_signature": "custodian is not a known principal"}]
    assert free(profile, obs) == ["widget_ref"]  # structural, works on unseen names


if __name__ == "__main__":
    import pytest, sys
    sys.exit(pytest.main([__file__, "-v"]))
