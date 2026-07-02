from attestable.evidence import EvidenceStore

def test_raw_returns_bytes_for_existing_doc(tmp_path):
    (tmp_path / "a.txt").write_text("hello", encoding="utf-8")
    store = EvidenceStore(tmp_path)
    assert store.raw("a.txt") == b"hello"

def test_raw_returns_none_for_missing_or_escaping(tmp_path):
    store = EvidenceStore(tmp_path)
    assert store.raw("nope.txt") is None
    assert store.raw("../outside.txt") is None
