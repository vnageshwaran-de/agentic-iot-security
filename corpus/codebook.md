# Coding Codebook — PRISMA Corpus Extraction

This codebook defines the closed category set, decision rules, and tie-breaking
conventions used to code each included study in `extraction_matrix.csv`. It
documents the protocol summarised in Sections 3.4–3.5 and Section 5 of the
companion survey, so that the coding can be inspected and re-applied
independently.

## Coding procedure

Coding proceeded in two passes:

1. **First-author pass** — every included study was coded along all dimensions
   below, using only the closed categories defined here.
2. **Senior-author re-code** — a 15% random spot-check sample was independently
   re-coded to check agreement.

Two classes of disagreement were resolved separately:

- **Include/exclude disagreements** were resolved by discussion to consensus
  (binary inter-rater agreement: Cohen's κ = 0.84, 90.4% raw agreement on the
  spot-check sample).
- **Dimension-coding disagreements** on already-included papers were resolved by
  re-reading the primary study against the rule for that dimension. Where the
  primary study does not disclose a value, the dimension is coded **empty
  ("not reported")** rather than inferred — a conservative rule that prevents the
  synthesis from over-stating what the literature measured.

The `coding_source` column records, per row, the provenance of the coding:
`manuscript-explicit` for rows coded directly from an explicit statement in the
primary study / manuscript, and `author-verified` for rows that were initially
auto-drafted and have since been checked against the primary study and confirmed
or corrected by the author. All 153 rows are now in one of these two verified
states; no rows remain pending verification.

## Primary-function decision rules

Because the four taxonomy pillars are analytic projections of one system, a study
can touch several categories at once. Membership is therefore decided by the
**most consequential / primary** function, not by surface features:

1. **Architecture** is decided by the number of *independently-prompted* LLM
   control loops, not by the number of tools. One LLM that calls many tools is
   `single-agent`; a manager LLM that delegates to separately-prompted workers is
   `multi-agent` (hierarchical), even on one host.
2. **Action scope** is coded by the most consequential action the agent is
   *authorised* to take. A system that both classifies and opens a containment
   ticket is `response`, not `detection`.
3. **Reasoning strategy** is coded from the control loop the paper actually
   implements. Interleaved reason-and-act is `react`; a full plan committed before
   acting is `plan-and-solve`; neither is `none`/`cot`. An unnamed loop with a
   single mid-stream tool call is resolved in favour of `react` and flagged.
4. **Topology** is coded by where LLM inference physically executes. A hybrid
   edge-ML / cloud-LLM detector is coded `cloud` for its LLM component, with the
   hybrid character recorded under architecture.

## Column definitions (`extraction_matrix.csv`)

| Column | Closed categories / format |
|---|---|
| `study_id` | Internal id matching the manuscript reference number (e.g., `ref-1`). |
| `title`, `first_author`, `venue`, `year` | Study identifier (free text / integer). |
| `iot_domain` | `general IoT` \| `industrial IoT` \| `medical IoT` \| `vehicular IoT` \| `smart-grid IoT` \| `cross-cutting`. |
| `topology` | `edge` \| `fog` \| `cloud` \| `cross` \| empty (not reported). |
| `agent_architecture` | `single-agent` \| `multi-agent` \| `non-agentic-baseline`. |
| `reasoning_strategy` | `cot` \| `react` \| `plan-and-solve` \| `tool-use` \| `none` \| empty. |
| `cybersecurity_focus` | `detection` \| `response` \| `threat-hunting` \| `vulnerability-discovery` \| `deception` \| `authentication` \| `threat-intelligence`. |
| `benchmarks` | Dataset(s) and headline metric(s); free text; empty if none reported. |
| `critical_limitations` | Semicolon-separated subset of: `latency`; `hallucination`; `dataset-bias`; `adversarial-fragility`; `scalability`. |
| `compound_failure_mode` | `error-propagation` \| `tool-use-amplification` \| `context-poisoning` \| empty. Backs the 5-of-153 count (Section 8.2). |
| `reports_false_discovery_rate` | `yes` \| `no` (vulnerability-discovery studies only). Backs the 2-of-13 count (Section 5.3.4). |
| `coding_source` | `manuscript-explicit` \| `author-verified` (both are verified states; no rows remain pending). |

## Tie-breaking summary

- Multiple action scopes present → code the highest-blast-radius scope; record
  secondary scope only in the manuscript narrative, not as a second row (so counts
  do not double-count).
- Hybrid architecture → `single-agent` or `multi-agent` per the LLM-loop count
  rule above; "hybrid" is a narrative qualifier, not a separate code.
- Unnamed reasoning loop → `react` if any mid-stream tool call is shown,
  otherwise `none`.
- Any dimension not disclosed by the primary study → empty (not reported).
