from pathlib import Path
import openpyxl
from .types import Citation, CellRef, TextSpan


class EvidenceStore:
    def __init__(self, root: Path):
        self.root = Path(root)
        self._text_cache: dict[str, str] = {}
        self._wb_cache: dict[str, openpyxl.Workbook] = {}

    def text(self, doc: str) -> str:
        if doc not in self._text_cache:
            path = self.root / doc
            self._text_cache[doc] = path.read_text(encoding="utf-8") if path.exists() else ""
        return self._text_cache[doc]

    def resolve(self, citation: Citation) -> str | None:
        if isinstance(citation, CellRef):
            return self._resolve_cell(citation)
        if isinstance(citation, TextSpan):
            return self._resolve_span(citation)
        return None

    def _resolve_cell(self, ref: CellRef) -> str | None:
        path = self.root / ref.doc
        if not path.exists():
            return None
        if ref.doc not in self._wb_cache:
            self._wb_cache[ref.doc] = openpyxl.load_workbook(path, data_only=True)
        wb = self._wb_cache[ref.doc]
        if ref.sheet not in wb.sheetnames:
            return None
        value = wb[ref.sheet][ref.cell].value
        return None if value is None else str(value)

    def _resolve_span(self, span: TextSpan) -> str | None:
        text = self.text(span.doc)
        if span.start < 0 or span.end > len(text) or span.start >= span.end:
            return None
        return text[span.start:span.end]
