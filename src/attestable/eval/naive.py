from ..types import Outcome, Verdict, VerifiedFact
from ..extract import extract_facts
from ..controls.definition import ControlDefinition


def run_naive(control: ControlDefinition, store, sample_id: str, llm, manifest: str = "") -> Verdict:
    """The no-guardrails baseline: accept every proposed fact WITHOUT the faithfulness
    gate, and decide WITHOUT the UNVERIFIABLE abstention (optimistic PASS on a missing
    required fact). This exists only to quantify what the trust core buys."""
    proposed = extract_facts(control.required_keys, manifest, llm)
    accepted = [VerifiedFact(a, a.value) for a in proposed]  # trust the model's value, no source check
    by_key = {vf.assertion.claim: vf for vf in accepted}
    missing = [k for k in control.required_keys if k not in by_key]
    if not missing:
        outcome, narrative = control.rule(by_key)
        return Verdict(outcome, accepted, [], "naive: " + narrative)
    return Verdict(Outcome.PASS, accepted, missing,
                   "naive: assumed PASS despite missing " + ", ".join(missing))
