from attestable.scenarios.build_scenarios import build_scenarios
from attestable.evidence import EvidenceStore
from attestable.population import read_population


def test_read_population_returns_all_user_ids_in_order(tmp_path):
    build_scenarios(tmp_path)
    store = EvidenceStore(tmp_path)
    assert read_population(store) == ["14", "15", "16", "17"]
