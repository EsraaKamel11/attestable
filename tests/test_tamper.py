"""The three tamper tests: content, structure, and source-document tampering."""
import openpyxl
from attestable.types import Outcome, CellRef
from attestable.controls.definition import ControlDefinition
from attestable.audit.log import AuditLog
from attestable.audit.replay import audit_replay
from attestable.predicates import default_registry
from attestable.serial import citation_to_dict
from attestable.evidence import EvidenceStore

def _control():
    return ControlDefinition("t", ["role"], lambda v: (Outcome.PASS, "ok"),
                             lambda s, sid: "readable", lambda s: True)

def _log():
    log = AuditLog()
    cit = CellRef("access_export.xlsx", "Users", "C2")
    log.append("gate", "fact.accepted",
               {"claim": "role", "value": "payments_admin", "citation": citation_to_dict(cit)})
    log.append("verdict", "verdict", {"outcome": "pass", "narrative": "ok", "unmet": []})
    return log

def test_T1_content_tamper_breaks_integrity(evidence_root):
    log = _log()
    seal = log.seal()
    log.entries[0]["payload"]["value"] = "read_only"  # edit a logged fact
    report = audit_replay(log, EvidenceStore(evidence_root), default_registry(), _control(), "14", seal)
    assert report.integrity is False

def test_T2_structure_tamper_breaks_integrity(evidence_root):
    log = _log()
    seal = log.seal()
    log.entries.pop(0)  # drop an entry
    report = audit_replay(log, EvidenceStore(evidence_root), default_registry(), _control(), "14", seal)
    assert report.integrity is False

def test_T3_source_tamper_kept_log_but_breaks_grounding(evidence_root):
    log = _log()
    seal = log.seal()
    wb = openpyxl.load_workbook(evidence_root / "access_export.xlsx")
    wb["Users"]["C2"] = "read_only"  # edit the underlying evidence after sealing
    wb.save(evidence_root / "access_export.xlsx")
    report = audit_replay(log, EvidenceStore(evidence_root), default_registry(), _control(), "14", seal)
    assert report.integrity is True and report.grounding is False

def test_T4_tail_truncation_breaks_integrity(evidence_root):
    log = _log()
    seal = log.seal()
    log.entries.pop()  # drop the last entry (the verdict)
    report = audit_replay(log, EvidenceStore(evidence_root), default_registry(), _control(), "14", seal)
    assert report.integrity is False and report.ok is False

def test_empty_log_is_not_ok(evidence_root):
    log = _log()
    seal = log.seal()
    log.entries.clear()
    report = audit_replay(log, EvidenceStore(evidence_root), default_registry(), _control(), "14", seal)
    assert report.ok is False
