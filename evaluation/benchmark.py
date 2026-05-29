"""End-to-end accuracy + latency harness for the single-agent ReAct loop.

Each row produces:
- a predicted attack family
- per-decision wall-clock latency

Outputs a JSON summary and a per-row CSV.

Usage
-----
    python evaluation/benchmark.py --rows 200 --model stub
"""
from __future__ import annotations
import argparse
import csv
import json
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core_loops.react_agent import run_react
from core_loops.utils import make_llm, StubLLMClient
from evaluation.datasets import load_rows
from evaluation.metrics import ClassificationReport, update, percentile


def heuristic_label(row) -> str:
    """When using --model stub, the LLM cannot reason, so we cheat with a heuristic that mirrors
    what an agentic detector might learn.  Useful for verifying the harness rather than the model."""
    if row.pkts_per_min > 1500:
        return "ddos"
    if row.avg_payload_entropy > 7.5:
        return "exfil" if row.pkts_per_min < 100 else "injection"
    if row.pkts_per_min > 120 and row.avg_payload_entropy < 5.5:
        return "brute-force"
    if row.pkts_per_min > 50 and row.peer_count >= 3:
        return "recon"
    if row.proto == "mqtt" and 4.0 <= row.avg_payload_entropy <= 6.0 and row.pkts_per_min > 25:
        return "mqtt-mitm"
    return "benign"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", type=int, default=200)
    ap.add_argument("--model", default="stub", choices=["stub", "openai", "anthropic"])
    ap.add_argument("--topology", default="edge", choices=["edge", "fog", "cloud"])
    ap.add_argument("--out-prefix", default="benchmark_run")
    args = ap.parse_args()

    report = ClassificationReport(total=0, correct=0, by_family_total={}, by_family_correct={})
    latencies: list[float] = []
    per_row_csv = pathlib.Path(f"{args.out_prefix}.csv")
    with per_row_csv.open("w", newline="") as csvf:
        writer = csv.writer(csvf)
        writer.writerow(["row_idx", "gold", "pred", "latency_s", "src_ip"])
        for i, row in enumerate(load_rows(args.rows)):
            t0 = time.time()
            if args.model == "stub":
                pred = heuristic_label(row)
            else:
                llm = make_llm(args.model)
                # Use anomaly_interpretation prompt; ask LLM to emit JSON {verdict, attack_family}.
                from core_loops.react_agent import PROMPT_DIR
                system = (PROMPT_DIR / "anomaly_interpretation.md").read_text()
                system = system.replace("{{topology}}", args.topology)
                system = system.replace("{{latency_budget_ms}}", "500")
                system = system.replace("{{device_classes}}", "sensors, gateways")
                result = run_react(llm, system, row.as_text())
                f = result["final"]
                pred = f.get("attack_family") or ("benign" if f.get("verdict") == "benign" else "ddos")
            elapsed = time.time() - t0
            latencies.append(elapsed)
            update(report, pred, row.label)
            writer.writerow([i, row.label, pred, f"{elapsed:.4f}", row.src_ip])

    summary = {
        "rows": report.total,
        "accuracy": round(report.accuracy, 4),
        "per_family_recall": {k: round(v, 4) for k, v in report.per_family_recall().items()},
        "latency_s": {
            "p50": round(percentile(latencies, 0.5), 4),
            "p95": round(percentile(latencies, 0.95), 4),
            "p99": round(percentile(latencies, 0.99), 4),
        },
        "topology": args.topology, "model": args.model,
    }
    pathlib.Path(f"{args.out_prefix}.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
