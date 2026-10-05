"""Ingestion / metadata parser: corpus/*.md -> Clause records with document metadata."""
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import yaml

from .config import CORPUS_DIR

CLAUSE_RE = re.compile(r"^\*\*(D\d+:C\d+)\*\*\s+—\s+(.*)$")


@dataclass(frozen=True)
class Clause:
    clause_id: str  # e.g. "D003:C1"
    doc_id: str
    text: str
    title: str
    issuing_authority: str
    effective_date: date
    sunset_date: date | None
    supersedes: str | None
    version: str
    category: str

    def in_force(self, as_of: date) -> bool:
        """Window is [effective_date, sunset_date] inclusive (charter: sunset is the last valid day)."""
        return self.effective_date <= as_of and (self.sunset_date is None or as_of <= self.sunset_date)


def _d(value) -> date | None:
    if value in (None, "", "null"):
        return None
    return value if isinstance(value, date) else date.fromisoformat(str(value))


def parse_document(path: Path) -> list[Clause]:
    raw = path.read_text(encoding="utf-8")
    _, front, body = raw.split("---", 2)
    meta = yaml.safe_load(front)
    clauses = []
    for line in body.splitlines():
        m = CLAUSE_RE.match(line.strip())
        if m:
            clauses.append(
                Clause(
                    clause_id=m.group(1),
                    doc_id=meta["doc_id"],
                    text=m.group(2).strip(),
                    title=meta["title"],
                    issuing_authority=meta["issuing_authority"],
                    effective_date=_d(meta["effective_date"]),
                    sunset_date=_d(meta.get("sunset_date")),
                    supersedes=meta.get("supersedes"),
                    version=str(meta["version"]),
                    category=meta["category"],
                )
            )
    return clauses


def load_corpus(corpus_dir: Path = CORPUS_DIR) -> list[Clause]:
    clauses: list[Clause] = []
    for path in sorted(corpus_dir.glob("D*.md")):
        clauses.extend(parse_document(path))
    return clauses
