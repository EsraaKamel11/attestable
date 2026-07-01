from dataclasses import dataclass
from .types import Assertion, VerifiedFact
from .evidence import EvidenceStore
from .predicates import PredicateRegistry


@dataclass
class GateResult:
    ok: bool
    fact: VerifiedFact | None
    reason: str


def verify_assertion(assertion: Assertion, store: EvidenceStore, registry: PredicateRegistry) -> GateResult:
    if assertion.citation is None:
        return GateResult(False, None, "no-citation")
    resolved = store.resolve(assertion.citation)
    if resolved is None:
        return GateResult(False, None, "unresolvable")
    predicate = registry.for_citation(assertion.citation)
    if predicate is None:
        return GateResult(False, None, "no-predicate")
    if not predicate.faithful(assertion, resolved):
        return GateResult(False, None, "unfaithful")
    return GateResult(True, VerifiedFact(assertion=assertion, resolved=resolved), "ok")
