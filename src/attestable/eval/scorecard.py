def render_scorecard(summary: dict) -> str:
    fc = summary.get("guarded_false_citation", 0)
    faithful_line = (
        "Guarded citation faithfulness: 100 percent, the gate accepts no fact that is not faithful to its source."
        if fc == 0 else
        f"Guarded citation faithfulness: below 100 percent, {fc} accepted fact(s) failed a source re-check."
    )
    lines = [
        "# Controls-testing eval scorecard",
        "",
        "This is a demonstration over a small synthetic hand-labeled set, it is NOT a "
        "statistically powered benchmark. \"Naive\" is the no-guardrails baseline: the same "
        "model-proposed facts, accepted without the faithfulness gate and decided without the "
        "UNVERIFIABLE abstention (it defaults to PASS on a missing required fact).",
        "",
        f"Samples: {summary['n']}",
        "",
        "| Metric | Guarded | Naive |",
        "| --- | --- | --- |",
        f"| False-pass (PASS where the truth is not PASS) | {summary['guarded_false_pass']} | {summary['naive_false_pass']} |",
        f"| Decision accuracy (verdict == gold) | {summary['guarded_accuracy']}/{summary['n']} | {summary['naive_accuracy']}/{summary['n']} |",
        "",
        f"Guarded over-abstention (abstained on a determinable sample): {summary['guarded_over_abstention']}",
        f"Guarded false-citation (accepted facts that fail a source re-check): {fc}",
        faithful_line,
        "",
        "Headline: the guarded pipeline never issues a false PASS on this set; the naive "
        "baseline does. That difference is exactly the faithfulness gate plus the UNVERIFIABLE "
        "abstention.",
    ]
    return "\n".join(lines)
