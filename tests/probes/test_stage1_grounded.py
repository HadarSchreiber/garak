"""Stage 1: grounded-identifier extraction is structural (no vocabulary) and anti-fabrication.

Extracts the Stage-1 helpers from the probe source in isolation (no garak install) and asserts:
grounded ids come ONLY from collection-returning observations (real listings), a single write-tool
confirmation's invented id is excluded, and detection does not depend on any field/tool vocabulary.
"""
import re
from pathlib import Path

SRC = (Path(__file__).resolve().parents[2] / "garak" / "probes" / "agent_breaker.py").read_text()
_block = SRC[SRC.index("    # --- Stage 1: recon anti-fabrication"): SRC.index("    def _perform_recon_probes(")]
_ns = {"re": re}
exec("class _T:\n" + _block, _ns)  # keeps the 4-space class-body indent
T = _ns["_T"]


def _obj(behaviors):
    o = T()
    o.tool_behaviors = behaviors
    return o


def test_collection_ids_grounded_single_confirmation_excluded():
    beh = {
        # a read tool that returned a listing -> >=2 ids -> trusted
        "functions.search_catalog": [{"outcome": "success",
            "output_sample": "P-100 Trailframe, P-200 Tent, P-300 Headlamp"}],
        # a write tool that confirmed one action -> single invented id -> excluded
        "functions.place_order": [{"outcome": "success", "output_sample": "order PRD-40221 placed"}],
    }
    got = _obj(beh)._grounded_identifiers()
    assert set(got) == {"P-100", "P-200", "P-300"}
    assert "PRD-40221" not in got


def test_collection_by_output_shape():
    beh = {"functions.list_group_members": [{"output_shape": "list[dict]",
            "output_sample": "one member: alice-01"}]}  # 1 id but shape says collection
    assert _obj(beh)._grounded_identifiers() == ["alice-01"]


def test_no_vocabulary_dependence():
    # fields/tools renamed to a novel domain; a listing of ids must still be grounded structurally
    beh = {"enumerate_widgets": [{"output_shape": "array", "output_sample": "WID-900, WID-901, WID-902"}]}
    assert set(_obj(beh)._grounded_identifiers()) == {"WID-900", "WID-901", "WID-902"}


def test_emails_grounded_free_text_excluded():
    beh = {"get_contacts": [{"output_shape": "list",
            "output_sample": "Maria Santos <maria@acme.example>, John Roe <john@acme.example>"}]}
    got = _obj(beh)._grounded_identifiers()
    assert set(got) == {"maria@acme.example", "john@acme.example"}  # names (free text) not captured


if __name__ == "__main__":
    import pytest, sys
    sys.exit(pytest.main([__file__, "-v"]))
