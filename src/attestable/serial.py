from .types import Citation, CellRef, TextSpan


def citation_to_dict(c: Citation) -> dict:
    if isinstance(c, CellRef):
        return {"kind": "cell", "doc": c.doc, "sheet": c.sheet, "cell": c.cell}
    elif isinstance(c, TextSpan):
        return {"kind": "span", "doc": c.doc, "start": c.start, "end": c.end, "quote": c.quote}
    else:
        raise TypeError(f"unknown citation type {type(c).__name__}")


def citation_from_dict(d: dict) -> Citation:
    if d["kind"] == "cell":
        return CellRef(d["doc"], d["sheet"], d["cell"])
    if d["kind"] == "span":
        return TextSpan(d["doc"], int(d["start"]), int(d["end"]), d["quote"])
    raise ValueError(f"unknown citation kind {d['kind']!r}")
