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


def test_corrupted_xlsx_returns_none(evidence_root):
    """Corrupted but existent xlsx file returns None instead of raising."""
    (evidence_root / "bad.xlsx").write_bytes(b"not a real xlsx")
    store = EvidenceStore(evidence_root)
    assert store.resolve(CellRef("bad.xlsx", "Users", "A1")) is None


def test_missing_sheet_returns_none(evidence_root):
    """Missing sheet returns None instead of raising."""
    store = EvidenceStore(evidence_root)
    assert store.resolve(CellRef("access_export.xlsx", "NoSuchSheet", "A1")) is None


def test_malformed_cell_coordinate_returns_none(evidence_root):
    """Malformed cell coordinate returns None instead of raising."""
    store = EvidenceStore(evidence_root)
    assert store.resolve(CellRef("access_export.xlsx", "Users", "NOT-A-CELL")) is None


def test_missing_document_textspan_returns_none(evidence_root):
    """TextSpan on missing document returns None."""
    store = EvidenceStore(evidence_root)
    assert store.resolve(TextSpan("missing.txt", 0, 3, "abc")) is None


def test_out_of_range_textspan_returns_none(evidence_root):
    """Out-of-range TextSpan returns None."""
    store = EvidenceStore(evidence_root)
    assert store.resolve(TextSpan("approvals.txt", 0, 99999, "x")) is None
