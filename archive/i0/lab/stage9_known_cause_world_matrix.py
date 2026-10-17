"""Seed-varied P-47 physical attribution diagnostics, NOT scientific acceptance.

Every probe creates a fresh WorldBody. World truth belongs exclusively to this
bench; the AgencyComparator receives only a frozen command and accessible
Perception, never an oracle label. There are four genuinely different
geometric layouts; repeating one is rejected rather than counted as an
independent world. These are compatibility probes, not lived autonomous runs.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import json

from .determinism import canonical_causal_bytes, sha256_hex
from .stage9_known_causes_benchmark import (
    KnownCauseMetrics, _protocol, run_known_cause_probes,
)


@dataclass(frozen=True, slots=True)
class KnownCauseWorldRun:
    seed: int
    world_digest: str
    results: KnownCauseMetrics


@dataclass(frozen=True, slots=True)
class KnownCauseWorldMatrix:
    protocol_version: str
    seeds: tuple[int, ...]
    runs: tuple[KnownCauseWorldRun, ...]
    physically_ground_truthed_cases: int
    correct_links: int
    uncertain_cases: int
    false_self_links: int
    observed_accuracy: float | None
    classification: str
    digest: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)

    def verify_digest(self) -> bool:
        data = self.as_dict()
        digest = data.pop("digest")
        return digest == sha256_hex(canonical_causal_bytes(data))

    def to_json(self) -> str:
        return json.dumps(
            self.as_dict(), sort_keys=True, indent=2, ensure_ascii=False,
        ) + "\n"


def run_known_cause_world_matrix(
    *, seeds: tuple[int, ...] = (41, 42, 43),
) -> KnownCauseWorldMatrix:
    if (
        not isinstance(seeds, tuple)
        or not seeds
        or any(type(seed) is not int or seed < 0 for seed in seeds)
        or len(set(seeds)) != len(seeds)
    ):
        raise ValueError("invalid known-cause world-matrix seeds")
    rows = []
    seen_worlds: set[str] = set()
    for seed in seeds:
        probes = _protocol(world_seed=seed)
        world_digest = sha256_hex(canonical_causal_bytes([
            {
                "probe": probe.identifier,
                "step": probe.sent_t_monde,
                "layout": probe.layout.as_dict(),
                "command": probe.command.as_dict(),
                "prediction": [
                    probe.prediction.variable,
                    probe.prediction.value_or_delta,
                    probe.prediction.precision,
                ],
                "bench_truth": [probe.known_cause, probe.physical_effect],
            }
            for probe in probes
        ]))
        if world_digest in seen_worlds:
            raise ValueError("reused physical layout is not an independent world")
        seen_worlds.add(world_digest)
        result = run_known_cause_probes(world_seed=seed)
        if (
            len(result.cases) != len(probes)
            or result.ground_truthed_cases <= 0
        ):
            raise AssertionError("seeded causal probe omitted physical cases")
        rows.append(KnownCauseWorldRun(
            seed=seed, world_digest=world_digest, results=result,
        ))
    total = sum(row.results.ground_truthed_cases for row in rows)
    correct = sum(row.results.correct_links for row in rows)
    report = KnownCauseWorldMatrix(
        protocol_version="stage9-known-cause-geometric-matrix-v1",
        seeds=seeds,
        runs=tuple(rows),
        physically_ground_truthed_cases=total,
        correct_links=correct,
        uncertain_cases=sum(row.results.uncertain_cases for row in rows),
        false_self_links=sum(row.results.false_self_links for row in rows),
        observed_accuracy=correct / total if total else None,
        classification="diagnostic_only",
        digest="",
    )
    data = report.as_dict()
    data.pop("digest")
    return replace(report, digest=sha256_hex(canonical_causal_bytes(data)))


def main() -> None:
    print(run_known_cause_world_matrix().to_json(), end="")


if __name__ == "__main__":
    main()
