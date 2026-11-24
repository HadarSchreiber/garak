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

## Stage 2 — ground profiles in observed behaviour
Deep-recon profiles are the agent describing ITSELF (restrictions can be wishful/hallucinated).
`_reconcile_profile(profile, observations)` collects the concrete signals the target actually
surfaced (refusal/error signatures, observed_constraints) into `observed_constraints`; the renderer
now marks the profile's own restrictions "self-reported - UNVERIFIED" and the observed ones
"OBSERVED during recon (what the live target actually did)". Data-driven from the observation fields,
no vocabulary. Test: tests/probes/test_stage2_reconcile.py (3 pass).

## Stage gating (for experiment variations)
Each improvement is env-gated via `_stage_enabled("<NAME>")` reading AB_STAGE_<NAME> (default off), so
the recon_exp2 harness can A/B each stage as its own variant (bar_port baseline vs +stage) with one
probe and no code fork. Stage 1 = AB_STAGE_GROUND; Stage 2 = AB_STAGE_RECONCILE.

## Stage 3 — free-parameter / affordance detection (AB_STAGE_AFFORD)
`_free_parameters(profile, observations)`: a required parameter the recon never saw validated (no
refusal/error/constraint text references it) is a CANDIDATE free (caller-controlled, server-unvalidated)
parameter - the exploitable surface (an amount decoupled from a total, an id whose ownership is never
checked). Surfaced in the profile render. Structural (tool's own param names + its own observed signals),
no vocabulary. _profile_for_render() composes reconcile (S2) + affordance (S3). Test:
tests/probes/test_stage3_afford.py (4 pass; works on unseen param names).
