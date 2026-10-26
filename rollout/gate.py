import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def decide(summaries, policy):
    """Return (allowed stage names, reasons it stopped).

    Every hard block applies to every stage and counts failures on BOTH eval sets.
    The pass rate that unlocks a stage comes from the held-out set only, because the
    tuning set is the one the aliases were written against.
    """
    reasons = []
    for bucket, limit in policy["hard_blocks"].items():
        seen = sum(s["buckets"].get(bucket, 0) for s in summaries.values())
        if seen > limit:
            reasons.append(f"{bucket}: {seen} (limit {limit})")
    if reasons:
        return [], reasons
    rate = summaries["holdout"]["pass_rate"]
    allowed = []
    for stage in policy["stages"]:
        if rate >= stage["min_holdout_pass"]:
            allowed.append(stage["name"])
        else:
            reasons.append(f"{stage['name']}: held-out pass rate {rate} is under {stage['min_holdout_pass']}")
            break
    return allowed, reasons


def main(root=ROOT):
    policy = json.loads((root / "rollout" / "rollout.json").read_text())
    out = root / "out"
    summaries = {
        "tuning": json.loads((out / "summary.json").read_text()),
        "holdout": json.loads((out / "holdout-summary.json").read_text()),
    }
    allowed, reasons = decide(summaries, policy)
    print("allowed stages:", ", ".join(allowed) or "none")
    for r in reasons:
        print("  stopped:", r)
    return 0 if allowed else 1


if __name__ == "__main__":
    sys.exit(main())
