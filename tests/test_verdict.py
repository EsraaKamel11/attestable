from attestable.types import Outcome, Assertion, VerifiedFact, CellRef
from attestable.controls.definition import ControlDefinition
from attestable.verdict import decide

def _vf(key, value):
    return VerifiedFact(Assertion(key, value, CellRef("d", "s", "A1")), value)

def _control(status="readable", complete=True):
    return ControlDefinition(
        name="t", required_keys=["current_entitlements", "approved_entitlements"],
        rule=lambda v: (Outcome.PASS, "ok"),
        approval_status=lambda store, sid: status,
        corpus_complete=lambda store: complete,
    )

def test_all_verified_applies_rule():
    v = [_vf("current_entitlements", "payment_creator"), _vf("approved_entitlements", "payment_creator")]
    assert decide(_control(), v, "14", store=None).outcome is Outcome.PASS

def test_unreadable_approval_is_unverifiable():
    v = [_vf("current_entitlements", "payment_creator")]
    out = decide(_control(status="unreadable"), v, "15", store=None)
    assert out.outcome is Outcome.UNVERIFIABLE and "unreadable" in out.narrative.lower()

def test_absent_approval_with_complete_corpus_is_exception():
    v = [_vf("current_entitlements", "payment_creator")]
    out = decide(_control(status="absent", complete=True), v, "16", store=None)
    assert out.outcome is Outcome.EXCEPTION

def test_absent_approval_with_incomplete_corpus_is_unverifiable():
    v = [_vf("current_entitlements", "payment_creator")]
    out = decide(_control(status="absent", complete=False), v, "16", store=None)
    assert out.outcome is Outcome.UNVERIFIABLE and "complete" in out.narrative.lower()

def test_missing_current_entitlements_is_unverifiable():
    out = decide(_control(), [], "14", store=None)
    assert out.outcome is Outcome.UNVERIFIABLE
