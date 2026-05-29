# Agentic IoT Security Lab

Companion code artifact for the survey **"Agentic AI and Large Language Models for Autonomous IoT Cybersecurity: A Systematic Survey, Taxonomy, and Research Roadmap"**.

This repository operationalises the four-pillar taxonomy from Section 5 of the manuscript by providing:

- **`/prompts`** — reusable system-prompt templates and JSON tool schemas for each action scope (anomaly interpretation, response orchestration, threat hunting, vulnerability discovery, deception).
- **`/core_loops`** — minimal, reproducible Python reference implementations of a single-agent ReAct loop and three multi-agent coordination patterns (pipeline, debate, blackboard).
- **`/evaluation`** — benchmark harness that runs an agent against Edge-IIoTset-style traffic, recording detection accuracy and end-to-end latency, plus an adversarial harness that injects prompt-injection probes.
- **`/data`** — placeholder for downloaded datasets (not redistributed).

> The repository is intended as scaffolding: every file is fully runnable, but is deliberately kept under ~150 lines per module so it can be adapted in a single afternoon.

---

## Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Run the single-agent ReAct loop against a stub LLM and stub tools.
python core_loops/react_agent.py --model stub

# Run the three multi-agent patterns.
python core_loops/multi_agent.py --pattern pipeline
python core_loops/multi_agent.py --pattern debate
python core_loops/multi_agent.py --pattern blackboard

# Run the evaluation harness on synthetic Edge-IIoTset rows.
python evaluation/benchmark.py --rows 200

# Run the adversarial prompt-injection harness.
python evaluation/adversarial.py --probes 25
```

The default `--model stub` backend implements deterministic responses so the harness runs offline. To target a real LLM, set `--model openai|anthropic|llamacpp` and the corresponding API key/path.

## Project layout

```
.
├── README.md
├── requirements.txt
├── prompts/
│   ├── anomaly_interpretation.md
│   ├── response_orchestration.md
│   ├── threat_hunting.md
│   ├── vulnerability_discovery.md
│   ├── deception.md
│   └── tool_schemas.json
├── core_loops/
│   ├── react_agent.py
│   ├── multi_agent.py
│   └── utils.py
├── evaluation/
│   ├── benchmark.py
│   ├── adversarial.py
│   ├── metrics.py
│   └── datasets.py
└── data/.gitkeep
```

## Mapping to the manuscript taxonomy

| Taxonomy dimension | Where in this repo |
|---|---|
| Pillar I — Agent architecture | `core_loops/react_agent.py`, `core_loops/multi_agent.py` |
| Pillar II — Reasoning strategy | ReAct loop in `react_agent.py`; reflection helpers in `utils.py` |
| Pillar III — Action scope | `prompts/*.md`, `prompts/tool_schemas.json` |
| Pillar IV — Deployment topology | `--topology edge\|fog\|cloud` flag toggles model size and tool-set in `benchmark.py` |

## License

MIT. See `LICENSE`.

## Citation

If you build on this repository, please cite the companion survey (full BibTeX entry in the manuscript references).
