from attestable.types import Outcome, Assertion, VerifiedFact, CellRef
from attestable.controls.user_access_sod import USER_ACCESS_SOD

def _vf(key, value):
    return VerifiedFact(Assertion(key, value, CellRef("d", "s", "A1")), value)

def test_rule_flags_sod_conflict():
    verified = {
        "current_entitlements": _vf("current_entitlements", "payment_creator;payment_approver"),
        "approved_entitlements": _vf("approved_entitlements", "payment_creator;payment_approver"),
    }
    outcome, narrative = USER_ACCESS_SOD.rule(verified)
    assert outcome is Outcome.EXCEPTION and "segregation" in narrative.lower()

def test_rule_flags_access_exceeding_approval():
    verified = {
        "current_entitlements": _vf("current_entitlements", "payment_creator;reporting"),
        "approved_entitlements": _vf("approved_entitlements", "payment_creator"),
    }
    outcome, narrative = USER_ACCESS_SOD.rule(verified)
    assert outcome is Outcome.EXCEPTION and "exceed" in narrative.lower()

def test_rule_passes_when_within_approval_and_no_conflict():
    verified = {
        "current_entitlements": _vf("current_entitlements", "payment_creator"),
        "approved_entitlements": _vf("approved_entitlements", "payment_creator;reporting"),
    }
    outcome, _ = USER_ACCESS_SOD.rule(verified)
    assert outcome is Outcome.PASS
