from attestable.types import CellRef, Assertion
from attestable.evidence import EvidenceStore
from attestable.predicates import default_registry, PredicateRegistry
from attestable.gate import verify_assertion


def test_faithful_assertion_passes(evidence_root):
    store, reg = EvidenceStore(evidence_root), default_registry()
    a = Assertion("role", "payments_admin", CellRef("access_export.xlsx", "Users", "C2"))
    res = verify_assertion(a, store, reg)
    assert res.ok and res.fact is not None and res.fact.resolved == "payments_admin"


def test_unresolvable_citation_rejected(evidence_root):
    store, reg = EvidenceStore(evidence_root), default_registry()
    a = Assertion("role", "payments_admin", CellRef("access_export.xlsx", "Users", "Z99"))
    res = verify_assertion(a, store, reg)
    assert not res.ok and res.reason == "unresolvable"


def test_misciting_value_rejected(evidence_root):
    store, reg = EvidenceStore(evidence_root), default_registry()
    a = Assertion("role", "super_admin", CellRef("access_export.xlsx", "Users", "C2"))
    res = verify_assertion(a, store, reg)
    assert not res.ok and res.reason == "unfaithful"


def test_no_citation_rejected(evidence_root):
    store, reg = EvidenceStore(evidence_root), default_registry()
    a = Assertion("role", "x", None)
    res = verify_assertion(a, store, reg)
    assert not res.ok and res.reason == "no-citation"


def test_no_predicate_rejected(evidence_root):
    store = EvidenceStore(evidence_root)
    empty_registry = PredicateRegistry()
    a = Assertion("role", "payments_admin", CellRef("access_export.xlsx", "Users", "C2"))
    res = verify_assertion(a, store, empty_registry)
    assert not res.ok and res.reason == "no-predicate"
