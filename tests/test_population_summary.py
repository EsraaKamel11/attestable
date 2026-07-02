import json
from attestable.scenarios.build_scenarios import build_scenarios
from attestable.evidence import EvidenceStore
from attestable.controls.user_access_sod import USER_ACCESS_SOD
from attestable.population import run_population, render_population_summary

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

def test_population_summary_lists_exceptions_and_escalations(tmp_path):
    build_scenarios(tmp_path)
    store = EvidenceStore(tmp_path)
    result = run_population(USER_ACCESS_SOD, store, _llm_for(tmp_path))
    md = render_population_summary(USER_ACCESS_SOD, result)
    assert "user-access-review-sod" in md
    assert "Population tested: 4" in md
    assert "Exceptions: 2" in md and "Escalations: 1" in md
    # each exception user appears with a cited source; the escalated user appears in escalations
    assert "user 14" in md and "user 16" in md and "user 15" in md
    assert "access_export.xlsx" in md   # a cited source is shown
    assert "—" not in md           # em-dash-free
