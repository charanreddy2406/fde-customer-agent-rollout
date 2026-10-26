import json
from pathlib import Path

from .agent import answer
from .checks import verify
from .kb import KnowledgeBase

ROOT = Path(__file__).resolve().parent.parent


def grade(ticket, result, kb):
    """Return (passed, bucket). bucket is None when the ticket passes."""
    want, got = ticket["expect_action"], result["action"]
    if want == "escalate" and got != "escalate":
        return False, "missed_escalation"
    if want == "refuse" and got == "answer":
        return False, "made_up_answer"
    if want == "answer" and got == "escalate":
        return False, "false_escalation"
    if want == "answer" and got == "refuse":
        return False, "false_refusal"
    if want == "answer" and got == "answer":
        if not verify(result, kb)[0]:
            return False, "bad_citation"
        cite = result["cite"]
        if (cite["doc"], cite["heading"]) != (ticket["expect_doc"], ticket["expect_heading"]):
            return False, "retrieval_miss"
        if ticket["must_contain"].lower() not in result["text"].lower():
            return False, "wrong_sentence"
    return True, None


def run(root=ROOT, tickets_file="tickets.jsonl", tag=""):
    kb = KnowledgeBase(root / "data" / "docs")
    lines = (root / "data" / tickets_file).read_text().splitlines()
    traces, buckets = [], {}
    for ticket in map(json.loads, lines):
        result = answer(kb, ticket["question"])
        passed, bucket = grade(ticket, result, kb)
        traces.append({"id": ticket["id"], "passed": passed, "bucket": bucket,
                       "expect": ticket, "result": result})
        if bucket:
            buckets[bucket] = buckets.get(bucket, 0) + 1
    out = root / "out"
    out.mkdir(exist_ok=True)
    (out / f"{tag}traces.jsonl").write_text("".join(json.dumps(t) + "\n" for t in traces))
    passed = sum(t["passed"] for t in traces)
    summary = {
        "total": len(traces), "passed": passed,
        "pass_rate": round(passed / len(traces), 3), "buckets": buckets,
    }
    (out / f"{tag}summary.json").write_text(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    print("tuning set", json.dumps(run()))
    print("held out  ", json.dumps(run(tickets_file="holdout.jsonl", tag="holdout-")))
