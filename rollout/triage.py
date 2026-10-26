import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEVERITY = ["missed_escalation", "bad_citation", "made_up_answer",
            "false_escalation", "retrieval_miss", "false_refusal", "wrong_sentence"]
NEXT_MOVE = {
    "missed_escalation": "add the wording to rollout/guards.py and a test that it fires",
    "bad_citation": "stop shipping the answer; fix the composer, never the checker",
    "made_up_answer": "raise MIN_SCORE in rollout/agent.py or add an out-of-scope ticket",
    "false_escalation": "narrow the guard pattern and add a must-not-trigger test",
    "retrieval_miss": "the customer says it differently than the docs; add the wording to the alias list",
    "false_refusal": "the answer exists but scored low; check the query terms and MIN_SCORE",
    "wrong_sentence": "right section, wrong sentence; improve best_sentence",
}


def triage(root=ROOT, tag=""):
    path = root / "out" / f"{tag}traces.jsonl"
    traces = [json.loads(l) for l in path.read_text().splitlines()]
    groups = {}
    for t in traces:
        if not t["passed"]:
            groups.setdefault(t["bucket"], []).append(t)
    order = sorted(groups, key=lambda b: (SEVERITY.index(b), -len(groups[b])))
    return [(b, groups[b]) for b in order]


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else ""
    for bucket, items in triage(tag=tag):
        print(f"{bucket}  x{len(items)}  -> {NEXT_MOVE[bucket]}")
        for t in items:
            r = t["result"]
            print(f"  {t['id']}  {t['expect']['question']}")
            print(f"       expected {t['expect'].get('expect_doc') or t['expect']['expect_action']}"
                  f"  got {r['action']}  retrieved {r['retrieved'][:2]}")


if __name__ == "__main__":
    main()
