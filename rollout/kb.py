import json
import re
import sqlite3
from pathlib import Path

STOP = {
    "a", "an", "and", "are", "can", "do", "does", "for", "how", "i", "in", "is",
    "it", "long", "me", "my", "of", "on", "or", "the", "to", "what", "when",
    "will", "with", "you", "your", "not", "out", "near",
}


ALIASES = json.loads((Path(__file__).parent / "aliases.json").read_text())


def load_sections(docs_dir):
    sections = []
    for path in sorted(Path(docs_dir).glob("*.txt")):
        heading, lines = None, []
        for line in path.read_text().splitlines():
            if line.startswith("## "):
                if heading:
                    sections.append((path.stem, heading, " ".join(lines)))
                heading, lines = line[3:].strip(), []
            elif heading and line.strip():
                lines.append(line.strip())
        if heading:
            sections.append((path.stem, heading, " ".join(lines)))
    return sections


class KnowledgeBase:
    def __init__(self, docs_dir):
        self.db = sqlite3.connect(":memory:")
        self.db.execute(
            "CREATE VIRTUAL TABLE sections USING fts5("
            "doc UNINDEXED, heading, body, tokenize='porter')"
        )
        for doc, heading, body in load_sections(docs_dir):
            self.db.execute("INSERT INTO sections VALUES (?, ?, ?)", (doc, heading, body))

    def terms(self, question):
        words = re.findall(r"[a-z0-9]+", question.lower())
        terms = [w for w in words if w not in STOP]
        extra = [a for w in terms for a in ALIASES.get(w, [])]
        return terms + extra

    def search(self, question, k=3):
        terms = self.terms(question)
        if not terms:
            return []
        query = " OR ".join(f'"{t}"' for t in terms)
        rows = self.db.execute(
            "SELECT doc, heading, body, -bm25(sections, 0, 3.0, 1.0) AS score "
            "FROM sections WHERE sections MATCH ? ORDER BY score DESC LIMIT ?",
            (query, k),
        ).fetchall()
        return [{"doc": d, "heading": h, "body": b, "score": s} for d, h, b, s in rows]

    def section(self, doc, heading):
        row = self.db.execute(
            "SELECT body FROM sections WHERE doc = ? AND heading = ?", (doc, heading)
        ).fetchone()
        return row[0] if row else None
