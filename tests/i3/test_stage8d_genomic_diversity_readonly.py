"""Stage8-D pure posthoc genotype falsifiers, no World, no new life."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import inspect
import json
import math
import unittest

from i3.lab import stage8d_genomic_diversity_readonly as D
from i3.modules import genome as G


class Stage8DGeneticDiversityPureTests(unittest.TestCase):
    def test_rms_diversity_276_pairs_and_normalized_bounds(self):
        a = G.midpoint()
        self.assertEqual(D.pairwise_rms_diversity([a]*24), 0)
        b = G.generation_zero(654321)
        genomes = [a]*12+[b]*12
        observed = D.pairwise_rms_diversity(genomes)
        distance = math.sqrt(sum(
            (x-y)**2 for x,y in zip(D.normalized_genome(a),D.normalized_genome(b))
        )/len(G.BOUNDS))
        self.assertAlmostEqual(observed, 144*distance/276, places=13)
        self.assertEqual(D.PAIRS, 276)
        with self.assertRaises(ValueError):
            D.pairwise_rms_diversity(genomes[:-1])
        with self.assertRaises(ValueError):
            D.pairwise_rms_diversity([G.midpoint()]*23+[{"schema":G.SCHEMA, "genes":{}}])

    def test_parent_entropy_matches_occupancy_and_fails_closed(self):
        same = D.parent_occupancy([3]*24)
        self.assertEqual(same["distinct_parents"], 1)
        self.assertEqual(same["entropy_nats"], 0)
        unique = D.parent_occupancy(list(range(24)))
        self.assertEqual(unique["distinct_parents"], 24)
        self.assertAlmostEqual(unique["entropy_nats"], math.log(24))
        s = D.parent_occupancy([0]*12+[1]*8+[2]*4)
        m = D.parent_occupancy([6]*8+[15]*4+[23]*12)
        self.assertEqual(s["multiplicity_multiset"],m["multiplicity_multiset"])
        self.assertEqual(s["entropy_nats"],m["entropy_nats"])
        for invalid in ([0]*23, [0]*25, [0]*23+[24],
                        [0]*23+[-1], [0]*23+[True], None):
            with self.subTest(value=str(invalid)), self.assertRaises(ValueError):
                D.parent_occupancy(invalid)

    def test_pearson_uses_only_32_population_units_and_no_pvalue(self):
        x = list(range(32))
        self.assertAlmostEqual(D.pearson_descriptive(x, [v*7+2 for v in x]), 1)
        self.assertAlmostEqual(D.pearson_descriptive(x, [-v for v in x]), -1)
        self.assertIsNone(D.pearson_descriptive([2]*32, x))
        with self.assertRaises(ValueError):
            D.pearson_descriptive(x[:-1],x)
        with self.assertRaises(ValueError):
            D.pearson_descriptive([float("nan")]+x[1:],x)

    def test_sealed_records_include_all_1152_born_and_parent_slots(self):
        g=G.midpoint()
        offspring=[]
        parents=[]
        for p in range(16):
            for arm in D.ARMS:
                for slot in range(24):
                    parents.append({"population":p,"arm":arm,"slot":slot,
                                    "parent_slot":slot})
                    offspring.append({"population":p,"arm":arm,"slot":slot,
                                      "genome":g,"genome_sha256":G.digest(g)})
        event={"schema":"i3-stage8c-sealed-three-arm-parentage/v1",
               "generation":2,"draws":parents,"offspring":offspring}
        with TemporaryDirectory() as temp:
            file=Path(temp)/"SELECT_G2.json"
            file.write_text(json.dumps(event))
            result=D._selection_records(file,2)
            self.assertEqual(len(result["born"]),1152)
            self.assertEqual(result["drawn"][4,"matched_multiplicity",10],10)
            event["offspring"][-1]["genome_sha256"]="0"*64
            file.write_text(json.dumps(event))
            with self.assertRaises(ValueError):
                D._selection_records(file,2)
            event["offspring"][-1]["genome_sha256"]=G.digest(g)
            event["draws"][-1]["parent_slot"]=24
            file.write_text(json.dumps(event))
            with self.assertRaises(ValueError):
                D._selection_records(file,2)

    def test_original_audit_required_before_genomic_read(self):
        with TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                D._from_verified_panels(Path(temp), {"status":"PASS"})
            with self.assertRaises(ValueError):
                D.audit_full(str(Path(temp)/"plan"),str(Path(temp)/"none"),
                             str(Path(temp)/"receipt"))
        self.assertEqual(D.SOURCE, D.A.ORIGINAL_HEAD)
        self.assertEqual(D.PREVERDICT_AUDITOR,
                         "23d0e3eabff0042123c84f4b292a2e4c72cfcc8f")

    def test_no_native_life_motor_world_mutation_in_module(self):
        src=inspect.getsource(D)
        forbidden=("run_life(", "world_for_stage6(", ".mutate(",
                   "create_world(", "allocate_science(", "generation_zero(",
                   "from i3.lab import stage8c_prospective_science",
                   "from i3.lab import stage8c_three_arm_transport")
        for item in forbidden:
            self.assertNotIn(item,src)
        self.assertEqual(D.RUN_ID,44320492293)
        self.assertEqual(D.POPULATIONS,32)
        self.assertEqual(D.STATUS,
                         "STAGE8D_POSTHOC_ORIGINAL_BOUND_DESCRIPTIVE_COMPLETE")


if __name__ == "__main__":
    unittest.main()
