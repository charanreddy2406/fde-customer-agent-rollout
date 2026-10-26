import re

from .checks import verify
from .guards import escalation_reason

MIN_SCORE = 1.0
HANDOFF = "I do not have that in the help center, so I am passing it to a person."
ESCALATE = "This needs a person, so I am passing it to our support team now."


def sentences(body):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", body) if s.strip()]


def best_sentence(body, terms):
    """The two neighbouring sentences that share the most words with the question."""
    stems = {t[:5] for t in terms}
    parts = sentences(body)

    def overlap(sentence):
        words = re.findall(r"[a-z0-9]+", sentence.lower())
        return sum(1 for w in words if w[:5] in stems)

    windows = [parts[i:i + 2] for i in range(max(1, len(parts) - 1))]
    best = max(windows, key=lambda w: sum(overlap(s) for s in w))
    return " ".join(best)


def answer(kb, question, compose=None):
    why = escalation_reason(question)
    if why:
        return {
            "question": question, "retrieved": [], "score": 0.0,
            "action": "escalate", "text": ESCALATE, "cite": None, "reason": why,
        }
    hits = kb.search(question)
    result = {
        "question": question,
        "retrieved": [f"{h['doc']}/{h['heading']}" for h in hits],
        "score": hits[0]["score"] if hits else 0.0,
    }
    if not hits or hits[0]["score"] < MIN_SCORE:
        return {**result, "action": "refuse", "text": HANDOFF, "cite": None}
    top = hits[0]
    compose = compose or best_sentence
    result.update(
        action="answer",
        text=compose(top["body"], kb.terms(question)),
        cite={"doc": top["doc"], "heading": top["heading"]},
    )
    ok, why = verify(result, kb)
    if not ok:
        return {**result, "action": "refuse", "text": HANDOFF, "reason": why}
    return result
