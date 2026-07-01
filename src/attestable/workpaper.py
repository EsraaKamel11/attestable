from .types import Verdict, VerifiedFact, CellRef, TextSpan


def _cite_ref(fact: VerifiedFact) -> str:
    c = fact.assertion.citation
    if isinstance(c, CellRef):
        return f"{c.doc}!{c.sheet}!{c.cell}"
    if isinstance(c, TextSpan):
        return f"{c.doc}@{c.start}:{c.end}"
    return "unknown"


def render_workpaper(control_name: str, sample_id: str, verdict: Verdict) -> str:
    lines = [
        f"# Working paper: {control_name}",
        f"Sample: {sample_id}",
        f"Outcome: {verdict.outcome.name}",
        "",
        "## Verified facts",
    ]
    for fact in verdict.verified:
        lines.append(f"- {fact.assertion.claim} = {fact.assertion.value}  [source: {_cite_ref(fact)}]")
    if verdict.unmet:
        lines += ["", "## Unmet requirements", *[f"- {u}" for u in verdict.unmet]]
    lines += ["", "## Narrative", verdict.narrative]
    return "\n".join(lines)
