import json
from attestable.llm.client import request_hash
from attestable.llm.replay_client import ReplayClient


def test_replay_returns_recorded_response(tmp_path):
    prompt = "extract facts for user 14"
    (tmp_path / f"{request_hash(prompt)}.json").write_text(
        json.dumps({"prompt": prompt, "response": "RECORDED"}), encoding="utf-8"
    )
    assert ReplayClient(tmp_path).complete(prompt) == "RECORDED"


def test_replay_miss_raises(tmp_path):
    import pytest
    with pytest.raises(KeyError):
        ReplayClient(tmp_path).complete("never recorded")
