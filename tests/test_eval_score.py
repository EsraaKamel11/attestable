from attestable.types import Outcome
from attestable.eval.score import score

def _row(gold, guarded, naive, determinable=True):
    return {"gold": gold, "guarded": guarded, "naive": naive, "determinable": determinable}

def test_score_counts_false_pass_and_accuracy():
    rows = [
        _row(Outcome.PASS, Outcome.PASS, Outcome.PASS),
        _row(Outcome.EXCEPTION, Outcome.EXCEPTION, Outcome.PASS),        # naive false-pass
        _row(Outcome.UNVERIFIABLE, Outcome.UNVERIFIABLE, Outcome.PASS,   # naive false-pass
             determinable=False),
    ]
    s = score(rows)
    assert s["n"] == 3
    assert s["guarded_false_pass"] == 0
    assert s["naive_false_pass"] == 2
    assert s["guarded_accuracy"] == 3
    assert s["naive_accuracy"] == 1
    assert s["guarded_over_abstention"] == 0

def test_over_abstention_counts_only_determinable_rows():
    rows = [_row(Outcome.EXCEPTION, Outcome.UNVERIFIABLE, Outcome.PASS, determinable=True)]
    assert score(rows)["guarded_over_abstention"] == 1
