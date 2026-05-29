"""Single-agent ReAct reasoning loop for IoT security tasks.

Pillar I  : single-agent
Pillar II : ReAct (thought → action → observation → ... → answer)
Pillar III: any action scope (system prompt is parameterised)
Pillar IV : --topology selects the LLM size class

Usage
-----
    python core_loops/react_agent.py --model stub --scope anomaly_interpretation
"""
from __future__ import annotations
import argparse
import json
import pathlib
import sys
import time
from typing import Callable

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core_loops.utils import (
    LLMClient, make_llm, Trace, looks_like_injection, confidence_gate,
)

PROMPT_DIR = ROOT / "prompts"
MAX_STEPS = 8


# ---------------------------------------------------------------------------- stub tool registry
def tool_siem_query(args: dict) -> dict:
    return {"hits": [{"src_ip": "10.0.5.7", "dst_port": 1883, "count": 4421, "label": "mqtt-burst"}]}

def tool_attack_lookup(args: dict) -> dict:
    return {"technique_id": args.get("technique_id", "T0000"), "description": "Stub description"}

def tool_device_inventory(args: dict) -> dict:
    return {"device_id": args.get("identifier"), "tier": 3, "class": "sensor"}

def tool_pcap_sandbox(args: dict) -> dict:
    return {"packets": 142, "anomalies": ["repeated 0xCAFE marker"]}

def tool_cti_feed(args: dict) -> dict:
    return {"indicator": args.get("indicator"), "matches": 0}

TOOLS: dict[str, Callable[[dict], dict]] = {
    "siem_query": tool_siem_query,
    "attack_lookup": tool_attack_lookup,
    "device_inventory": tool_device_inventory,
    "pcap_sandbox": tool_pcap_sandbox,
    "cti_feed": tool_cti_feed,
}


# ---------------------------------------------------------------------------- ReAct loop
def parse_action(raw: str) -> tuple[str | None, dict | None, str | None]:
    """Extract either {tool, args} or {answer} from an LLM reply.  Tolerant of fenced JSON."""
    text = raw.strip()
    # Strip code fences if present.
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json\n"):
            text = text[5:]
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        return None, None, None
    if "answer" in obj:
        return None, None, json.dumps(obj["answer"])
    if "action" in obj:
        a = obj["action"]
        return a.get("tool"), a.get("args", {}), None
    if "tool" in obj:
        return obj["tool"], obj.get("args", {}), None
    return None, None, None


def run_react(llm: LLMClient, system_prompt: str, user_task: str) -> dict:
    trace = Trace()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_task},
    ]
    started = time.time()

    for step in range(1, MAX_STEPS + 1):
        reply = llm.complete(messages, temperature=0.2)
        trace.add("thought", reply)

        tool, args, final = parse_action(reply)
        if final:
            trace.add("answer", final)
            return {
                "run_id": trace.run_id,
                "steps": step,
                "elapsed_s": round(time.time() - started, 3),
                "final": json.loads(final),
                "trace": trace.to_jsonl(),
            }
        if tool is None:
            messages.append({"role": "assistant", "content": reply})
            messages.append({"role": "user", "content": "Please respond with strict JSON: {action: {tool, args}} or {answer: ...}."})
            continue

        if tool not in TOOLS:
            obs = {"error": f"unknown tool: {tool}"}
        else:
            obs = TOOLS[tool](args or {})
            # Defensive: inspect observation for injection markers before passing back to the LLM.
            if looks_like_injection(json.dumps(obs)):
                obs["__warning__"] = "indirect_prompt_injection_suspected"
        trace.add("tool_call", {"tool": tool, "args": args})
        trace.add("observation", obs)
        messages.append({"role": "assistant", "content": reply})
        messages.append({"role": "user", "content": f"observation: {json.dumps(obs)}"})

    return {
        "run_id": trace.run_id,
        "steps": MAX_STEPS,
        "elapsed_s": round(time.time() - started, 3),
        "final": {"verdict": "inconclusive", "confidence": 0.0, "reason": "max_steps_reached"},
        "trace": trace.to_jsonl(),
    }


# ---------------------------------------------------------------------------- CLI
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="stub", choices=["stub", "openai", "anthropic"])
    ap.add_argument("--scope", default="anomaly_interpretation",
                    choices=["anomaly_interpretation", "response_orchestration",
                             "threat_hunting", "vulnerability_discovery", "deception"])
    ap.add_argument("--topology", default="edge", choices=["edge", "fog", "cloud"])
    ap.add_argument("--task", default=(
        "Flow record: src=10.0.5.7, dst=mqtt-broker.local:1883, packets=4421/min, "
        "payload entropy=7.9, peer count=1. Decide whether this is benign, attack, or novel."
    ))
    args = ap.parse_args()

    sys_prompt_path = PROMPT_DIR / f"{args.scope}.md"
    system = sys_prompt_path.read_text().replace("{{topology}}", args.topology)
    system = system.replace("{{latency_budget_ms}}", {"edge": "200", "fog": "500", "cloud": "2000"}[args.topology])
    system = system.replace("{{device_classes}}", "sensors, gateways, MQTT brokers, IPCams")

    llm = make_llm(args.model)
    result = run_react(llm, system, args.task)
    print(json.dumps({k: v for k, v in result.items() if k != "trace"}, indent=2))


if __name__ == "__main__":
    main()
