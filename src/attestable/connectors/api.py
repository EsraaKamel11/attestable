# src/attestable/connectors/api.py
from pathlib import Path
import openpyxl
from .base import Provenance, FetchResult, content_hash


class ApiConnector:
    """Fetches a user's access record from the SoR API and normalizes it into the
    same evidence forms Slice 1 consumes, so the gate, rule, and citations are unchanged.
    The HTTP client is injected so the identical path runs against a TestClient or a live client."""

    def __init__(self, client):
        self._client = client

    def fetch(self, query: str, root: Path) -> FetchResult:
        root = Path(root)
        root.mkdir(parents=True, exist_ok=True)
        resp = self._client.get(f"/users/{query}/access")
        if resp.status_code != 200:
            raise LookupError(f"SoR returned {resp.status_code} for user {query}")
        rec = resp.json()
        locator = f"GET /users/{query}/access"

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Users"
        ws.append(["user_id", "name", "entitlements"])
        ws.append([rec["user_id"], rec["name"], rec["entitlements"]])
        wb.save(root / "access_export.xlsx")

        (root / "approvals.txt").write_text(
            "# approvals_complete: true\n"
            f"Approval 1: user {query} approved entitlements: {rec['approved']}\n",
            encoding="utf-8",
        )

        prov = [
            Provenance(doc, "api", locator, content_hash((root / doc).read_bytes()))
            for doc in ("access_export.xlsx", "approvals.txt")
        ]
        return FetchResult(root=root, provenance=prov)
