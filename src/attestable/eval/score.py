from ..types import Outcome


def _false_pass(rows, key):
    return sum(1 for r in rows if r[key] is Outcome.PASS and r["gold"] is not Outcome.PASS)


def _accuracy(rows, key):
    return sum(1 for r in rows if r[key] is r["gold"])


def score(rows: list[dict]) -> dict:
    return {
        "n": len(rows),
        "guarded_false_pass": _false_pass(rows, "guarded"),
        "naive_false_pass": _false_pass(rows, "naive"),
        "guarded_accuracy": _accuracy(rows, "guarded"),
        "naive_accuracy": _accuracy(rows, "naive"),
        "guarded_over_abstention": sum(
            1 for r in rows if r["guarded"] is Outcome.UNVERIFIABLE and r["determinable"]),
    }
