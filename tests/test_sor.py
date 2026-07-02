from fastapi.testclient import TestClient
from attestable.sor.app import build_sor

USERS = [
    {"user_id": "14", "name": "Sam Lee", "entitlements": "payment_creator;payment_approver", "approved": "payment_creator;payment_approver"},
    {"user_id": "17", "name": "Jo Kim", "entitlements": "payment_creator", "approved": "payment_creator;reporting"},
]

def test_sor_serves_seeded_user():
    client = TestClient(build_sor(USERS))
    r = client.get("/users/14/access")
    assert r.status_code == 200
    body = r.json()
    assert body["entitlements"] == "payment_creator;payment_approver"
    assert body["approved"] == "payment_creator;payment_approver"

def test_sor_404_for_unknown_user():
    client = TestClient(build_sor(USERS))
    assert client.get("/users/999/access").status_code == 404
