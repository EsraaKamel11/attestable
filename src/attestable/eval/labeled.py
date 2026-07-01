import json
from dataclasses import dataclass
from pathlib import Path
import openpyxl
from ..types import Outcome


@dataclass(frozen=True)
class Sample:
    uid: str
    current: str          # the real current entitlements (the cell's true value)
    approved: str | None  # the value the LLM asserts for approved; None means it is omitted
    gold: Outcome
    determinable: bool     # could a faithful agent decide this without abstaining?
    faithful: bool         # is the scripted approved fact faithful to its cited source?


# The real approved text per user, written into approvals.txt (SOURCE OF TRUTH the gate checks).
# None = no approval line (absent); "" = present-but-blank field (unreadable).
_REAL_APPROVED: dict[str, str | None] = {
    "20": "payment_creator;reporting", "21": "reporting;viewer", "22": "viewer",
    "23": "payment_creator;reporting;admin", "24": "payment_creator;payment_approver",
    "25": "payment_creator", "26": None, "27": "", "28": "",
    "29": "payment_creator", "30": "reporting", "31": "payment_creator;reporting",
}

# In spreadsheet-row order: sample i -> row i+2 -> cell C{i+2}.
LABELED_SAMPLES: list[Sample] = [
    Sample("20", "payment_creator",                "payment_creator;reporting",       Outcome.PASS,         True,  True),
    Sample("21", "reporting",                      "reporting;viewer",                Outcome.PASS,         True,  True),
    Sample("22", "viewer",                         "viewer",                          Outcome.PASS,         True,  True),
    Sample("23", "payment_creator;reporting",      "payment_creator;reporting;admin", Outcome.PASS,         True,  True),
    Sample("24", "payment_creator;payment_approver","payment_creator;payment_approver",Outcome.EXCEPTION,   True,  True),
    Sample("25", "payment_creator;admin",          "payment_creator",                 Outcome.EXCEPTION,    True,  True),
    Sample("26", "payment_creator",                None,                              Outcome.EXCEPTION,    True,  True),
    Sample("27", "payment_creator",                None,                              Outcome.UNVERIFIABLE, False, True),
    Sample("28", "payment_creator",                None,                              Outcome.UNVERIFIABLE, False, True),
    Sample("29", "payment_creator;admin",          "payment_creator;admin",           Outcome.EXCEPTION,    False, False),
    Sample("30", "reporting;admin",                "reporting;admin",                 Outcome.EXCEPTION,    False, False),
    Sample("31", "payment_creator",                "payment_creator;reporting",       Outcome.PASS,         True,  True),
]


def build_labeled_scenario(root: Path) -> None:
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Users"
    ws.append(["user_id", "name", "entitlements"])
    for s in LABELED_SAMPLES:
        ws.append([s.uid, "User " + s.uid, s.current])
    wb.save(root / "access_export.xlsx")
    lines = ["# approvals_complete: true"]
    for s in LABELED_SAMPLES:
        real = _REAL_APPROVED[s.uid]
        if real is None:
            continue  # absent: no approval line for this user
        lines.append(f"Approval {s.uid}: user {s.uid} approved entitlements: {real}")
    (root / "approvals.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def scripted_payload(store, index: int, sample: Sample) -> str:
    cell = f"C{index + 2}"
    facts = [{"claim": "current_entitlements", "value": sample.current,
              "citation": {"kind": "cell", "doc": "access_export.xlsx", "sheet": "Users", "cell": cell}}]
    if sample.approved is not None:
        text = store.text("approvals.txt")
        real = _REAL_APPROVED[sample.uid] or ""
        marker = f"user {sample.uid} approved entitlements: "
        mi = text.find(marker)
        assert mi >= 0, f"no approval line found for user {sample.uid}"
        start = mi + len(marker) if mi >= 0 else 0
        end = start + len(real)
        quote = text[start:end] if mi >= 0 else sample.approved
        facts.append({"claim": "approved_entitlements", "value": sample.approved,
                      "citation": {"kind": "span", "doc": "approvals.txt", "start": start, "end": end, "quote": quote}})
    return json.dumps(facts)
