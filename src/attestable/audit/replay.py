import hashlib
from dataclasses import dataclass
from .canonical import canonical_bytes
from .log import GENESIS
from ..types import Assertion
from ..serial import citation_from_dict
from ..gate import verify_assertion
from ..verdict import decide


@dataclass
class ReplayReport:
    integrity: bool
    grounding: bool
    derivation: bool

    @property
    def ok(self) -> bool:
        return self.integrity and self.grounding and self.derivation


def _recompute(entry: dict) -> str:
    content = {k: entry[k] for k in ("seq", "actor", "action", "payload", "prev_hash")}
    return hashlib.sha256(canonical_bytes(content)).hexdigest()


def _check_integrity(log) -> bool:
    prev = GENESIS
    for e in log.entries:
        if e["prev_hash"] != prev or _recompute(e) != e["entry_hash"]:
            return False
        prev = e["entry_hash"]
    return True


def audit_replay(log, store, registry, control, sample_id: str) -> ReplayReport:
    integrity = _check_integrity(log)
    verified, grounding = [], True
    for e in log.entries:
        if e["action"] == "fact.accepted":
            p = e["payload"]
            a = Assertion(p["claim"], p["value"], citation_from_dict(p["citation"]))
            res = verify_assertion(a, store, registry)
            if res.ok:
                verified.append(res.fact)
            else:
                grounding = False
    logged = [e for e in log.entries if e["action"] == "verdict"]
    derivation = True
    if logged:
        derivation = decide(control, verified, sample_id, store).outcome.value == logged[-1]["payload"]["outcome"]
    return ReplayReport(integrity, grounding, derivation)
