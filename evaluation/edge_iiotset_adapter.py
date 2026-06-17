"""Adapter: official Edge-IIoTset (Ferrag et al., 2022) -> kit loader schema.

The kit's evaluation loader (`evaluation/datasets.py`) expects an 8-column CSV with
engineered *flow* features:

    src_ip, dst_ip, dst_port, proto, pkts_per_min, avg_payload_entropy, peer_count, label

The official Edge-IIoTset release ships *packet-level* CSVs with ~63 Wireshark
fields and an `Attack_type` label.  This adapter converts the raw per-attack and
normal-traffic CSVs into the kit schema so that the manuscript's Section 10.3
*Step (i)* validation (re-run the shipped benchmark on real data; report the delta
against the synthetic generator) can be executed.

Honest mapping notes
--------------------
* `src_ip`, `dst_ip`, `dst_port`, `proto`  -> derived from real raw fields.
* `pkts_per_min`, `peer_count`             -> derived for real by aggregating
  packets into flows keyed by (src, dst, proto, dst_port).
* `avg_payload_entropy`                     -> NOT RECOVERABLE: every payload
  field (`tcp.payload`, `mqtt.msg`, `http.file_data`) is zeroed in the public
  release.  It is set to a documented neutral constant (ENTROPY_DEFAULT).  This
  deactivates the entropy-dependent branches of the kit's stub heuristic and is
  the single largest contributor to the synthetic-to-real gap reported by Step (i).

Usage
-----
    python evaluation/edge_iiotset_adapter.py \
        --archive "data/archive/Edge-IIoTset dataset" \
        --per-class 2500 --out data/edge_iiotset.csv
"""
from __future__ import annotations
import argparse
import csv
import glob
import math
import os
import pathlib
import random
import re
from collections import defaultdict

ENTROPY_DEFAULT = 5.0  # payloads are stripped in the public release; see module docstring.

# Edge-IIoTset Attack_type  ->  kit family (7 classes used by datasets.py)
LABEL_MAP = {
    "Normal": "benign",
    "DDoS_UDP": "ddos", "DDoS_ICMP": "ddos", "DDoS_TCP": "ddos", "DDoS_HTTP": "ddos",
    "Port_Scanning": "recon", "Vulnerability_scanner": "recon",
    "Fingerprinting": "recon", "OS_Fingerprinting": "recon",
    "SQL_injection": "injection", "XSS": "injection", "Uploading": "injection",
    "Password": "brute-force",
    "Backdoor": "exfil", "Ransomware": "exfil",
    "MITM": "mqtt-mitm",
}

TIME_RE = re.compile(r"(\d{2}):(\d{2}):(\d{2}\.\d+)")


def _f(x: str) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


def _secs(frame_time: str) -> float | None:
    """Best-effort seconds-of-day from an Edge-IIoTset frame.time string."""
    m = TIME_RE.search(frame_time or "")
    if not m:
        return None
    h, mnt, s = m.groups()
    return int(h) * 3600 + int(mnt) * 60 + float(s)


def _proto(row: dict) -> str:
    if _f(row.get("mqtt.len")) or _f(row.get("mqtt.topic_len")) or str(row.get("mqtt.protoname", "0")) not in ("0", "0.0", ""):
        return "mqtt"
    if _f(row.get("mbtcp.len")) or _f(row.get("mbtcp.trans_id")):
        return "modbus"
    if str(row.get("http.request.method", "0")) not in ("0", "0.0", "") or _f(row.get("http.content_length")):
        return "http"
    if _f(row.get("udp.port")):
        return "coap"
    return "http"  # default for TCP/web traffic


def _port(row: dict) -> int:
    for k in ("tcp.dstport", "udp.port"):
        v = _f(row.get(k))
        if v:
            return int(v)
    return 0


def iter_rows(path: str, cap: int, rng: random.Random):
    """Reservoir-free streaming sample: take the first `cap` usable rows."""
    n = 0
    with open(path, newline="", errors="replace") as f:
        r = csv.DictReader(f)
        for row in r:
            src = str(row.get("ip.src_host", "")).strip()
            if not src or src in ("0", "0.0"):
                continue
            yield row
            n += 1
            if n >= cap:
                return


def build(archive: str, per_class: int, out: str, seed: int = 7) -> dict:
    rng = random.Random(seed)
    attack_dir = os.path.join(archive, "Attack traffic")
    normal_dir = os.path.join(archive, "Normal traffic")

    # Collect a per-class sample of raw packets.
    packets = []  # list of (src, dst, proto, port, secs, kit_label)
    sources = sorted(glob.glob(os.path.join(attack_dir, "*.csv")))
    # one representative normal file (smallest available) to supply benign traffic
    normal_files = sorted(glob.glob(os.path.join(normal_dir, "**", "*.csv"), recursive=True),
                          key=os.path.getsize)
    if normal_files:
        sources.append(normal_files[0])

    per_label_taken = defaultdict(int)
    for path in sources:
        for row in iter_rows(path, cap=per_class * 4, rng=rng):
            atype = str(row.get("Attack_type", "")).strip()
            kit = LABEL_MAP.get(atype)
            if kit is None:
                continue
            if per_label_taken[kit] >= per_class:
                continue
            src = str(row["ip.src_host"]).strip()
            dst = str(row.get("ip.dst_host", "")).strip() or "10.0.0.1"
            if dst in ("0", "0.0"):
                dst = "10.0.0.1"
            packets.append((src, dst, _proto(row), _port(row), _secs(row.get("frame.time", "")), kit))
            per_label_taken[kit] += 1

    # Aggregate packets into flows keyed by (src, dst, proto, port).
    flows = defaultdict(list)
    peers = defaultdict(set)
    for src, dst, proto, port, secs, kit in packets:
        flows[(src, dst, proto, port)].append((secs, kit))
        peers[src].add(dst)

    rows_out = []
    for (src, dst, proto, port), members in flows.items():
        times = [t for t, _ in members if t is not None]
        count = len(members)
        if len(times) >= 2 and (max(times) - min(times)) > 0:
            span_min = (max(times) - min(times)) / 60.0
            ppm = count / max(span_min, 1e-3)
        else:
            ppm = float(count)  # intensity proxy when timestamps are unusable
        # majority label of the flow
        labs = [k for _, k in members]
        label = max(set(labs), key=labs.count)
        rows_out.append({
            "src_ip": src, "dst_ip": dst, "dst_port": int(port), "proto": proto,
            "pkts_per_min": int(round(ppm)),
            "avg_payload_entropy": ENTROPY_DEFAULT,
            "peer_count": len(peers[src]),
            "label": label,
        })

    rng.shuffle(rows_out)
    out_path = pathlib.Path(out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["src_ip", "dst_ip", "dst_port", "proto",
                                          "pkts_per_min", "avg_payload_entropy",
                                          "peer_count", "label"])
        w.writeheader()
        w.writerows(rows_out)

    dist = defaultdict(int)
    for r in rows_out:
        dist[r["label"]] += 1
    return {"packets": len(packets), "flows": len(rows_out), "by_label": dict(dist), "out": str(out_path)}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--archive", default="data/archive/Edge-IIoTset dataset")
    ap.add_argument("--per-class", type=int, default=2500)
    ap.add_argument("--out", default="data/edge_iiotset.csv")
    a = ap.parse_args()
    summary = build(a.archive, a.per_class, a.out)
    print(summary)
