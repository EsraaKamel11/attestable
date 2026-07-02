# src/attestable/connectors/orchestrate.py
from pathlib import Path
from ..audit.log import AuditLog
from ..evidence import EvidenceStore
from ..pipeline import run_control


def run_with_connector(connector, query: str, control, sample_id: str, llm, root: Path,
                       registry=None, return_log: bool = False):
    """Acquire evidence through the connector, log the acquisition into the SAME audit
    log before extraction, then run the unchanged pipeline. Chain: acquire -> fact.accepted -> verdict."""
    log = AuditLog()
    fetch = connector.fetch(query, root)
    for p in fetch.provenance:
        log.append("connector", "evidence.acquired",
                   {"doc": p.doc, "method": p.method, "locator": p.locator, "content_hash": p.content_hash})
    store = EvidenceStore(fetch.root)
    result = run_control(control, store, sample_id, llm, registry, log=log)
    if return_log:
        return result, store, log
    return result, store
