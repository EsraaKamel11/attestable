from dataclasses import dataclass, field
from enum import Enum


class Outcome(str, Enum):
    PASS = "pass"
    EXCEPTION = "exception"
    UNVERIFIABLE = "unverifiable"


@dataclass(frozen=True)
class CellRef:
    doc: str
    sheet: str
    cell: str  # A1-style, e.g. "C14"


@dataclass(frozen=True)
class TextSpan:
    doc: str
    start: int
    end: int
    quote: str  # the exact substring expected at [start:end]


Citation = CellRef | TextSpan


@dataclass(frozen=True)
class Assertion:
    claim: str
    value: str
    citation: Citation


@dataclass(frozen=True)
class VerifiedFact:
    assertion: Assertion
    resolved: str  # the content the citation resolved to


@dataclass
class Verdict:
    outcome: Outcome
    verified: list[VerifiedFact] = field(default_factory=list)
    unmet: list[str] = field(default_factory=list)
    narrative: str = ""
