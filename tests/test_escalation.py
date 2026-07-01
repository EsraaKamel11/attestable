from attestable.escalation import EscalationQueue


def test_enqueue_survives_reopen(tmp_path):
    path = tmp_path / "queue.jsonl"
    EscalationQueue(path).enqueue({"sample_id": "15", "reason": "unreadable approval"})
    # a fresh instance on the same path (simulating a restart) still sees it
    pending = EscalationQueue(path).pending()
    assert pending == [{"sample_id": "15", "reason": "unreadable approval"}]


def test_pending_missing_file_is_empty(tmp_path):
    assert EscalationQueue(tmp_path / "none.jsonl").pending() == []


def test_multi_enqueue_accumulates(tmp_path):
    q = EscalationQueue(tmp_path / "queue.jsonl")
    q.enqueue({"id": "1"})
    q.enqueue({"id": "2"})
    assert q.pending() == [{"id": "1"}, {"id": "2"}]
