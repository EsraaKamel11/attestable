from attestable.types import Outcome, Assertion, VerifiedFact, CellRef, Verdict
from attestable.workpaper import render_workpaper

def test_workpaper_shows_verdict_facts_and_citations():
    vf = VerifiedFact(Assertion("current_entitlements", "payment_creator;payment_approver",
                                CellRef("access_export.xlsx", "Users", "C2")), "payment_creator;payment_approver")
    v = Verdict(Outcome.EXCEPTION, [vf], [], "Segregation-of-duties conflict.")
    md = render_workpaper("user-access-review-sod", "14", v)
    assert "EXCEPTION" in md
    assert "current_entitlements = payment_creator;payment_approver" in md
    assert "access_export.xlsx!Users!C2" in md
    assert "Segregation-of-duties conflict." in md
    assert "—" not in md  # no em-dash
