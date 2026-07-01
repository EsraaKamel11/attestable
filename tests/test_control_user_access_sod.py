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

def test_approval_status_readable_unreadable_absent(tmp_path):
    from attestable.evidence import EvidenceStore
    (tmp_path / "approvals.txt").write_text(
        "# approvals_complete: true\n"
        "Approval 1: user 14 approved entitlements: payment_creator\n"
        "Approval 2: user 15 approved entitlements: \n",
        encoding="utf-8")
    store = EvidenceStore(tmp_path)
    assert USER_ACCESS_SOD.approval_status(store, "14") == "readable"
    assert USER_ACCESS_SOD.approval_status(store, "15") == "unreadable"
    assert USER_ACCESS_SOD.approval_status(store, "99") == "absent"

def test_corpus_complete_marker(tmp_path):
    from attestable.evidence import EvidenceStore
    (tmp_path / "approvals.txt").write_text("# approvals_complete: true\n", encoding="utf-8")
    assert USER_ACCESS_SOD.corpus_complete(EvidenceStore(tmp_path)) is True
    (tmp_path / "approvals.txt").write_text("nothing here\n", encoding="utf-8")
    assert USER_ACCESS_SOD.corpus_complete(EvidenceStore(tmp_path)) is False
