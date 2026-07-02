# tests/test_replay_acquisition.py
import json
from fastapi.testclient import TestClient
from attestable.sor.app import build_sor
from attestable.connectors.api import ApiConnector
from attestable.connectors.orchestrate import run_with_connector
from attestable.controls.user_access_sod import USER_ACCESS_SOD
from attestable.predicates import default_registry
from attestable.evidence import EvidenceStore
from attestable.audit.replay import audit_replay, ReplayReport

USERS = [{"user_id": "14", "name": "Sam Lee",
          "entitlements": "payment_creator;payment_approver",
          "approved": "payment_creator;payment_approver"}]

class Scripted:
    def __init__(self, payload): self.payload = payload
    def complete(self, prompt): return self.payload

def _facts():
    text = ("# approvals_complete: true\n"
            "Approval 1: user 14 approved entitlements: payment_creator;payment_approver\n")
    appr = "payment_creator;payment_approver"
    start = text.index(appr); end = start + len(appr)
    return json.dumps([
        {"claim": "current_entitlements", "value": "payment_creator;payment_approver",
         "citation": {"kind": "cell", "doc": "access_export.xlsx", "sheet": "Users", "cell": "C2"}},
        {"claim": "approved_entitlements", "value": "payment_creator;payment_approver",
         "citation": {"kind": "span", "doc": "approvals.txt", "start": start, "end": end, "quote": appr}},
    ])

def test_acquisition_true_on_untampered_run(tmp_path):
    conn = ApiConnector(TestClient(build_sor(USERS)))
    result, store, log = run_with_connector(conn, "14", USER_ACCESS_SOD, "14",
                                            Scripted(_facts()), tmp_path, return_log=True)
    report = audit_replay(log, store, default_registry(), USER_ACCESS_SOD, "14", result.seal)
    assert report.acquisition is True and report.ok is True

def test_acquisition_false_when_fetched_doc_changes_after_seal(tmp_path):
    conn = ApiConnector(TestClient(build_sor(USERS)))
    result, store, log = run_with_connector(conn, "14", USER_ACCESS_SOD, "14",
                                            Scripted(_facts()), tmp_path, return_log=True)
    # append an UNCITED comment line: grounding still passes, acquisition must catch the byte change
    with open(tmp_path / "approvals.txt", "a", encoding="utf-8") as f:
        f.write("# tampered comment\n")
    fresh = EvidenceStore(tmp_path)  # fresh store so caches do not hide the tamper
    report = audit_replay(log, fresh, default_registry(), USER_ACCESS_SOD, "14", result.seal)
    assert report.grounding is True      # the cited span is unchanged
    assert report.integrity is True and report.derivation is True
    assert report.acquisition is False   # the doc's bytes changed since fetch
    assert report.ok is False

def test_replayreport_default_keeps_slice1_construction_valid():
    assert ReplayReport(True, True, True).acquisition is True
    assert ReplayReport(True, True, True).ok is True
