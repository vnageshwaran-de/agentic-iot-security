# Sample Runs (v0.2.0)

This directory ships the deterministic offline-stub validation outputs cited
in Section 10.3 of the companion survey manuscript.

| File | Command | Notes |
|------|---------|-------|
| `benchmark_5k_stub.csv` / `.json` | `python evaluation/benchmark.py --rows 5000 --out-prefix evaluation/sample_runs/benchmark_5k_stub` | 5,000 synthetic Edge-IIoTset-style rows; `--model stub` (no API key required); seed fixed in `evaluation/datasets.py`. |
| `adversarial_25probes.json` | `python evaluation/adversarial.py --probes 25 --out evaluation/sample_runs/adversarial_25probes.json` | 25 prompt-injection probes (provenance in `../probes/PROVENANCE.md`); reports flip rate and pre-action detection rate. |

## Summary statistics (computed from `benchmark_5k_stub.csv`)

```
Binary attack-vs.-benign:    precision = 0.892, recall = 0.782, F1 = 0.833
7-way multi-class macro:     precision = 0.653, recall = 0.550, F1 = 0.544
Per-decision stub latency:   p50 = 0.12 us, p95 = 0.21 us (heuristic only; no LLM call)
```

These numbers are the *kit outputs* described in Section 10.3 of the manuscript
and should not be compared against the literature-derived rows of Table 5
(latency-frontier table), which reflect best-reported numbers from primary
studies on real datasets and real hardware.

## Re-running

```bash
python evaluation/benchmark.py --rows 5000 --out-prefix evaluation/sample_runs/benchmark_5k_stub
python evaluation/adversarial.py --probes 25 --out evaluation/sample_runs/adversarial_25probes.json
```

Both commands are deterministic under `--model stub`: re-running produces
byte-identical CSV / JSON output. To swap in a real model, add
`--model openai` or `--model anthropic` (requires `OPENAI_API_KEY` or
`ANTHROPIC_API_KEY` in the environment).
