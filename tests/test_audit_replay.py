from attestable.types import Outcome, Assertion, CellRef
from attestable.controls.definition import ControlDefinition
from attestable.audit.log import AuditLog
from attestable.audit.replay import audit_replay
from attestable.predicates import default_registry
from attestable.serial import citation_to_dict
from attestable.evidence import EvidenceStore

def _good_log():
    log = AuditLog()
    cit = CellRef("access_export.xlsx", "Users", "C2")
    log.append("gate", "fact.accepted",
               {"claim": "role", "value": "payments_admin", "citation": citation_to_dict(cit)})
    log.append("verdict", "verdict", {"outcome": "pass", "narrative": "ok", "unmet": []})
    return log

def _control():
    return ControlDefinition("t", ["role"], lambda v: (Outcome.PASS, "ok"),
                             lambda s, sid: "readable", lambda s: True)

def test_clean_log_replays_all_green(evidence_root):
    log = _good_log()
    seal = log.seal()
    report = audit_replay(log, EvidenceStore(evidence_root), default_registry(), _control(), "14", seal)
    assert report.integrity and report.grounding and report.derivation and report.ok
