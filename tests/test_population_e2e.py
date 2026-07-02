"""Population-based testing, demonstrated end to end: the per-record user-access + SoD control
run over the whole access-export population under one sealed audit log, with a green replay that
re-verifies every user's citations and verdicts and recomputes the headline counts from the log."""
import json
from attestable.scenarios.build_scenarios import build_scenarios
from attestable.evidence import EvidenceStore
from attestable.controls.user_access_sod import USER_ACCESS_SOD
from attestable.predicates import default_registry
from attestable.types import Outcome
from attestable.population import run_population, population_replay, render_population_summary

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

def test_full_population_run_and_green_replay(tmp_path):
    build_scenarios(tmp_path)
    store = EvidenceStore(tmp_path)
    result = run_population(USER_ACCESS_SOD, store, _llm_for(tmp_path))

    assert {uo.uid: uo.verdict.outcome for uo in result.per_user} == {
        "14": Outcome.EXCEPTION, "15": Outcome.UNVERIFIABLE,
        "16": Outcome.EXCEPTION, "17": Outcome.PASS}
    assert result.summary == {"tested": 4, "passes": 1, "exceptions": 2, "escalations": 1}

    report = population_replay(result.log, store, default_registry(), USER_ACCESS_SOD, result.seal)
    assert report.ok is True
    assert (report.integrity, report.grounding, report.derivation) == (True, True, True)
    assert report.summary == result.summary

    # the population working paper renders the whole result without reverse-engineering
    md = render_population_summary(USER_ACCESS_SOD, result)
    assert "Population tested: 4" in md
