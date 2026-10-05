#!/usr/bin/env python3
"""Verify the public RiNGSiDE TP4 performance supplement."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "performance.json"
EXPECTED_CONCURRENCY = [1, 2, 4, 6, 8, 12, 16]
EXPECTED_PROFILES = {"code", "prose-fr", "json", "mixed"}


def close(observed: float, expected: float, tolerance: float = 1e-6) -> None:
    if abs(observed - expected) > tolerance:
        raise SystemExit(f"value mismatch: {observed} != {expected}")


def main() -> int:
    document = json.loads(DATA.read_text(encoding="utf-8"))
    if document["schema"] != "glm53.ringside.performance.public.v1":
        raise SystemExit("unexpected performance schema")
    if any(document["privacy"].values()):
        raise SystemExit("performance privacy boundary flags are not clean")

    baseline = document["baseline_reproduction"]
    if len(baseline["cells"]) != 23:
        raise SystemExit("unexpected baseline reproduction cell count")
    if baseline["maximum_absolute_delta_percent"] >= 3.0:
        raise SystemExit("baseline reproduction drift exceeds the public threshold")

    decode = document["decode"]
    if (decode["cells"], decode["measured_requests"], len(decode["rows"])) != (24, 72, 24):
        raise SystemExit("unexpected decode matrix dimensions")
    decode_2048 = {row["content"]: row for row in decode["rows"] if row["budget_tokens"] == 2048}
    close(decode_2048["code"]["decode_tps"]["mean"], 99.6660907567773)
    close(decode_2048["reasoning"]["decode_tps"]["mean"], 78.41243774923699)

    prefill = document["cold_prefill"]
    if (prefill["measured_requests"], len(prefill["rows"])) != (21, 7):
        raise SystemExit("unexpected cold prefill dimensions")
    if not prefill["all_cold"] or any(row["cache_hit_rate"] for row in prefill["rows"]):
        raise SystemExit("cold prefill rows are not all cold")
    close(prefill["rows"][-1]["ttft_s"]["mean"], 54.233734028724335)

    cache = document["prefix_cache"]
    if (cache["requests"], len(cache["rows"])) != (105, 35):
        raise SystemExit("unexpected prefix cache dimensions")
    near_limit = [
        row for row in cache["rows"]
        if row["target_tokens"] == 260096 and row["condition"] == "shared-session"
    ][0]
    close(near_limit["cold_speedup"], 44.481211979553024)

    profiles = document["concurrency"]["profiles"]
    if set(profiles) != EXPECTED_PROFILES:
        raise SystemExit("unexpected concurrency profiles")
    for name, levels in profiles.items():
        if [row["concurrency"] for row in levels] != EXPECTED_CONCURRENCY:
            raise SystemExit(f"unexpected concurrency levels for {name}")
        if any(row["request_errors"] or row["quality_errors"] for row in levels):
            raise SystemExit(f"errors present in concurrency profile {name}")
    close(profiles["code"][-1]["aggregate_tps"], 439.75246554381135)

    soak = document["endurance_follow_up"]
    if (soak["duration_hours"], soak["requests"], soak["request_errors"], soak["transport_losses"]) != (2, 2550, 0, 0):
        raise SystemExit("unexpected endurance summary")

    print("ok  baseline reproduction: 23 cells, <3% maximum drift")
    print("ok  decode: 24 cells / 72 measured requests")
    print("ok  cold prefill: 7 sizes / 21 requests / zero cache hits")
    print("ok  prefix cache: 35 cells / 105 requests")
    print("ok  concurrency: C1-C16 across 4 profiles")
    print("ok  endurance: 2 h / 2,550 requests / zero errors")
    print("ok  public performance boundary")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
