import json
from pathlib import Path
from attestable.types import Outcome
from attestable.evidence import EvidenceStore
from attestable.predicates import default_registry
from attestable.controls.user_access_sod import USER_ACCESS_SOD
from attestable.audit.log import AuditLog
from attestable.audit.replay import audit_replay
from attestable.escalation import EscalationQueue
from attestable.pipeline import run_control
from attestable.scenarios.build_scenarios import build_scenarios

ROW = {"14": "C2", "15": "C3", "16": "C4", "17": "C5"}

def _span(text, sub):
    i = text.index(sub)
    return {"kind": "span", "doc": "approvals.txt", "start": i, "end": i + len(sub), "quote": sub}

class Scripted:
    def __init__(self, payload): self.payload = payload
    def complete(self, prompt): return self.payload

def _facts(store, uid, current_value, approved_value):
    facts = [{"claim": "current_entitlements", "value": current_value,
              "citation": {"kind": "cell", "doc": "access_export.xlsx", "sheet": "Users", "cell": ROW[uid]}}]
    if approved_value is not None:
        facts.append({"claim": "approved_entitlements", "value": approved_value,
                      "citation": _span(store.text("approvals.txt"), approved_value)})
    return json.dumps(facts)

def _run(root, uid, current_value, approved_value):
    store = EvidenceStore(root)
    llm = Scripted(_facts(store, uid, current_value, approved_value))
    queue = EscalationQueue(root / "queue.jsonl")
    log = AuditLog()
    result = run_control(USER_ACCESS_SOD, store, uid, llm, default_registry(), log, queue)
    report = audit_replay(log, store, default_registry(), USER_ACCESS_SOD, uid)
    return result, report, queue

def test_e2e_all_four_outcomes_and_replays(tmp_path: Path):
    build_scenarios(tmp_path)
    # user 14: holds both toxic entitlements -> EXCEPTION (SoD)
    r, rep, _ = _run(tmp_path, "14", "payment_creator;payment_approver", "payment_creator;payment_approver")
    assert r.verdict.outcome is Outcome.EXCEPTION and "segregation" in r.verdict.narrative.lower()
    assert rep.ok
    # user 15: approval field blank -> UNVERIFIABLE + escalated
    r, rep, queue = _run(tmp_path, "15", "payment_creator", None)
    assert r.verdict.outcome is Outcome.UNVERIFIABLE and rep.ok
    assert any(item["sample_id"] == "15" for item in queue.pending())
    # user 16: no approval, corpus complete -> EXCEPTION (unapproved)
    r, rep, _ = _run(tmp_path, "16", "payment_creator", None)
    assert r.verdict.outcome is Outcome.EXCEPTION and rep.ok
    # user 17: within approval, no conflict -> PASS
    r, rep, _ = _run(tmp_path, "17", "payment_creator", "payment_creator;reporting")
    assert r.verdict.outcome is Outcome.PASS and rep.ok
    assert "PASS" in r.workpaper and r.seal
