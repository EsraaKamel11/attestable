from attestable.audit.canonical import canonical_bytes, CANON_VERSION


def test_key_order_independence():
    a = canonical_bytes({"b": 1, "a": 2})
    b = canonical_bytes({"a": 2, "b": 1})
    assert a == b


def test_golden_bytes_are_stable():
    got = canonical_bytes({"seq": 1, "actor": "gate", "value": "read_only"})
    assert got == CANON_VERSION.encode() + b'\n' + b'{"actor":"gate","seq":1,"value":"read_only"}'


def test_nondeterministic_types_rejected():
    import pytest
    with pytest.raises(TypeError):
        canonical_bytes({"t": object()})
