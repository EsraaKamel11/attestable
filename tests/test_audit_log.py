from attestable.audit.log import AuditLog, GENESIS

def test_chain_links_and_seal():
    log = AuditLog()
    e0 = log.append("gate", "fact.accepted", {"claim": "role", "value": "admin"})
    e1 = log.append("verdict", "verdict", {"outcome": "pass"})
    assert e0["prev_hash"] == GENESIS
    assert e1["prev_hash"] == e0["entry_hash"]
    assert log.seal() == e1["entry_hash"]

def test_hashing_is_deterministic():
    def build():
        lg = AuditLog(); lg.append("a", "x", {"k": 1}); lg.append("b", "y", {"k": 2}); return lg.seal()
    assert build() == build()

def test_signed_seal_differs_from_seal():
    log = AuditLog(); log.append("a", "x", {"k": 1})
    assert log.signed_seal(b"secret") != log.seal()
    assert len(log.signed_seal(b"secret")) == 64


def test_empty_log_seal_is_genesis():
    assert AuditLog().seal() == GENESIS
