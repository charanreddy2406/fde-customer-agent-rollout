import re

SAFETY_OR_LEGAL = re.compile(
    r"\bsmell\w*\b.*\bgas\b|\bgas (smell|leak)|\b(smoke|smoking|sparks?|"
    r"carbon monoxide|lawyer|attorney|sue|lawsuit|injur\w+)\b|\bon fire\b",
    re.I,
)
MONEY = re.compile(r"\$\s?(\d[\d,]*(?:\.\d+)?)")
MONEY_WORDS = re.compile(r"(\d[\d,]*(?:\.\d+)?)\s?(?:dollars?|usd)\b", re.I)
REFUND_WORDS = re.compile(r"refund|money back|chargeback", re.I)
REFUND_LIMIT = 500


def escalation_reason(question):
    """Return why a person must handle this ticket, or None. No model involved."""
    hit = SAFETY_OR_LEGAL.search(question)
    if hit:
        return "safety or legal wording"
    if REFUND_WORDS.search(question):
        for amount in MONEY.findall(question) + MONEY_WORDS.findall(question):
            if float(amount.replace(",", "")) > REFUND_LIMIT:
                return "refund above the manager limit"
    return None
