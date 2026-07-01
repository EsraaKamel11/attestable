"""Headline artifact: the pipeline refuses to accept fabricated or mis-cited claims."""
from attestable.types import CellRef, Assertion
from attestable.evidence import EvidenceStore
from attestable.predicates import default_registry
from attestable.gate import verify_assertion


def test_fabricated_source_is_rejected(evidence_root):
    store, reg = EvidenceStore(evidence_root), default_registry()
    invented = Assertion("role", "payments_admin", CellRef("does_not_exist.xlsx", "Users", "C2"))
    assert verify_assertion(invented, store, reg).reason == "unresolvable"


def test_real_cell_wrong_value_is_rejected(evidence_root):
    store, reg = EvidenceStore(evidence_root), default_registry()
    twisted = Assertion("role", "read_only", CellRef("access_export.xlsx", "Users", "C2"))
    assert verify_assertion(twisted, store, reg).reason == "unfaithful"
