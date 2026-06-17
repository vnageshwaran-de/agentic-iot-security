# Changelog

All notable changes to the Agentic IoT Security Lab companion kit.
The Zenodo concept DOI `10.5281/zenodo.20438072` always resolves to the latest version.

## [0.3.0] - 2026-06-17

Second-revision (R2) release accompanying the revised *Electronics* manuscript.

### Added
- `evaluation/edge_iiotset_adapter.py` — adapter mapping the official Edge-IIoTset
  packet-level CSVs into the harness's 8-column loader schema, enabling the
  manuscript's Section 10.3 **Step (i)** real-data validation.
- `evaluation/sample_runs/edge_iiotset_real_step_i.{json,csv}` — Step (i) run on
  real Edge-IIoTset (2,481 flows). Reported as a **negative control**: stub-harness
  accuracy = 0.062 (real) vs 0.783 (synthetic), quantifying the synthetic-to-real
  gap. Payload entropy is unavailable in the public release (all payload fields
  zeroed), which deactivates the entropy-dependent heuristic branches. Not a
  detection claim.
- `corpus/codebook.md` — closed category definitions, primary-function decision
  rules, and tie-breaking conventions for the coded extraction matrix.

### Changed
- `corpus/extraction_matrix.csv` — all rows verified: `coding_source` is now
  `manuscript-explicit` (41) or `author-verified` (112); no rows remain pending.
  Three rows re-tagged to their correct primary `cybersecurity_focus`
  (`ref-126` → detection, `ref-97` → threat-intelligence, `ref-99` →
  threat-intelligence). Headline counts unchanged and verified: compound failure
  modes = 5/153 (§8.2); false-discovery-rate reporting = 2/13 FDR-assessed
  vulnerability-discovery studies (§5.3.4).
- `corpus/README.md`, `evaluation/sample_runs/README.md` — documentation updated
  for the above.

## [0.2.1] - 2026 (manuscript Round-1 revision)
- Added `corpus/` PRISMA materials (extraction matrix, search strategy).
- 25-pattern prompt-injection probe corpus with provenance map.
- Two-stage inter-agent input sanitization (`core_loops/multi_agent/sanitize.py`).
- Deterministic stub-mode sample runs.
