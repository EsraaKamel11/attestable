from dataclasses import dataclass
from .types import Outcome, Verdict
from .evidence import EvidenceStore
from .predicates import PredicateRegistry, default_registry
from .gate import verify_assertion
from .extract import extract_facts
from .verdict import decide
from .audit.log import AuditLog
from .serial import citation_to_dict
from .workpaper import render_workpaper
from .controls.definition import ControlDefinition


@dataclass
class RunResult:
    sample_id: str
    verdict: Verdict
    seal: str
    workpaper: str


def run_control(control: ControlDefinition, store: EvidenceStore, sample_id: str, llm,
                registry: PredicateRegistry | None = None, log: AuditLog | None = None,
                queue=None, manifest: str = "") -> RunResult:
    registry = registry or default_registry()
    log = log or AuditLog()
    verified = []
    for a in extract_facts(control.required_keys, manifest, llm):
        res = verify_assertion(a, store, registry)
        if res.ok:
            log.append("gate", "fact.accepted",
                       {"claim": a.claim, "value": a.value, "citation": citation_to_dict(a.citation)})
            verified.append(res.fact)
        else:
            log.append("gate", "fact.rejected",
                       {"claim": a.claim, "reason": res.reason, "citation": citation_to_dict(a.citation)})
    v = decide(control, verified, sample_id, store)
    log.append("verdict", "verdict", {"outcome": v.outcome.value, "narrative": v.narrative, "unmet": v.unmet})
    if v.outcome is Outcome.UNVERIFIABLE and queue is not None:
        queue.enqueue({"sample_id": sample_id, "reason": v.narrative, "unmet": v.unmet})
    return RunResult(sample_id, v, log.seal(), render_workpaper(control.name, sample_id, v))
