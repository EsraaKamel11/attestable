# tests/test_eval_labeled.py
from pathlib import Path
from attestable.types import Outcome
from attestable.eval.labeled import build_labeled_scenario, LABELED_SAMPLES, scripted_payload
from attestable.evidence import EvidenceStore

def test_labeled_set_is_balanced_and_built(tmp_path: Path):
    build_labeled_scenario(tmp_path)
    assert (tmp_path / "access_export.xlsx").exists()
    assert (tmp_path / "approvals.txt").exists()
    assert len(LABELED_SAMPLES) == 12
    golds = {s.gold for s in LABELED_SAMPLES}
    assert golds == {Outcome.PASS, Outcome.EXCEPTION, Outcome.UNVERIFIABLE}

def test_scripted_current_cell_resolves_faithfully(tmp_path: Path):
    build_labeled_scenario(tmp_path)
    store = EvidenceStore(tmp_path)
    # sample 0 is written to row 2 (cell C2); its current value must resolve there
    from attestable.types import CellRef
    assert store.resolve(CellRef("access_export.xlsx", "Users", "C2")) == LABELED_SAMPLES[0].current
    payload = scripted_payload(store, 0, LABELED_SAMPLES[0])
    assert '"C2"' in payload and '"current_entitlements"' in payload
