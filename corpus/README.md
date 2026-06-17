# PRISMA Corpus Materials

This directory ships the systematic-review materials that the companion survey
manuscript (Sections 3.4, 3.5, and 10) states are released alongside the kit,
so that any reader can replicate the corpus selection and verify the
quantitative claims derived from the coded extraction matrix.

| File | Contents |
|---|---|
| `extraction_matrix.csv` | The full coded matrix: one row per included study (n = 153), coded along the seven dimensions of the extraction schema (manuscript Section 3.5). |
| `search_strategy.md` | Search strings, venue list, date window, inclusion/exclusion criteria, and exclusion rationale (manuscript Sections 3.2–3.4). |
| `codebook.md` | Closed category definitions, primary-function decision rules, and tie-breaking conventions used to code the matrix (manuscript Sections 3.4–3.5 and 5). |

## Columns of `extraction_matrix.csv`

1. `study_id` — internal identifier matching the manuscript reference number (e.g., `ref-1`).
2. `title`, `first_author`, `venue`, `year` — study identifier.
3. `iot_layer` — perception | network | application; `topology` — edge | fog | cloud | cross.
4. `agent_architecture` — single-agent | multi-agent | non-agentic-baseline.
5. `reasoning_strategy` — cot | react | plan-and-solve | tool-use | none.
6. `cybersecurity_focus` — detection | response | threat-hunting | vulnerability-discovery | deception | authentication | threat-intelligence.
7. `benchmarks` — dataset(s) and headline metric(s) used.
8. `critical_limitations` — latency | hallucination | dataset-bias | adversarial-fragility | scalability (semicolon-separated).
9. `compound_failure_mode` — one of `error-propagation`, `tool-use-amplification`,
   `context-poisoning`, or empty. Used to derive the prevalence count reported
   in Section 8.2 of the revised manuscript (5 of 153 studies).
10. `reports_false_discovery_rate` — `yes`/`no`; applies to vulnerability-discovery
    studies only. Used to derive the 2-of-13 reporting-gap count in Section 5.3.4
    of the revised manuscript.

## Status

All 153 corpus rows are present and verified. The `coding_source` column records
provenance: `manuscript-explicit` (n = 41) for rows coded directly from explicit
statements in the primary study / manuscript, and `author-verified` (n = 112) for
rows that were initially auto-drafted by keyword analysis and have since been
checked against the primary study and confirmed or corrected by the author. No
rows remain pending verification. Counts backing the manuscript's quantified
claims: compound failure modes = 5 of 153 (Section 8.2); false-discovery-rate
reporting = 2 of 13 vulnerability-discovery studies (Section 5.3.4).
