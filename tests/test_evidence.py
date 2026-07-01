from attestable.types import CellRef, TextSpan
from attestable.evidence import EvidenceStore


def test_resolves_cell(evidence_root):
    store = EvidenceStore(evidence_root)
    got = store.resolve(CellRef("access_export.xlsx", "Users", "C2"))
    assert got == "payments_admin"


def test_unresolvable_cell_is_none(evidence_root):
    store = EvidenceStore(evidence_root)
    assert store.resolve(CellRef("access_export.xlsx", "Users", "Z99")) is None
    assert store.resolve(CellRef("missing.xlsx", "Users", "A1")) is None


def test_resolves_text_span(evidence_root):
    store = EvidenceStore(evidence_root)
    text = store.text("approvals.txt")
    i = text.index("read_only")
    got = store.resolve(TextSpan("approvals.txt", i, i + len("read_only"), "read_only"))
    assert got == "read_only"
