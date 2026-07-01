from attestable.escalation import EscalationQueue


def test_enqueue_survives_reopen(tmp_path):
    path = tmp_path / "queue.jsonl"
    EscalationQueue(path).enqueue({"sample_id": "15", "reason": "unreadable approval"})
    # a fresh instance on the same path (simulating a restart) still sees it
    pending = EscalationQueue(path).pending()
    assert pending == [{"sample_id": "15", "reason": "unreadable approval"}]
