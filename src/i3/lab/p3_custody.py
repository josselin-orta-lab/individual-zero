"""Post-run I3 P3 custody: reconstruct and freeze G2 genomes from evidence.

Read-only derivative of the one preregistered original selection artifact.
Never opens any world or executes any additional life. Run against the same
unchanged genome algorithm that produced the pilot.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import sys

from i3.lab import p3_schedule
from i3.modules.genome import digest as genome_digest, generation_zero, mutate, validate

SOURCE_SHA = "52476fec3f39a7fd70bf611877b01d9c13d26009"
SCHEDULE_SHA = "230cd653f0a8e580682b351fa3474b9f4dbd9f3e98e7eec1fa61361c0e7289db"
PROTOCOL = "i3-p3-mutation-pilot-v1"
MAX_LIVES = 864


def verify_and_freeze(report: dict) -> dict:
    """Fail closed if a birth, world key, fitness or life receipt is missing."""
    if (report["schema"] != PROTOCOL or report["source_sha"] != SOURCE_SHA or
        report["schedule_sha256"] != SCHEDULE_SHA or
        report["status"] != "selection_only_validation_NOT_RUN" or
        report["total_lives"] != MAX_LIVES or
        len(report["populations"]) != p3_schedule.POPULATIONS):
        raise ValueError("unrecognized original P3 protocol or partial run")
    claimed = report["sha256"]
    raw = {k: v for k, v in report.items() if k != "sha256"}
    if sha256(json.dumps(raw, sort_keys=True, separators=(",", ":")).encode()
              ).hexdigest() != claimed:
        raise ValueError("original P3 evidence content digest mismatch")
    keys = set()
    manifestations = 0
    g2 = []
    for p, population in enumerate(report["populations"]):
        if population["population"] != p:
            raise ValueError("population index changed")
        cohorts = {}
        if len(population["generations"]) != p3_schedule.GENERATIONS:
            raise ValueError("missing generation")
        for g, generation in enumerate(population["generations"]):
            if generation["generation"] != g:
                raise ValueError("generation order changed")
            for arm in p3_schedule.ARMS:
                if arm not in generation["arms"]:
                    raise ValueError("missing experimental arm")
                people = generation["arms"][arm]
                if len(people) != p3_schedule.GENOTYPES:
                    raise ValueError("missing genotype")
                rebuilt = []
                for slot, person in enumerate(people):
                    if person["slot"] != slot:
                        raise ValueError("genome slot mismatch")
                    if g == 0:
                        seed = p3_schedule.generation_zero_seed(p, slot)
                        if person["genome_seed"] != seed or person["parent_slot"] is not None:
                            raise ValueError("generation-zero provenance mismatch")
                        genome = generation_zero(seed)
                    else:
                        parent_slot = person["parent_slot"]
                        if type(parent_slot) is not int or not 0 <= parent_slot < p3_schedule.GENOTYPES:
                            raise ValueError("parent not in previous cohort")
                        parent = cohorts[arm][parent_slot]
                        if genome_digest(parent) != person["parent_genome_sha256"]:
                            raise ValueError("parent digest mismatch")
                        expected_seed = p3_schedule.mutation_seed(p, g, slot, arm)
                        if person["mutation_seed"] != expected_seed:
                            raise ValueError("offspring mutation seed mismatch")
                        genome = mutate(parent, expected_seed, scale=p3_schedule.MUTATION_SCALE)
                    validate(genome)
                    if genome_digest(genome) != person["genome_sha256"]:
                        raise ValueError("observed genome cannot be reconstructed")
                    lives = person["lives"]
                    if len(lives) != len(p3_schedule.FAMILIES) * p3_schedule.REPEATS:
                        raise ValueError("missing lifetime sample")
                    survivors = steps = 0
                    for f, family in enumerate(p3_schedule.FAMILIES):
                        for repeat in range(p3_schedule.REPEATS):
                            i = f * p3_schedule.REPEATS + repeat
                            life = lives[i]
                            world_index = p3_schedule.selection_world_index(p, g, family, repeat)
                            expected_seed = p3_schedule.life_seed(p, g, family, repeat)
                            if (life["arm"] != arm or life["population"] != p or
                                life["generation"] != g or life["slot"] != slot or
                                life["family"] != family or
                                life["selection_world_index"] != world_index or
                                life["life_seed"] != expected_seed or
                                life["genome_sha256"] != person["genome_sha256"] or
                                not life["manifest_id"] or not life["evidence_head"] or
                                type(life["steps_lived"]) is not int or
                                not 1 <= life["steps_lived"] <= p3_schedule.HORIZON or
                                life["censored"] != (life["terminal"] == "censored") or
                                (life["terminal"] == "censored" and
                                 life["steps_lived"] != p3_schedule.HORIZON) or
                                bool(life["death_causes"]) != (life["terminal"] == "dead") or
                                any(life["paid"][c] < 0 for c in ("energy","vigilance"))):
                                raise ValueError("invalid or mislabeled lifetime")
                            key = (p, g, family, repeat)
                            world_id = life["world_sha256"]
                            if key in keys and keys[key] != (world_id, expected_seed):
                                raise ValueError("unequal initial world opportunity")
                            keys[key] = (world_id, expected_seed)
                            survivors += life["censored"]
                            steps += life["steps_lived"]
                            manifestations += 1
                    if person["fitness"] != [survivors, steps]:
                        raise ValueError("fitness not derived exclusively from observed lives")
                    rebuilt.append(genome)
                    if g == p3_schedule.GENERATIONS - 1:
                        g2.append({
                            "population": p, "arm": arm, "slot": slot,
                            "genome": genome,
                            "genome_sha256": genome_digest(genome),
                            "parent_slot": person["parent_slot"],
                            "parent_genome_sha256": person["parent_genome_sha256"],
                            "mutation_seed": person["mutation_seed"],
                        })
                if g == 0 and arm == p3_schedule.ARMS[-1] and rebuilt != cohorts[p3_schedule.ARMS[0]]:
                    raise ValueError("G0 arms are not identical")
                cohorts[arm] = rebuilt
    if manifestations != MAX_LIVES or len(keys) != 72 or len(g2) != 48:
        raise ValueError("partial world, life, or G2 genome evidence")
    record = {
        "schema": "i3-p3-frozen-g2-genomes-v1",
        "origin_selection_sha256": claimed,
        "source_sha": SOURCE_SHA,
        "schedule_sha256": SCHEDULE_SHA,
        "population_count": p3_schedule.POPULATIONS,
        "generation": p3_schedule.GENERATIONS - 1,
        "selection_lives_verified": manifestations,
        "world_keys_verified": len(keys),
        "validation": "NOT_RUN",
        "reserve": "LOCKED",
        "genomes": g2,
    }
    record["sha256"] = sha256(json.dumps(record, sort_keys=True,
                                         separators=(",", ":")).encode()).hexdigest()
    return record


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: python -m i3.lab.p3_custody ORIGINAL.json FROZEN_G2.json")
    original = json.loads(Path(sys.argv[1]).read_text())
    frozen = verify_and_freeze(original)
    path = Path(sys.argv[2])
    if path.exists():
        raise FileExistsError("do not overwrite a previous G2 custody artifact")
    path.write_text(json.dumps(frozen, sort_keys=True, indent=2) + "\n")
    print(json.dumps({k: v for k, v in frozen.items() if k != "genomes"},
                     indent=2, sort_keys=True))
