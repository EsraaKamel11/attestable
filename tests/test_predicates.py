from attestable.types import CellRef, TextSpan, Assertion
from attestable.predicates import CellValueEquals, ExactSpanVerbatim, default_registry


def test_cell_value_equals_faithful():
    p = CellValueEquals()
    a = Assertion("role", "payments_admin", CellRef("d.xlsx", "Users", "C2"))
    assert p.applies(a.citation) is True
    assert p.faithful(a, resolved="payments_admin") is True
    assert p.faithful(a, resolved="read_only") is False


def test_exact_span_verbatim_requires_quote_match():
    p = ExactSpanVerbatim()
    a = Assertion("approved", "read_only", TextSpan("a.txt", 5, 14, "read_only"))
    assert p.applies(a.citation) is True
    # resolved is the substring the store returned for [start:end]
    assert p.faithful(a, resolved="read_only") is True
    assert p.faithful(a, resolved="read/writ") is False


def test_registry_routes_by_citation_type():
    reg = default_registry()
    assert isinstance(reg.for_citation(CellRef("d", "s", "A1")), CellValueEquals)
    assert isinstance(reg.for_citation(TextSpan("d", 0, 1, "x")), ExactSpanVerbatim)
