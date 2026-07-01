from dataclasses import dataclass
from typing import Callable
from ..types import Outcome, VerifiedFact
from ..evidence import EvidenceStore


@dataclass(frozen=True)
class ControlDefinition:
    name: str
    required_keys: list[str]
    rule: Callable[[dict[str, VerifiedFact]], tuple[Outcome, str]]
    approval_status: Callable[[EvidenceStore, str], str]  # "readable"|"unreadable"|"absent"
    corpus_complete: Callable[[EvidenceStore], bool]
