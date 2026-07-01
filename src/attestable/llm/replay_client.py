import json
from pathlib import Path
from .client import request_hash


class ReplayClient:
    def __init__(self, fixtures_dir: Path):
        self.fixtures_dir = Path(fixtures_dir)

    def complete(self, prompt: str) -> str:
        path = self.fixtures_dir / f"{request_hash(prompt)}.json"
        if not path.exists():
            raise KeyError(f"no recorded response for prompt hash {path.stem}")
        return json.loads(path.read_text(encoding="utf-8"))["response"]
