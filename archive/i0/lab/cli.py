"""Command-line entry point for the bootstrap runtime."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from i0 import BootstrapI0

from .runtime import RunConfig, run_individual
from .scenarios import SmokeScenario
from .sinks import JsonlSink


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="individual-zero",
        description=(
            "Run the deterministic Individual Zero bootstrap runtime. "
            "This validates execution and observability only; it is not a cognitive experiment."
        ),
    )
    parser.add_argument("--cycles", type=int, default=3)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--run-id", default="bootstrap-run")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/bootstrap-run.jsonl"),
        help="JSONL event artifact path.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    config = RunConfig(
        run_id=args.run_id,
        seed=args.seed,
        cycles=args.cycles,
    )

    summary = run_individual(
        individual=BootstrapI0(),
        scenario=SmokeScenario(),
        config=config,
        sink=JsonlSink(args.output),
    )

    print(json.dumps(summary.as_dict(), sort_keys=True))
    print(f"artifact={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
