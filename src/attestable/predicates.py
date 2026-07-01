from typing import Protocol, runtime_checkable
from .types import Citation, CellRef, TextSpan, Assertion


@runtime_checkable
class Predicate(Protocol):
    def applies(self, citation: Citation) -> bool: ...
    def faithful(self, assertion: Assertion, resolved: str) -> bool: ...


class CellValueEquals:
    def applies(self, citation: Citation) -> bool:
        return isinstance(citation, CellRef)

    def faithful(self, assertion: Assertion, resolved: str) -> bool:
        if not isinstance(assertion.citation, CellRef):
            raise TypeError(
                f"CellValueEquals.faithful requires a CellRef citation, "
                f"got {type(assertion.citation).__name__}"
            )
        return resolved.strip() == assertion.value.strip()


class ExactSpanVerbatim:
    def applies(self, citation: Citation) -> bool:
        return isinstance(citation, TextSpan)

    def faithful(self, assertion: Assertion, resolved: str) -> bool:
        # the resolved substring must equal both the asserted value and the cited quote
        if not isinstance(assertion.citation, TextSpan):
            raise TypeError(
                f"ExactSpanVerbatim.faithful requires a TextSpan citation, "
                f"got {type(assertion.citation).__name__}"
            )
        return resolved == assertion.value == assertion.citation.quote


class PredicateRegistry:
    def __init__(self) -> None:
        self._predicates: list[Predicate] = []

    def register(self, predicate: Predicate) -> None:
        self._predicates.append(predicate)

    def for_citation(self, citation: Citation) -> Predicate | None:
        for p in self._predicates:
            if p.applies(citation):
                return p
        return None


def default_registry() -> PredicateRegistry:
    reg = PredicateRegistry()
    reg.register(CellValueEquals())
    reg.register(ExactSpanVerbatim())
    return reg
