import sys
from pathlib import Path
from .evidence import EvidenceStore
from .controls.user_access_sod import USER_ACCESS_SOD
from .llm.replay_client import ReplayClient
from .pipeline import run_control


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if len(argv) != 3 or argv[0] != "run":
        print("usage: python -m attestable.cli run <scenario_dir> <sample_id>")
        return 2
    _, scenario_dir, sample_id = argv
    store = EvidenceStore(Path(scenario_dir))
    llm = ReplayClient(Path(scenario_dir) / "fixtures")
    result = run_control(USER_ACCESS_SOD, store, sample_id, llm)
    print(result.workpaper)
    print(f"\nseal: {result.seal}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
