#!/usr/bin/env python3
"""Verify the public dataset, headline aggregates, privacy boundary, and manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "results.json"
MANIFEST = ROOT / "MANIFEST.sha256"
EXPECTED = {
    "ringside-nvfp4-tp4": (79, 90, 72, 72, 7, 18, 69, 16, 24, 0, 6),
    "mia-exl3-stock-tp2": (85, 90, 72, 72, 13, 18, 56, 13, 24, 0, 6),
    "mia-exl3-ablit-r02-tp2": (85, 90, 72, 72, 13, 18, 69, 12, 24, 0, 6),
}
FOLLOW_UP_EXPECTED = {
    "m0-repeat-1": (31, 54, 53, 54),
    "m0-repeat-2": (29, 54, 54, 54),
    "target-kv-bf16": (25, 54, 52, 54),
    "greedy-verification-disabled": (25, 54, 50, 54),
    "kda-state-fp32": (26, 54, 54, 54),
}


def depth_summary(variant: dict) -> tuple[int, int, int, int, int, int]:
    rows = variant["depth"]["by_size"]
    total = sum(row["checks_correct"] for row in rows)
    possible = sum(row["checks_total"] for row in rows)
    retrieval = sum(row["retrieval_correct"] for row in rows)
    retrieval_possible = sum(row["retrieval_total"] for row in rows)
    return total, possible, retrieval, retrieval_possible, total - retrieval, possible - retrieval_possible


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def verify_manifest() -> None:
    entries = {}
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, relative = line.split("  ", 1)
        entries[relative] = digest
    for relative, expected in entries.items():
        actual = sha256(ROOT / relative)
        if actual != expected:
            raise SystemExit(f"manifest mismatch: {relative}")


def main() -> int:
    document = json.loads(DATA.read_text(encoding="utf-8"))
    if document["schema"] != "glm53.quality-ab.public.v2":
        raise SystemExit("unexpected schema")
    if document["pure_quantization_isolation"] is not False:
        raise SystemExit("comparability flag must remain false")

    if any(document["privacy"].values()):
        raise SystemExit("public data boundary flags are not clean")

    for variant in document["variants"]:
        common = variant["agentic_common"]
        long_track = variant["agentic_long"]
        observed = (
            *depth_summary(variant),
            variant["tool_eval"]["score_median"],
            common["outcomes"].get("success", 0),
            common["n_ticket_runs"],
            long_track["outcomes"].get("success", 0),
            long_track["n_ticket_runs"],
        )
        expected = EXPECTED.get(variant["id"])
        if observed != expected:
            raise SystemExit(f"aggregate mismatch for {variant['id']}: {observed} != {expected}")
        print(f"ok  {variant['id']}: {observed}")

    observed_follow_up = {}
    for row in document["follow_up"]["configurations"]:
        observed_follow_up[row["id"]] = (
            row["composite_gate_correct"],
            row["composite_gate_total"],
            row["retrieval_sentry_correct"],
            row["retrieval_sentry_total"],
        )
    if observed_follow_up != FOLLOW_UP_EXPECTED:
        raise SystemExit(f"follow-up mismatch: {observed_follow_up} != {FOLLOW_UP_EXPECTED}")
    soak = document["follow_up"]["soak"]
    if (soak["requests"], soak["request_errors"], soak["transport_losses"]) != (2550, 0, 0):
        raise SystemExit(f"unexpected soak summary: {soak}")
    print("ok  RiNGSiDE+ follow-up")

    verify_manifest()
    print("ok  manifest")
    print("ok  public data boundary")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
