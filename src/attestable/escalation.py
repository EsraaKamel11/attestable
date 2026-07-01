import json
from pathlib import Path


class EscalationQueue:
    def __init__(self, path: Path):
        self.path = Path(path)

    def enqueue(self, item: dict) -> None:
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(item, ensure_ascii=False) + "\n")

    def pending(self) -> list[dict]:
        if not self.path.exists():
            return []
        return [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line]
