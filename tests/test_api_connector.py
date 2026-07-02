# tests/test_api_connector.py
from fastapi.testclient import TestClient
from attestable.sor.app import build_sor
from attestable.connectors.api import ApiConnector
from attestable.connectors.base import content_hash
from attestable.evidence import EvidenceStore
from attestable.types import CellRef

USERS = [{"user_id": "14", "name": "Sam Lee",
          "entitlements": "payment_creator;payment_approver",
          "approved": "payment_creator;payment_approver"}]

def test_fetch_materializes_slice1_evidence_and_provenance(tmp_path):
    conn = ApiConnector(TestClient(build_sor(USERS)))
    fr = conn.fetch("14", tmp_path)
    # evidence is in the Slice-1 forms and resolves through the ordinary store
    store = EvidenceStore(fr.root)
    assert store.resolve(CellRef("access_export.xlsx", "Users", "C2")) == "payment_creator;payment_approver"
    assert "user 14 approved entitlements: payment_creator;payment_approver" in store.text("approvals.txt")
    # one provenance per doc, method api, hash matches the persisted bytes
    docs = {p.doc: p for p in fr.provenance}
    assert set(docs) == {"access_export.xlsx", "approvals.txt"}
    for p in fr.provenance:
        assert p.method == "api" and p.locator == "GET /users/14/access"
        assert p.content_hash == content_hash(store.raw(p.doc))
