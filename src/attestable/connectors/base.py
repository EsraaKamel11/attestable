import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol


def content_hash(data: bytes) -> str:
    """sha256 hex of the exact evidence bytes, computed once at fetch time."""
    return hashlib.sha256(data).hexdigest()


@dataclass(frozen=True)
class Provenance:
    doc: str        # the materialized evidence file this describes
    method: str     # "api" (browser fallback is designed-not-built this slice)
    locator: str    # how it was obtained, e.g. "GET /users/14/access"
    content_hash: str  # sha256 of the doc's bytes at fetch


@dataclass
class FetchResult:
    root: Path
    provenance: list[Provenance] = field(default_factory=list)


class Connector(Protocol):
    def fetch(self, query: str, root: Path) -> FetchResult: ...
