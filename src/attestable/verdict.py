from .types import Outcome, Verdict, VerifiedFact
from .controls.definition import ControlDefinition
from .evidence import EvidenceStore


def decide(control: ControlDefinition, verified: list[VerifiedFact], sample_id: str,
           store: EvidenceStore) -> Verdict:
    by_key = {vf.assertion.claim: vf for vf in verified}
    missing = [k for k in control.required_keys if k not in by_key]

    if not missing:
        outcome, narrative = control.rule(by_key)
        return Verdict(outcome=outcome, verified=verified, unmet=[], narrative=narrative)

    if "current_entitlements" in missing:
        return Verdict(Outcome.UNVERIFIABLE, verified, missing,
                       "Cannot test: current entitlements could not be verified.")

    # only approved_entitlements is missing -> apply the boundary
    status = control.approval_status(store, sample_id)
    if status == "unreadable":
        return Verdict(Outcome.UNVERIFIABLE, verified, missing,
                       "Approval record present but its approved-access field is unreadable.")
    if status == "absent":
        if control.corpus_complete(store):
            return Verdict(Outcome.EXCEPTION, verified, missing,
                           "No approval for a bounded, complete approvals set: access is unapproved.")
        return Verdict(Outcome.UNVERIFIABLE, verified, missing,
                       "No approval found, but the approvals corpus is not established as complete.")
    return Verdict(Outcome.UNVERIFIABLE, verified, missing,
                   "Approval readable but not extracted; treat as indeterminate.")
