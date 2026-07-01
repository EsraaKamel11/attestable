import json
from dataclasses import is_dataclass, asdict
from enum import Enum

CANON_VERSION = "cbor-json/1"


def _prepare(obj):
    if isinstance(obj, Enum):
        return obj.value
    if is_dataclass(obj) and not isinstance(obj, type):
        return {k: _prepare(v) for k, v in asdict(obj).items()}
    if isinstance(obj, dict):
        return {k: _prepare(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_prepare(v) for v in obj]
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    raise TypeError(f"non-canonicalizable type: {type(obj).__name__}")


def canonical_bytes(obj) -> bytes:
    body = json.dumps(_prepare(obj), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return CANON_VERSION.encode("utf-8") + b"\n" + body.encode("utf-8")
