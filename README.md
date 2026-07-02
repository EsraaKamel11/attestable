# attestable

A verifiable evidence-and-citation pipeline for an audit agent. An AI agent tests an internal control against sampled evidence and produces a decision where **every assertion is linked to a source span, nothing is asserted without a citation**, and **the agent's own actions are written to a hash-chained, tamper-evident log that anyone can replay**.

Built as a clean-room demonstration of the half of audit automation that gets harder, not easier, as you move into regulated customers: an agent that audits must itself be auditable.

## The idea in one screen

- The LLM is bounded to **proposing** typed, cited facts. It never decides the outcome.
- A deterministic **gate** verifies each proposed fact against its source (a spreadsheet cell or an exact text span). A fact whose citation does not resolve, or does not match its source, is rejected. This is enforced by code, not by trusting the model.
- A **rule engine** computes the verdict (`PASS` / `EXCEPTION` / `UNVERIFIABLE`) over verified facts only. The model cannot fabricate a verdict (it is computed) or a fact (each is checked against source).
- Every step is appended to a **hash-chained audit log** with a pinned canonical serialization.
- An independent **audit-replay** re-checks, from the sealed log plus the source documents plus a retained seal, that the chain is intact, every citation still resolves and still matches, and the verdict still follows from the evidence. No model and no trust are required to re-verify.
- When the agent cannot establish a required fact, it returns **UNVERIFIABLE** and escalates to a human. It never guesses a pass.

The worked control is a **user-access review with a segregation-of-duties check**, an IT general control and the most common area in real SOX 404 programs.

## Clone and run

Requires Python 3.11+.

```
python -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]"      # Windows
# or:  .venv/bin/python -m pip install -e ".[dev]"    # macOS / Linux
.venv\Scripts\python -m pytest -q
```

The entire suite runs **with no API key and no network**: every model call is served from a recorded or scripted deterministic spine. `ANTHROPIC_API_KEY` is read from the environment only, and only in an explicit record mode.

## The demo, told by the tests

- `tests/test_pipeline_e2e.py` drives four users through the four outcomes end to end: a segregation-of-duties **EXCEPTION**; an **UNVERIFIABLE** case (an approval whose field is unreadable) that escalates to a human queue; an **EXCEPTION** for access with no approval over a *complete* approvals corpus; and a clean **PASS**, each with a fully green audit-replay.
- `tests/test_adversarial_citation.py` is the "refuses to fabricate" proof: a fabricated source and a mis-cited value are both rejected at the gate.
- `tests/test_tamper.py` is the tamper-evidence proof: **T1** alters a logged fact (integrity fails); **T2** drops a mid-chain entry (integrity fails); **T3** edits the underlying spreadsheet *after* sealing, so the log stays intact but grounding re-resolution catches it; **T4** truncates the tail (caught by the retained seal); and an emptied log is caught too.
- `tests/test_eval_ablation.py` is the with-vs-without eval: over a 12-sample hand-labeled set, the guarded pipeline's false-pass rate is **0** while a naive no-guardrails baseline's is **5**. Run `attestable.eval.run_eval` to write a scorecard (`scorecard.json` and `scorecard.md`). This is a demonstration over a small synthetic labeled set, not a statistically powered benchmark; "naive" means the same model proposals with the faithfulness gate and the UNVERIFIABLE abstention removed.
- `tests/test_connector_e2e.py` is the auditable-acquisition demo: evidence is fetched from a synthetic FastAPI + SQLite system-of-record over its API, normalized into the same cited evidence forms, and the acquisition path (method + locator + a content hash of the fetched bytes) is written into the same hash chain. Replay then audits the fetch too: **T5** changes an uncited byte in a fetched file after sealing, which grounding does not see but the acquisition check catches.

## Architecture

```
src/attestable/
  types.py         Citation (cell | text-span), Assertion, VerifiedFact, Outcome, Verdict
  evidence.py      EvidenceStore: resolve a citation to its source content (confined to a root)
  predicates.py    deterministic faithfulness predicates (cell-value-equals, exact-span-verbatim)
  gate.py          resolve-and-faithfulness gate: nothing enters without a matching citation
  llm/             record/replay LLM spine (keyless) plus a real client used only for recording
  extract.py       the LLM proposes typed, cited facts
  controls/        the control abstraction plus the user-access + SoD control
  verdict.py       PASS / EXCEPTION / UNVERIFIABLE, with the EXCEPTION vs UNVERIFIABLE boundary
  audit/
    canonical.py   pinned, versioned, deterministic serialization (golden-byte tested)
    log.py         hash-chained, seal-able audit log
    replay.py      independent audit-replay: integrity + grounding + derivation
  escalation.py    durable human-review queue for UNVERIFIABLE
  workpaper.py     the cited working-paper output
  pipeline.py      orchestration
  scenarios/       deterministic synthetic evidence (no real data)
```

## Honest boundaries

This is a clean-room demonstration, and it is careful about what it does and does not claim.

- **Not an auditor's tool.** It brings the agent-reliability half, not audit-domain judgment. The control logic rests on documented rules, not professional judgment.
- **Synthetic data only.** The evidence and the system of record are synthetic; there is no integration with a real IAM or GRC system. The API evidence connector against a synthetic system-of-record is built and its acquisition is audited; the browser fallback is designed, not built here (proven against a live UI elsewhere). Acquisition-audit proves evidence is unchanged since fetch with a recorded method and locator, it does not prove the source authentically served it (there is no source signature). There is no integration with a real IAM or GRC system.
- **"Regulator-grade in spirit," not certified.** The audit trail embodies the properties a regulator would want: integrity, provenance to a source of record, reproducible derivation, and independent verifiability. It is a demonstration of those properties, not a certified or legally-admissible record. In particular, tail-truncation is only detectable with a **retained or published seal**, not from the log alone, so replay takes that seal as an input.
- **Deterministic faithfulness only.** The gate checks literal value and span equality; anything not literally decidable becomes UNVERIFIABLE rather than being judged by the model.
- **One control built; a second (three-way match) designed on paper.** The engine is control-pluggable by design; only the user-access + SoD control is built.

## What is next (designed, not yet built)

- The **browser fallback** for the evidence connector (Playwright driving a read-only SoR UI when its API is unavailable), recorded and replayed on the same keyless spine, with the browser action sequence written into the audit trail exactly as the API path is.

---

Every line in this repository is original, written fresh for this artifact.
