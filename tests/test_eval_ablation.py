"""CI gate: the guarded pipeline has a false-pass rate of 0 on the labeled set,
the naive baseline does not, the guarded pipeline never over-abstains on a
determinable sample, and it accepts no unfaithful fact. This is the with-vs-without ablation."""
from attestable.eval.run_eval import run_eval

def test_guarded_false_pass_is_zero_and_naive_is_not(tmp_path):
    s = run_eval(tmp_path)["summary"]
    assert s["n"] == 12
    assert s["guarded_false_pass"] == 0, "REGRESSION: the guarded pipeline issued a false PASS"
    assert s["naive_false_pass"] >= 3, "the ablation is vacuous if the naive baseline never false-passes"
    assert s["guarded_over_abstention"] == 0
    assert s["guarded_false_citation"] == 0
    assert s["guarded_accuracy"] >= s["naive_accuracy"]
