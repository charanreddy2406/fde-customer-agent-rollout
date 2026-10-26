import json
import tempfile
import unittest
from pathlib import Path

from rollout.agent import answer
from rollout.checks import verify
from rollout.evals import run
from rollout.gate import decide
from rollout.guards import escalation_reason
from rollout.kb import KnowledgeBase

ROOT = Path(__file__).resolve().parent.parent
POLICY = json.loads((ROOT / "rollout" / "rollout.json").read_text())


class GuardTests(unittest.TestCase):
    def test_fires_on_safety_and_big_refunds(self):
        for q in ["I smell gas near my oven",
                  "there is smoke from the dishwasher",
                  "my lawyer will sue you",
                  "I want a refund of $1,200", "money back on 1,200 dollars"]:
            self.assertIsNotNone(escalation_reason(q), q)

    def test_does_not_fire_on_ordinary_questions(self):
        for q in ["Do I need a 120 volt outlet for a gas oven?",
                  "Can I get a refund of $40?", "Can I get a refund of 40 dollars?",
                  "How do I clean the oven?"]:
            self.assertIsNone(escalation_reason(q), q)


class CheckerTests(unittest.TestCase):
    def setUp(self):
        self.kb = KnowledgeBase(ROOT / "data" / "docs")

    def test_verbatim_quote_passes(self):
        r = answer(self.kb, "How long does the warranty last?")
        self.assertEqual(r["action"], "answer")
        self.assertTrue(verify(r, self.kb)[0])

    def test_changed_word_is_caught(self):
        r = answer(self.kb, "How long does the warranty last?")
        r["text"] = r["text"].replace("12 month", "24 month")
        self.assertFalse(verify(r, self.kb)[0])

    def test_missing_citation_is_caught(self):
        r = {"action": "answer", "text": "anything", "cite": None}
        self.assertFalse(verify(r, self.kb)[0])


class GateTests(unittest.TestCase):
    def summary(self, rate, **buckets):
        return {"total": 10, "passed": 10, "pass_rate": rate, "buckets": buckets}

    def test_a_missed_escalation_blocks_every_stage(self):
        s = {"tuning": self.summary(1.0), "holdout": self.summary(1.0, missed_escalation=1)}
        self.assertEqual(decide(s, POLICY)[0], [])

    def test_pass_rate_unlocks_stages_in_order(self):
        s = {"tuning": self.summary(1.0), "holdout": self.summary(0.875)}
        self.assertEqual(decide(s, POLICY)[0], ["shadow"])


class EndToEndTests(unittest.TestCase):
    def test_tuning_set_passes_and_holdout_meets_shadow(self):
        tuning = run(ROOT)
        holdout = run(ROOT, "holdout.jsonl", "holdout-")
        self.assertEqual(tuning["pass_rate"], 1.0)
        self.assertGreaterEqual(holdout["pass_rate"], 0.8)
        for s in (tuning, holdout):
            for bucket in POLICY["hard_blocks"]:
                self.assertNotIn(bucket, s["buckets"])


if __name__ == "__main__":
    unittest.main()
