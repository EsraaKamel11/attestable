import json
from fastapi.testclient import TestClient
from attestable.sor.app import build_sor
from attestable.connectors.api import ApiConnector
from attestable.connectors.orchestrate import run_with_connector
from attestable.controls.user_access_sod import USER_ACCESS_SOD
from attestable.types import Outcome

USERS = [{"user_id": "14", "name": "Sam Lee",
          "entitlements": "payment_creator;payment_approver",
          "approved": "payment_creator;payment_approver"}]

class Scripted:
    def __init__(self, payload): self.payload = payload
    def complete(self, prompt): return self.payload

def _facts():
    # compute the span offset against the exact approvals.txt the ApiConnector writes
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

def test_orchestrator_logs_acquire_before_facts_and_verdict(tmp_path):
    conn = ApiConnector(TestClient(build_sor(USERS)))
    result, store, log = run_with_connector(conn, "14", USER_ACCESS_SOD, "14",
                                            Scripted(_facts()), tmp_path, return_log=True)
    actions = [e["action"] for e in log.entries]
    assert actions[0] == "evidence.acquired" and actions.count("evidence.acquired") == 2
    assert actions.index("verdict") > max(i for i, a in enumerate(actions) if a == "evidence.acquired")
    assert "fact.accepted" in actions
    assert result.verdict.outcome is Outcome.EXCEPTION
