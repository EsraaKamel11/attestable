# tests/test_eval_scorecard.py
from pathlib import Path
from attestable.eval.run_eval import run_eval
from attestable.eval.scorecard import render_scorecard

def test_run_eval_headline_numbers(tmp_path: Path):
    result = run_eval(tmp_path)
    s = result["summary"]
    assert s["n"] == 12
    assert s["guarded_false_pass"] == 0          # the headline
    assert s["naive_false_pass"] >= 3            # the contrast is real
    assert s["guarded_over_abstention"] == 0
    assert s["guarded_false_citation"] == 0      # the gate accepts nothing unfaithful
    assert (tmp_path / "scorecard.json").exists() and (tmp_path / "scorecard.md").exists()

def test_scorecard_states_the_honest_boundary():
    md = render_scorecard({"n": 12, "guarded_false_pass": 0, "naive_false_pass": 5,
                           "guarded_accuracy": 10, "naive_accuracy": 7,
                           "guarded_over_abstention": 0, "guarded_false_citation": 0})
    assert "demonstration" in md.lower() and "not a" in md.lower()
    assert "false-pass" in md.lower()
    assert "—" not in md  # em-dash-free
