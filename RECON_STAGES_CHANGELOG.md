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

## BLOCKER (discovered during the first E2E) — API budget exhausted
The victim agent returned HTTP 500 on every call: the gateway key (used by BOTH victim model and
attacker) is over budget:
  "Budget has been exceeded! Key=yuvic-fb7b1b95 (sk-...AUyw) Current cost: 1000.26, Max budget: 1000.0"
=> NO live run (recon or full experiment) can succeed until the budget is restored. The bar_port
pipeline itself is correct (discovery ran: "ToolChain # Discovering agent config..."); it just can't
call models. This is account-level; cannot be fixed here.

Status: stages implemented + unit-tested OFFLINE (no live recon_exp.json captured because of the
budget). Experiment is wired and ready (5 variants: bar_port, bar_s1_ground, bar_s2_reconcile,
bar_s3_afford, bar_all). When budget is restored, launch:
  cd /root/yuvi/agenteval-main
  set -a; . /root/yuvi/agenteval/.env; set +a; unset NIM_API_KEY
  export AGENT_EVAL_AGENTS_LAB=/root/yuvi/agents-lab-main
  uv run --no-project --with pyyaml python -m agent_eval.garak_chains.recon_exp2 run \
    -n 10 --stamp recon_cmp --scenarios codereview ecommerce identity \
    --variants bar_port bar_s1_ground bar_s2_reconcile bar_s3_afford bar_all \
    --concurrency 8 --attacker claude_opus46 --allow-stale-stacks
  # then: python -m agent_eval.garak_chains.recon_exp2 summarize <out> recon_cmp
Leftover idle containers from the aborted run: docker names matching 'cc-barport2-*' (safe to remove).
