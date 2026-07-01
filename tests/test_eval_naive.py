import json
from attestable.types import Outcome
from attestable.controls.user_access_sod import USER_ACCESS_SOD
from attestable.eval.naive import run_naive

class Scripted:
    def __init__(self, payload): self.payload = payload
    def complete(self, prompt): return self.payload

def _cur(val):
    return {"claim": "current_entitlements", "value": val,
            "citation": {"kind": "cell", "doc": "x.xlsx", "sheet": "Users", "cell": "C2"}}

def _app(val):
    return {"claim": "approved_entitlements", "value": val,
            "citation": {"kind": "span", "doc": "a.txt", "start": 0, "end": len(val), "quote": val}}

def test_naive_optimistic_pass_when_approval_missing():
    llm = Scripted(json.dumps([_cur("payment_creator;admin")]))  # no approved fact
    v = run_naive(USER_ACCESS_SOD, store=None, sample_id="u", llm=llm)
    assert v.outcome is Outcome.PASS  # naive never abstains

def test_naive_accepts_unfaithful_fact_without_checking_source():
    llm = Scripted(json.dumps([_cur("payment_creator;admin"), _app("payment_creator;admin")]))
    v = run_naive(USER_ACCESS_SOD, store=None, sample_id="u", llm=llm)
    assert v.outcome is Outcome.PASS  # current subset of the (unchecked) approved -> pass

def test_naive_still_flags_a_clean_sod_conflict():
    llm = Scripted(json.dumps([_cur("payment_creator;payment_approver"),
                               _app("payment_creator;payment_approver")]))
    v = run_naive(USER_ACCESS_SOD, store=None, sample_id="u", llm=llm)
    assert v.outcome is Outcome.EXCEPTION
