import json
from .types import Assertion, CellRef, TextSpan
from .llm.client import LLMClient


def build_prompt(required_keys: list[str], evidence_manifest: str) -> str:
    keys = ", ".join(required_keys)
    return (
        "You are an audit evidence extractor. Extract ONLY these facts: "
        f"{keys}.\n"
        "Every fact MUST cite its exact source. Return a JSON array of objects "
        '{"claim","value","citation"} where citation is either '
        '{"kind":"cell","doc","sheet","cell"} or '
        '{"kind":"span","doc","start","end","quote"}. '
        "Never invent a value or a citation. If a fact is not present in the "
        "evidence, omit it.\n\nEVIDENCE MANIFEST:\n" + evidence_manifest
    )


def parse_assertions(raw: str) -> list[Assertion]:
    facts: list[Assertion] = []
    for item in json.loads(raw):
        c = item["citation"]
        if c["kind"] == "cell":
            citation = CellRef(c["doc"], c["sheet"], c["cell"])
        elif c["kind"] == "span":
            citation = TextSpan(c["doc"], int(c["start"]), int(c["end"]), c["quote"])
        else:
            raise ValueError(f"unknown citation kind {c['kind']!r}")
        facts.append(Assertion(item["claim"], str(item["value"]), citation))
    return facts


def extract_facts(required_keys: list[str], evidence_manifest: str, llm: LLMClient) -> list[Assertion]:
    return parse_assertions(llm.complete(build_prompt(required_keys, evidence_manifest)))
