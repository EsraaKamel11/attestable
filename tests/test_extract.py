import json
from attestable.types import CellRef, TextSpan
from attestable.extract import parse_assertions, build_prompt, extract_facts

def test_parse_assertions_reads_both_citation_kinds():
    raw = json.dumps([
        {"claim": "current_entitlements", "value": "payment_creator;payment_approver",
         "citation": {"kind": "cell", "doc": "access_export.xlsx", "sheet": "Users", "cell": "C2"}},
        {"claim": "approved_entitlements", "value": "payment_creator",
         "citation": {"kind": "span", "doc": "approvals.txt", "start": 30, "end": 45, "quote": "payment_creator"}},
    ])
    facts = parse_assertions(raw)
    assert isinstance(facts[0].citation, CellRef) and facts[0].citation.cell == "C2"
    assert isinstance(facts[1].citation, TextSpan) and facts[1].citation.quote == "payment_creator"

def test_extract_uses_llm_and_prompt_mentions_keys():
    class FakeLLM:
        def __init__(self): self.seen = ""
        def complete(self, prompt): self.seen = prompt; return "[]"
    llm = FakeLLM()
    assert extract_facts(["current_entitlements"], "manifest", llm) == []
    assert "current_entitlements" in llm.seen and "manifest" in llm.seen
