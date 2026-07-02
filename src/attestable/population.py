import openpyxl
from .evidence import EvidenceStore


def read_population(store: EvidenceStore) -> list[str]:
    """Every user id in the access export (column A, row 2 onward), in sheet order."""
    wb = openpyxl.load_workbook(store.root / "access_export.xlsx", data_only=True)
    ws = wb["Users"]
    ids = []
    for row in ws.iter_rows(min_row=2, max_col=1, values_only=True):
        if row[0] is not None:
            ids.append(str(row[0]))
    return ids
