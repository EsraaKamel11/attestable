from attestable.types import CellRef, Assertion
from attestable.evidence import EvidenceStore
from attestable.predicates import default_registry
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
