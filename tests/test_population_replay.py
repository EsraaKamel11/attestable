# tests/test_population_replay.py
import json
from attestable.scenarios.build_scenarios import build_scenarios
from attestable.evidence import EvidenceStore
from attestable.controls.user_access_sod import USER_ACCESS_SOD
from attestable.predicates import default_registry
from attestable.population import run_population, population_replay

class Scripted:
    def __init__(self, payload): self.payload = payload
    def complete(self, prompt): return self.payload

def _llm_for(tmp_path):
    appr = (tmp_path / "approvals.txt").read_text(encoding="utf-8")
    def span(v): i = appr.index(v); return i, i + len(v)
    def facts(cell, cur, approved=None):
        out = [{"claim": "current_entitlements", "value": cur,
                "citation": {"kind": "cell", "doc": "access_export.xlsx", "sheet": "Users", "cell": cell}}]
        if approved is not None:
            s, e = span(approved)
            out.append({"claim": "approved_entitlements", "value": approved,
                        "citation": {"kind": "span", "doc": "approvals.txt", "start": s, "end": e, "quote": approved}})
        return Scripted(json.dumps(out))
    payloads = {
        "14": facts("C2", "payment_creator;payment_approver", "payment_creator;payment_approver"),
        "15": facts("C3", "payment_creator"),
        "16": facts("C4", "payment_creator"),
        "17": facts("C5", "payment_creator", "payment_creator;reporting"),
    }
    return lambda uid: payloads[uid]

def test_population_replay_all_green_and_summary_recomputed(tmp_path):
    build_scenarios(tmp_path)
    store = EvidenceStore(tmp_path)
    result = run_population(USER_ACCESS_SOD, store, _llm_for(tmp_path))
    report = population_replay(result.log, store, default_registry(), USER_ACCESS_SOD, result.seal)
    assert report.ok is True
    assert (report.integrity, report.grounding, report.derivation) == (True, True, True)
    assert report.summary == result.summary   # the headline counts are recomputed from the log

def test_population_replay_catches_one_users_source_tamper(tmp_path):
    build_scenarios(tmp_path)
    store = EvidenceStore(tmp_path)
    result = run_population(USER_ACCESS_SOD, store, _llm_for(tmp_path))
    # edit user 17's entitlements cell AFTER sealing: their citation no longer resolves to the logged value
    import openpyxl
    wb = openpyxl.load_workbook(tmp_path / "access_export.xlsx")
    wb["Users"]["C5"] = "payment_creator;admin"
    wb.save(tmp_path / "access_export.xlsx")
    report = population_replay(result.log, EvidenceStore(tmp_path), default_registry(),
                               USER_ACCESS_SOD, result.seal)
    assert report.integrity is True     # the log itself is intact
    assert report.grounding is False    # user 17's cited cell no longer matches the logged value
    assert report.ok is False
