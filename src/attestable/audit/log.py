import copy
import hashlib
import hmac
from dataclasses import dataclass, field
from .canonical import canonical_bytes

GENESIS = "0" * 64


def _entry_hash(content: dict) -> str:
    return hashlib.sha256(canonical_bytes(content)).hexdigest()


@dataclass
class AuditLog:
    entries: list[dict] = field(default_factory=list)

    def append(self, actor: str, action: str, payload: dict) -> dict:
        prev = self.entries[-1]["entry_hash"] if self.entries else GENESIS
        content = {"seq": len(self.entries), "actor": actor, "action": action,
                   "payload": copy.deepcopy(payload), "prev_hash": prev}
        entry = dict(content, entry_hash=_entry_hash(content))
        self.entries.append(entry)
        return copy.deepcopy(entry)

    def seal(self) -> str:
        return self.entries[-1]["entry_hash"] if self.entries else GENESIS

    def signed_seal(self, key: bytes) -> str:
        return hmac.new(key, self.seal().encode("utf-8"), hashlib.sha256).hexdigest()
