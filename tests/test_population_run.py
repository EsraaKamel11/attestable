import json
from attestable.scenarios.build_scenarios import build_scenarios
from attestable.evidence import EvidenceStore
from attestable.controls.user_access_sod import USER_ACCESS_SOD
from attestable.types import Outcome
from attestable.population import run_population

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

def test_population_run_outcomes_and_summary(tmp_path):
    build_scenarios(tmp_path)
    store = EvidenceStore(tmp_path)
    result = run_population(USER_ACCESS_SOD, store, _llm_for(tmp_path))
    outcomes = {uo.uid: uo.verdict.outcome for uo in result.per_user}
    assert outcomes == {"14": Outcome.EXCEPTION, "15": Outcome.UNVERIFIABLE,
                        "16": Outcome.EXCEPTION, "17": Outcome.PASS}
    assert result.summary == {"tested": 4, "passes": 1, "exceptions": 2, "escalations": 1}
    actions = [e["action"] for e in result.log.entries]
    assert actions.count("sample.begin") == 4
    assert actions[0] == "sample.begin"
    assert result.seal == result.log.seal()
