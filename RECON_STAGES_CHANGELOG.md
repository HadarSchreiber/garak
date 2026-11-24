# Probe-improvement stages (branch tool-chain-recon-from-bar) — autonomous session

Method: measurement-first, one change per stage, each gated on an offline metric; reuse captured
recon data as fixtures (no re-run per stage); NO overfit constants (structural / value-morphology
only — never lab-specific field names, ids, or tool names).

Baseline: Bar deep-recon + behavioural baseline ported onto main (commits 2d0b75dd, 4c7e146b, ec4d8be2).
Stage 0 yardstick: scripts/score_recon_quality.py (cac77a57).

## Live baseline (bar_port E2E, stamp barport2) — pending (images building); score when it lands.

## Stage 1 — recon anti-fabrication (grounded identifiers)
The behavioural probe banks the agent's confabulated ids (write-tool replies invent #4821/jthompson42).
Added `_grounded_identifiers()`: real ids taken ONLY from observations that RETURNED A COLLECTION
(a listing/record carries real ids; a single side-effect confirmation invents one). "Collection" is
judged structurally (output_shape names a collection, or the sample carries >=2 id tokens) + value
morphology for ids (`_id_tokens`) - NO field/tool/value vocabulary. Surfaced in rendered_for_attacker
("REAL IDENTIFIERS OBSERVED") and the dump (`grounded_identifiers`) so the attacker reuses real values.
Test: tests/probes/test_stage1_grounded.py (4 pass) - collection-only, single-confirmation excluded,
novel-domain (no vocab), emails grounded / free-text names dropped.
