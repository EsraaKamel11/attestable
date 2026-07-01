from attestable.types import Outcome, CellRef, TextSpan, Assertion, VerifiedFact, Verdict

def test_citation_variants_and_assertion():
    c = CellRef(doc="access_export.xlsx", sheet="Users", cell="C14")
    a = Assertion(claim="user 14 role", value="payments_admin", citation=c)
    assert a.citation.cell == "C14"
    s = TextSpan(doc="approvals.txt", start=10, end=25, quote="read_only")
    assert s.quote == "read_only"

def test_verdict_holds_outcome():
    v = Verdict(outcome=Outcome.EXCEPTION, verified=[], unmet=["approval"], narrative="n")
    assert v.outcome is Outcome.EXCEPTION
    assert v.unmet == ["approval"]
