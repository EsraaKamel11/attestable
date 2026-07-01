import hashlib
from typing import Protocol


def request_hash(prompt: str) -> str:
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()


class LLMClient(Protocol):
    def complete(self, prompt: str) -> str: ...
