import json
import os
from pathlib import Path
from .client import request_hash


class AnthropicClient:
    """Real client. Used only to record fixtures and to run a live demo. Key from env only."""

    def __init__(self, record_dir: Path | None = None, model: str = "claude-opus-4-8"):
        self.record_dir = Path(record_dir) if record_dir else None
        self.model = model

    def complete(self, prompt: str) -> str:
        import anthropic  # imported lazily so tests never need the package/key
        key = os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise RuntimeError("ANTHROPIC_API_KEY not set or empty; use ReplayClient for tests")
        client = anthropic.Anthropic(api_key=key)
        msg = client.messages.create(
            model=self.model, max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(block.text for block in msg.content if block.type == "text")
        if self.record_dir:
            self.record_dir.mkdir(parents=True, exist_ok=True)
            (self.record_dir / f"{request_hash(prompt)}.json").write_text(
                json.dumps({"prompt": prompt, "response": text}, ensure_ascii=False),
                encoding="utf-8",
            )
        return text
