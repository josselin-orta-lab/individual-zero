"""P3 post-run custody using synthetic receipts; no P3 study world is opened."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i3.lab import p3_custody as custody, p3_schedule as sched
from i3.modules.genome import (
    historical_v3_generation_zero as generation_zero,
    historical_v3_mutate as mutate,
    digest_historical_v3 as digest,
)


def fixture():
    """Synthetic genealogy with all-dead one-step lives. NOT scientific evidence."""
    pops = []
    for p in range(4):
        gen_data = []
        cohorts = {}
        for g in range(3):
            arms = {}
            for arm in sched.ARMS:
                people = []
                genomes = []
                for slot in range(6):
                    parent = None
                    if g == 0:
                        seed = sched.generation_zero_seed(p, slot)
                        genome = generation_zero(seed)
                        ancestry = {"genome_seed": seed, "parent_slot": None}
                    else:
                        parent = cohorts[arm][slot]
                        seed = sched.mutation_seed(p, g, slot, arm)
                        genome = mutate(parent, seed, scale=sched.MUTATION_SCALE)
                        ancestry = {
                            "mutation_seed": seed, "parent_slot": slot,
                            "parent_genome_sha256": digest(parent),
                        }
                    lives = []
                    for family in sched.FAMILIES:
                        for repeat in range(sched.REPEATS):
                            world = sched.selection_world_index(p, g, family, repeat)
                            lives.append({
                                "population": p, "generation": g, "arm": arm, "slot": slot,
                                "family": family, "selection_world_index": world,
                                "life_seed": sched.life_seed(p, g, family, repeat),
                                "genome_sha256": digest(genome),
                                "world_sha256": ("%064x" % world),
                                "source_sha256": "f"*64,
                                "manifest_id": "synthetic-manifest",
                                "evidence_head": "synthetic-evidence",
                                "steps_lived": 1, "censored": False, "terminal": "dead",
                                "death_causes": ["zero_water"],
                                "paid": {"energy": 0.0, "vigilance": 0.0},
                            })
                    people.append({
                        "slot": slot, "genome_sha256": digest(genome),
                        "lives": lives, "fitness": [0, 6], **ancestry,
                    })
                    genomes.append(genome)
                arms[arm] = people
                cohorts[arm] = genomes
            gen_data.append({"generation": g, "arms": arms,
                             "world_indices": [
                                 sched.selection_world_index(p, g, fam, rep)
                                 for fam in sched.FAMILIES for rep in range(sched.REPEATS)]})
        pops.append({"population": p, "generations": gen_data})
    evidence = {
        "schema": custody.PROTOCOL, "source_sha": custody.SOURCE_SHA,
        "schedule_sha256": custody.SCHEDULE_SHA,
        "status": "selection_only_validation_NOT_RUN",
        "total_lives": custody.MAX_LIVES, "populations": pops,
    }
    reseal(evidence)
    return evidence


def reseal(report):
    report["sha256"] = sha256(json.dumps(
        {k: v for k, v in report.items() if k != "sha256"},
        sort_keys=True, separators=(",", ":")).encode()).hexdigest()


class P3EvidenceCustodyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = fixture()

    def test_custody_reconstructs_all_48_genomes_without_world(self):
        frozen = custody.verify_and_freeze(self.data)
        self.assertEqual(frozen["selection_lives_verified"], 864)
        self.assertEqual(frozen["world_keys_verified"], 72)
        self.assertEqual(len(frozen["genomes"]), 48)
        self.assertEqual(frozen["validation"], "NOT_RUN")
        self.assertEqual(frozen["reserve"], "LOCKED")
        for row in frozen["genomes"]:
            self.assertEqual(digest(row["genome"]), row["genome_sha256"])
            self.assertEqual(set(row["genome"]), {"schema", "genes"})

    def test_tampered_original_content_rejected(self):
        bad = deepcopy(self.data)
        bad["populations"][0]["generations"][0]["arms"]["selected"][0]["fitness"] = [5, 6]
        with self.assertRaises(ValueError):
            custody.verify_and_freeze(bad)

    def test_tampered_parent_genealogy_rejected_even_with_resigned_outer_hash(self):
        bad = deepcopy(self.data)
        person = bad["populations"][0]["generations"][1]["arms"]["selected"][0]
        person["parent_genome_sha256"] = "0"*64
        reseal(bad)
        with self.assertRaises(ValueError):
            custody.verify_and_freeze(bad)

    def test_tampered_world_receipt_rejected_even_with_resigned_outer_hash(self):
        bad = deepcopy(self.data)
        life = bad["populations"][0]["generations"][1]["arms"]["selected"][0]["lives"][0]
        life["world_sha256"] = "0"*64
        reseal(bad)
        with self.assertRaises(ValueError):
            custody.verify_and_freeze(bad)

    def test_forged_censoring_rejected(self):
        bad = deepcopy(self.data)
        life = bad["populations"][0]["generations"][1]["arms"]["selected"][0]["lives"][0]
        life["terminal"] = "censored"
        life["censored"] = True
        life["death_causes"] = []
        reseal(bad)
        with self.assertRaises(ValueError):
            custody.verify_and_freeze(bad)


if __name__ == "__main__":
    unittest.main()
