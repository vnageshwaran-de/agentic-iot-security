"""Synthetic Edge-IIoTset-style dataset loader.

The real Edge-IIoTset is not redistributed here.  This loader generates labeled flow rows
with the same column schema so the benchmark harness can run end-to-end out of the box.
Drop a real CSV at data/edge_iiotset.csv and the loader will use it instead.
"""
from __future__ import annotations
import csv
import pathlib
import random
from dataclasses import dataclass
from typing import Iterator

ROOT = pathlib.Path(__file__).resolve().parents[1]
REAL = ROOT / "data" / "edge_iiotset.csv"

ATTACK_FAMILIES = ["benign", "ddos", "recon", "injection", "exfil", "brute-force", "mqtt-mitm"]


@dataclass
class FlowRow:
    src_ip: str
    dst_ip: str
    dst_port: int
    proto: str
    pkts_per_min: int
    avg_payload_entropy: float
    peer_count: int
    label: str  # one of ATTACK_FAMILIES

    def as_text(self) -> str:
        return (
            f"Flow: src={self.src_ip} dst={self.dst_ip}:{self.dst_port}/{self.proto} "
            f"pkts/min={self.pkts_per_min} entropy={self.avg_payload_entropy:.2f} "
            f"peers={self.peer_count}"
        )

    def as_dict(self) -> dict:
        return {
            "src_ip": self.src_ip, "dst_ip": self.dst_ip, "dst_port": self.dst_port,
            "proto": self.proto, "pkts_per_min": self.pkts_per_min,
            "avg_payload_entropy": self.avg_payload_entropy, "peer_count": self.peer_count,
            "label": self.label,
        }


def _synth_row(rng: random.Random) -> FlowRow:
    label = rng.choices(ATTACK_FAMILIES, weights=[0.6, 0.08, 0.06, 0.06, 0.05, 0.08, 0.07])[0]
    base_proto = rng.choice(["mqtt", "coap", "http", "modbus"])
    if label == "benign":
        return FlowRow(
            src_ip=f"10.0.{rng.randint(0, 9)}.{rng.randint(2, 200)}",
            dst_ip="10.0.1.1", dst_port=1883 if base_proto == "mqtt" else 80,
            proto=base_proto, pkts_per_min=rng.randint(5, 50),
            avg_payload_entropy=rng.uniform(2.0, 5.5), peer_count=rng.randint(1, 3),
            label=label,
        )
    # Attacks: amplify one feature.
    base_pkts = 30
    entropy = 4.5
    if label == "ddos":
        base_pkts = rng.randint(2000, 8000); entropy = 1.5
    elif label == "recon":
        base_pkts = rng.randint(50, 200); entropy = rng.uniform(2.0, 4.0)
    elif label == "injection":
        entropy = rng.uniform(6.5, 7.95); base_pkts = rng.randint(40, 120)
    elif label == "exfil":
        entropy = rng.uniform(7.0, 7.9); base_pkts = rng.randint(20, 60)
    elif label == "brute-force":
        base_pkts = rng.randint(150, 800); entropy = rng.uniform(3.0, 5.0)
    elif label == "mqtt-mitm":
        base_pkts = rng.randint(30, 90); entropy = rng.uniform(4.0, 6.0)

    return FlowRow(
        src_ip=f"10.0.{rng.randint(0, 9)}.{rng.randint(2, 200)}",
        dst_ip="10.0.1.1", dst_port=1883 if base_proto == "mqtt" else 80,
        proto=base_proto, pkts_per_min=base_pkts,
        avg_payload_entropy=entropy, peer_count=rng.randint(1, 5),
        label=label,
    )


def load_rows(n: int, seed: int = 7) -> Iterator[FlowRow]:
    if REAL.exists():
        with REAL.open() as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if i >= n:
                    break
                yield FlowRow(
                    src_ip=row["src_ip"], dst_ip=row["dst_ip"], dst_port=int(row["dst_port"]),
                    proto=row["proto"], pkts_per_min=int(row["pkts_per_min"]),
                    avg_payload_entropy=float(row["avg_payload_entropy"]),
                    peer_count=int(row["peer_count"]), label=row["label"],
                )
        return
    rng = random.Random(seed)
    for _ in range(n):
        yield _synth_row(rng)
