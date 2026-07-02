from pathlib import Path
from attestable.connectors.base import content_hash, Provenance, FetchResult

def test_content_hash_is_deterministic_sha256_hex():
    h = content_hash(b"hello")
    assert h == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
    assert content_hash(b"hello") == h and content_hash(b"world") != h

def test_provenance_and_fetchresult_hold_fields():
    p = Provenance(doc="access_export.xlsx", method="api", locator="GET /users/14/access", content_hash="abc")
    fr = FetchResult(root=Path("/tmp/x"), provenance=[p])
    assert fr.provenance[0].method == "api" and fr.provenance[0].locator.endswith("/access")
