# tests/test_connector_e2e.py
"""End to end: acquire evidence from the synthetic SoR API, decide a cited verdict,
and replay the whole trail including the acquisition. T5 shows acquisition-audit catches
an uncited-byte tamper that grounding does not."""
import json
from fastapi.testclient import TestClient
from attestable.sor.app import build_sor
from attestable.connectors.api import ApiConnector
from attestable.connectors.orchestrate import run_with_connector
from attestable.controls.user_access_sod import USER_ACCESS_SOD
from attestable.predicates import default_registry
from attestable.evidence import EvidenceStore
from attestable.audit.replay import audit_replay
from attestable.types import Outcome

USERS = [
    {"user_id": "14", "name": "Sam Lee", "entitlements": "payment_creator;payment_approver", "approved": "payment_creator;payment_approver"},
    {"user_id": "17", "name": "Jo Kim", "entitlements": "payment_creator", "approved": "payment_creator;reporting"},
]

class Scripted:
    def __init__(self, payload): self.payload = payload
    def complete(self, prompt): return self.payload

def _facts(uid, cur, appr):
    text = f"# approvals_complete: true\nApproval 1: user {uid} approved entitlements: {appr}\n"
    start = text.index(appr); end = start + len(appr)
    return json.dumps([
        {"claim": "current_entitlements", "value": cur,
         "citation": {"kind": "cell", "doc": "access_export.xlsx", "sheet": "Users", "cell": "C2"}},
        {"claim": "approved_entitlements", "value": appr,
         "citation": {"kind": "span", "doc": "approvals.txt", "start": start, "end": end, "quote": appr}},
    ])

def test_e2e_exception_with_full_green_replay(tmp_path):
    conn = ApiConnector(TestClient(build_sor(USERS)))
    llm = Scripted(_facts("14", "payment_creator;payment_approver", "payment_creator;payment_approver"))
    result, store, log = run_with_connector(conn, "14", USER_ACCESS_SOD, "14", llm, tmp_path, return_log=True)
    assert result.verdict.outcome is Outcome.EXCEPTION
    report = audit_replay(log, store, default_registry(), USER_ACCESS_SOD, "14", result.seal)
    assert (report.integrity, report.grounding, report.derivation, report.acquisition) == (True, True, True, True)

def test_e2e_pass_user_over_api(tmp_path):
    conn = ApiConnector(TestClient(build_sor(USERS)))
    llm = Scripted(_facts("17", "payment_creator", "payment_creator;reporting"))
    result, store, log = run_with_connector(conn, "17", USER_ACCESS_SOD, "17", llm, tmp_path, return_log=True)
    assert result.verdict.outcome is Outcome.PASS
    assert audit_replay(log, store, default_registry(), USER_ACCESS_SOD, "17", result.seal).ok

def test_t5_acquisition_catches_uncited_tamper(tmp_path):
    conn = ApiConnector(TestClient(build_sor(USERS)))
    llm = Scripted(_facts("14", "payment_creator;payment_approver", "payment_creator;payment_approver"))
    result, store, log = run_with_connector(conn, "14", USER_ACCESS_SOD, "14", llm, tmp_path, return_log=True)
    with open(tmp_path / "approvals.txt", "a", encoding="utf-8") as f:
        f.write("# added after sealing\n")
    report = audit_replay(log, EvidenceStore(tmp_path), default_registry(), USER_ACCESS_SOD, "14", result.seal)
    assert report.integrity is True and report.derivation is True
    assert report.grounding is True and report.acquisition is False and report.ok is False
