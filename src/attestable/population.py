import openpyxl
from dataclasses import dataclass
from .evidence import EvidenceStore
from .types import Outcome, Verdict
from .audit.log import AuditLog
from .pipeline import run_control


def read_population(store: EvidenceStore) -> list[str]:
    """Every user id in the access export (column A, row 2 onward), in sheet order."""
    wb = openpyxl.load_workbook(store.root / "access_export.xlsx", data_only=True)
    ws = wb["Users"]
    ids = []
    for row in ws.iter_rows(min_row=2, max_col=1, values_only=True):
        if row[0] is not None:
            ids.append(str(row[0]))
    return ids


@dataclass
class UserOutcome:
    uid: str
    verdict: Verdict
    workpaper: str


@dataclass
class PopulationResult:
    per_user: list
    summary: dict
    seal: str
    log: AuditLog


def _summarize(per_user: list) -> dict:
    outs = [uo.verdict.outcome for uo in per_user]
    return {
        "tested": len(outs),
        "passes": sum(1 for o in outs if o is Outcome.PASS),
        "exceptions": sum(1 for o in outs if o is Outcome.EXCEPTION),
        "escalations": sum(1 for o in outs if o is Outcome.UNVERIFIABLE),
    }


def run_population(control, store, llm_for, registry=None, queue=None) -> PopulationResult:
    """Apply the per-record control across the whole population, under one shared audit log
    sealed once. A hash-chained sample.begin marker precedes each user's run so the chain
    can be segmented per user at replay. run_control is unchanged."""
    log = AuditLog()
    per_user = []
    for uid in read_population(store):
        log.append("population", "sample.begin", {"sample_id": uid})
        rr = run_control(control, store, uid, llm_for(uid), registry, log=log, queue=queue)
        per_user.append(UserOutcome(uid, rr.verdict, rr.workpaper))
    return PopulationResult(per_user, _summarize(per_user), log.seal(), log)


from .serial import citation_from_dict
from .gate import verify_assertion
from .verdict import decide
from .audit.replay import _check_integrity
from .types import Assertion


@dataclass
class PopulationReplayReport:
    integrity: bool
    grounding: bool
    derivation: bool
    summary: dict

    @property
    def ok(self) -> bool:
        return self.integrity and self.grounding and self.derivation


def _segments(log):
    """Split the shared chain into one segment per user at each sample.begin marker."""
    segs, cur = [], None
    for e in log.entries:
        if e["action"] == "sample.begin":
            cur = {"uid": e["payload"]["sample_id"], "facts": [], "verdict": None}
            segs.append(cur)
        elif cur is None:
            continue
        elif e["action"] == "fact.accepted":
            cur["facts"].append(e["payload"])
        elif e["action"] == "verdict":
            cur["verdict"] = e["payload"]
    return segs


def population_replay(log, store, registry, control, expected_seal) -> PopulationReplayReport:
    integrity = _check_integrity(log) and (log.seal() == expected_seal)
    grounding, derivation = True, True
    counts = {"tested": 0, "passes": 0, "exceptions": 0, "escalations": 0}
    bucket = {"pass": "passes", "exception": "exceptions", "unverifiable": "escalations"}
    for seg in _segments(log):
        counts["tested"] += 1
        verified = []
        for p in seg["facts"]:
            a = Assertion(p["claim"], p["value"], citation_from_dict(p["citation"]))
            res = verify_assertion(a, store, registry)
            if res.ok:
                verified.append(res.fact)
            else:
                grounding = False
        if seg["verdict"] is None:
            derivation = False
            continue
        logged = seg["verdict"]["outcome"]
        if decide(control, verified, seg["uid"], store).outcome.value != logged:
            derivation = False
        if logged in bucket:
            counts[bucket[logged]] += 1
    return PopulationReplayReport(integrity, grounding, derivation, counts)
