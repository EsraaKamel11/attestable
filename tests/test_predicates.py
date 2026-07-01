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


def test_for_citation_returns_none_for_unknown():
    from attestable.predicates import default_registry
    reg = default_registry()
    assert reg.for_citation("not a citation") is None
    assert reg.for_citation(None) is None


def test_predicates_satisfy_protocol():
    from attestable.predicates import CellValueEquals, ExactSpanVerbatim, Predicate
    assert isinstance(CellValueEquals(), Predicate)
    assert isinstance(ExactSpanVerbatim(), Predicate)


def test_cell_value_equals_strips_whitespace():
    from attestable.types import CellRef, Assertion
    from attestable.predicates import CellValueEquals
    a = Assertion("role", "payments_admin", CellRef("d.xlsx", "Users", "C2"))
    assert CellValueEquals().faithful(a, resolved="  payments_admin  ") is True


def test_faithful_raises_on_wrong_citation_type():
    import pytest
    from attestable.types import CellRef, TextSpan, Assertion
    from attestable.predicates import CellValueEquals, ExactSpanVerbatim
    span_assertion = Assertion("x", "v", TextSpan("d", 0, 1, "v"))
    with pytest.raises(TypeError):
        CellValueEquals().faithful(span_assertion, resolved="v")
    cell_assertion = Assertion("x", "v", CellRef("d", "s", "A1"))
    with pytest.raises(TypeError):
        ExactSpanVerbatim().faithful(cell_assertion, resolved="v")
