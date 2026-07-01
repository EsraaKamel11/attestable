from pathlib import Path
import openpyxl


def build_scenarios(root: Path) -> None:
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Users"
    ws.append(["user_id", "name", "entitlements"])
    ws.append(["14", "Sam Lee", "payment_creator;payment_approver"])
    ws.append(["15", "Ada Ng", "payment_creator"])
    ws.append(["16", "Ravi Rao", "payment_creator"])
    ws.append(["17", "Jo Kim", "payment_creator"])
    wb.save(root / "access_export.xlsx")
    (root / "approvals.txt").write_text(
        "# approvals_complete: true\n"
        "Approval 1041: user 14 approved entitlements: payment_creator;payment_approver\n"
        "Approval 1042: user 15 approved entitlements: \n"
        "Approval 1044: user 17 approved entitlements: payment_creator;reporting\n",
        encoding="utf-8",
    )
    (root / "sod_policy.txt").write_text(
        "Segregation of duties: holding both payment_creator and payment_approver is a conflict.\n",
        encoding="utf-8",
    )
