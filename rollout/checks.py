def verify(result, kb):
    """True only if an answer quotes its cited section word for word."""
    if result["action"] != "answer":
        return True, "nothing to verify"
    cite = result.get("cite")
    if not cite:
        return False, "answer has no citation"
    body = kb.section(cite["doc"], cite["heading"])
    if body is None:
        return False, "cited section does not exist"
    if result["text"] not in body:
        return False, "quote is not verbatim in the cited section"
    return True, "verbatim"
