"""Three reference multi-agent coordination patterns described in Section 5.1.2 of the survey.

Patterns
--------
- pipeline  : scanner → analyst → responder (directed-acyclic chain)
- debate    : two analysts argue; a judge agent resolves
- blackboard: agents read/write a shared state dict until a goal predicate fires

All three patterns share the same Agent abstraction.
"""
from __future__ import annotations
import argparse
import json
import pathlib
import sys
import time
from dataclasses import dataclass, field
from typing import Callable

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from core_loops.utils import LLMClient, make_llm, Trace, looks_like_injection


@dataclass
class Agent:
    name: str
    system_prompt: str
    llm: LLMClient
    role: str = "generic"

    def step(self, user_text: str) -> str:
        return self.llm.complete([
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_text},
        ])


# ---------------------------------------------------------------------------- pipeline
def pipeline(llm: LLMClient, observation: str) -> dict:
    scanner = Agent("scanner", "You are a network scanner agent. Summarise the observation in one line.", llm, "scan")
    analyst = Agent("analyst", "You are an analyst agent. Decide benign/attack/novel from the scanner summary.", llm, "analyse")
    responder = Agent("responder", "You are a responder agent. Choose a response action (log/rate_limit/block).", llm, "respond")

    trace = Trace()
    s1 = scanner.step(observation); trace.add("pipeline.scanner", s1)
    s2 = analyst.step(s1);          trace.add("pipeline.analyst", s2)
    s3 = responder.step(s2);        trace.add("pipeline.responder", s3)
    return {"pattern": "pipeline", "result": s3, "trace": trace.to_jsonl()}


# ---------------------------------------------------------------------------- debate
def debate(llm: LLMClient, observation: str) -> dict:
    pro = Agent("pro", "You argue the observation IS an attack. State your single strongest reason.", llm, "pro")
    con = Agent("con", "You argue the observation is BENIGN. State your single strongest reason.", llm, "con")
    judge = Agent("judge", "You are a neutral judge. Given the two arguments, emit a JSON {verdict, confidence}.", llm, "judge")

    trace = Trace()
    p = pro.step(observation); trace.add("debate.pro", p)
    c = con.step(observation); trace.add("debate.con", c)
    verdict = judge.step(f"PRO: {p}\nCON: {c}\nObservation: {observation}")
    trace.add("debate.judge", verdict)
    return {"pattern": "debate", "result": verdict, "trace": trace.to_jsonl()}


# ---------------------------------------------------------------------------- blackboard
def blackboard(llm: LLMClient, observation: str) -> dict:
    bb: dict = {"observation": observation, "facts": [], "goal_met": False}
    trace = Trace()

    sensor = Agent("sensor", "Extract concrete facts (k:v) from the observation. Return JSON list.", llm, "sensor")
    enricher = Agent("enricher", "Given facts, add 1 inferred fact about likely attack family. Return JSON list.", llm, "enricher")
    closer = Agent("closer", "Given all facts, decide if goal=produce-verdict is met. Return JSON {verdict, confidence, goal_met}.", llm, "closer")

    bb["facts"].append({"sensor": sensor.step(json.dumps(bb))})
    trace.add("bb.sensor", bb["facts"][-1])
    bb["facts"].append({"enricher": enricher.step(json.dumps(bb))})
    trace.add("bb.enricher", bb["facts"][-1])
    closer_out = closer.step(json.dumps(bb))
    trace.add("bb.closer", closer_out)
    bb["closer"] = closer_out
    return {"pattern": "blackboard", "result": closer_out, "trace": trace.to_jsonl(), "blackboard": bb}


# ---------------------------------------------------------------------------- main
PATTERNS: dict[str, Callable[[LLMClient, str], dict]] = {
    "pipeline": pipeline, "debate": debate, "blackboard": blackboard,
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="stub", choices=["stub", "openai", "anthropic"])
    ap.add_argument("--pattern", default="pipeline", choices=list(PATTERNS))
    ap.add_argument("--observation", default=(
        "Device 10.0.5.7 (sensor tier=3) is publishing to mqtt-broker.local at 4421 pkts/min, "
        "entropy=7.9, with a single peer.  Baseline avg=15 pkts/min."
    ))
    args = ap.parse_args()
    llm = make_llm(args.model)
    out = PATTERNS[args.pattern](llm, args.observation)
    print(json.dumps({k: v for k, v in out.items() if k != "trace"}, indent=2))


if __name__ == "__main__":
    main()

from core_loops.multi_agent.sanitize import sanitize_handoff, SyntacticFilter, SemanticFrame  # noqa: E402
