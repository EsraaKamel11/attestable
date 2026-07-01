import json
from pathlib import Path
from ..evidence import EvidenceStore
from ..predicates import default_registry
from ..gate import verify_assertion
from ..pipeline import run_control
from ..controls.user_access_sod import USER_ACCESS_SOD
from .naive import run_naive
from .score import score
from .scorecard import render_scorecard
from .labeled import build_labeled_scenario, LABELED_SAMPLES, scripted_payload


class _Scripted:
    def __init__(self, payload): self.payload = payload
    def complete(self, prompt): return self.payload


def run_eval(root: Path) -> dict:
    root = Path(root)
    build_labeled_scenario(root)
    store = EvidenceStore(root)
    reg = default_registry()
    rows = []
    false_citation = 0
    for i, s in enumerate(LABELED_SAMPLES):
        payload = scripted_payload(store, i, s)
        result = run_control(USER_ACCESS_SOD, store, s.uid, _Scripted(payload), reg)
        for vf in result.verdict.verified:  # every accepted fact must re-check as faithful
            if not verify_assertion(vf.assertion, store, reg).ok:
                false_citation += 1
        naive = run_naive(USER_ACCESS_SOD, store, s.uid, _Scripted(payload)).outcome
        rows.append({"gold": s.gold, "guarded": result.verdict.outcome, "naive": naive,
                     "determinable": s.determinable, "faithful": s.faithful, "uid": s.uid})
    summary = score(rows)
    summary["guarded_false_citation"] = false_citation
    (root / "scorecard.json").write_text(json.dumps({
        "summary": summary,
        "rows": [{"uid": r["uid"], "gold": r["gold"].value, "guarded": r["guarded"].value,
                  "naive": r["naive"].value, "determinable": r["determinable"], "faithful": r["faithful"]}
                 for r in rows],
    }, indent=2), encoding="utf-8")
    (root / "scorecard.md").write_text(render_scorecard(summary), encoding="utf-8")
    return {"summary": summary, "rows": rows}
