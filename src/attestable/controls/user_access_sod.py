from ..types import Outcome, VerifiedFact
from ..evidence import EvidenceStore
from .definition import ControlDefinition

SOD_PAIR = ("payment_creator", "payment_approver")


def _entitlements(value: str) -> set[str]:
    return {e.strip() for e in value.split(";") if e.strip()}


def _rule(verified: dict[str, VerifiedFact]) -> tuple[Outcome, str]:
    current = _entitlements(verified["current_entitlements"].resolved)
    approved = _entitlements(verified["approved_entitlements"].resolved)
    if set(SOD_PAIR) <= current:
        return Outcome.EXCEPTION, (
            "Segregation-of-duties conflict: user holds both "
            f"{SOD_PAIR[0]} and {SOD_PAIR[1]}."
        )
    extra = current - approved
    if extra:
        return Outcome.EXCEPTION, f"Access exceeds approval: {sorted(extra)} not approved."
    return Outcome.PASS, "Access is within approval and no SoD conflict."


def _approval_status(store: EvidenceStore, sample_id: str) -> str:
    text = store.text("approvals.txt")
    for line in text.splitlines():
        if f"user {sample_id} " in line and "approved entitlements:" in line:
            field = line.split("approved entitlements:", 1)[1].strip()
            return "readable" if field else "unreadable"
    return "absent"


def _corpus_complete(store: EvidenceStore) -> bool:
    return "approvals_complete: true" in store.text("approvals.txt").lower()


USER_ACCESS_SOD = ControlDefinition(
    name="user-access-review-sod",
    required_keys=["current_entitlements", "approved_entitlements"],
    rule=_rule,
    approval_status=_approval_status,
    corpus_complete=_corpus_complete,
)
