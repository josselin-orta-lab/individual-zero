"""I3 selected-reference routing without invented evidence or scientific World GO."""
from contextlib import redirect_stdout
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "i3_route_research_coordinator", ROOT / "tools/research_coordinator.py")
rc = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(rc)


class I3SelectedReferenceResearchRoutingTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.registry = {
            "active_generation": "I1", "reference_generation": "I3",
            "generations": {"I0": {"role": "frozen_reference"},
                            "I1": {"role": "active"}},
        }
        self.program = {
            "schema": rc.SCHEMA, "project": "josselin-orta-lab/individual-zero",
            "policy": {
                "no_auto_execution": True, "no_auto_promotion": True,
                "no_auto_scientific_go": True,
                "unreviewed_evidence_fails_closed": True,
                "score_is_heuristic_not_probability": True,
                "github_snapshot_max_age_hours": 24,
            }, "source_checks": [], "questions": [], "gates": [],
            "interventions": [], "findings": [], "catalog_roots": [],
        }
        self.surface = {
            "schema": "i3-active-surface/v1",
            "reference": "P1.3 funded-v2",
            "current_stage": "2.1 replay gate",
            "canonical_status": "REPLAY_GATE_CAPACITY_SHOWN",
            "next_scientific_action": (
                "HOLD: Stage-2 scientific verdict remains NOT_ISSUED. "
                "No new World permitted; E3 original CLOSED_NEGATIVE."
            ),
            "governance": {
                "fresh_lived_worlds_allowed": False,
                "scientific_gate_authorized": False,
                "other_world_indices_authorized": False,
                "next_scientific_cohort_authorized": False,
                "all_new_worlds_currently_authorized": False,
            },
        }
        self.contract = {
            "generation": "I3", "status": "proposal", "entrypoints": {},
            "activation": "NOT_REGISTERED_NOT_EXECUTABLE",
        }
        self.write("config/engine-registry.json", self.registry)
        self.write(rc.PROGRAM, self.program)
        self.write("src/i2/engine.json", {"status":"proposal","entrypoints":{}})
        self.write("src/i3/engine.json", self.contract)
        self.write(rc.I3_ROUTING_FILE, self.surface)
        path = self.root / rc.I3_STOP_REVIEW
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# Current C01 internal review, NOT external attestation\n",
                        encoding="utf-8")

    def write(self, name, value):
        path = self.root/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    def test_reference_i3_active_i1_route_never_autorizes_cohorts(self):
        self.assertEqual(rc.audit(self.root)["status"],"PASS")
        state = rc.research_state(self.root, at_sha="a"*40)
        self.assertEqual(state["development_reference_generation"], "I3")
        self.assertEqual(state["active_generation"], "I1")
        self.assertFalse(state["generations"]["I3"]["active"])
        self.assertEqual(state["generations"]["I3"]["contract_status"], "proposal")
        self.assertFalse(state["generations"]["I3"]["entrypoints_declared"])
        route = state["i3_scientific_route"]
        self.assertEqual(route["status"], "HOLD_INDEPENDENT_METHODS_REVIEW")
        self.assertEqual(route["scientific_verdict"], "NOT_ISSUED")
        self.assertFalse(route["source_pin_reviewed"])
        self.assertFalse(route["independent_methods_review"])
        self.assertFalse(route["scientific_world_authorized"])
        self.assertFalse(route["engine_activation_authorized"])
        self.assertEqual(route["execution"], "NOT_PERFORMED")
        raw = (self.root/rc.I3_ROUTING_FILE).read_bytes()
        expected = hashlib.sha1(
            b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw
        ).hexdigest()
        self.assertEqual(route["observed_source_git_blob_sha"], expected)

    def test_default_and_explicit_i3_prefer_nonexecuting_review_not_i2(self):
        state = rc.research_state(self.root, at_sha="b"*40)
        for selected in ("all","I3"):
            with self.subTest(selected=selected):
                ranked=rc.recommendations(state,self.program,5,generation=selected)
                self.assertEqual(ranked["status"],"I3_HOLD_NON_EXECUTABLE")
                self.assertEqual(ranked["recommended_next"]["id"],
                                 "I3-S2-C01-INDEPENDENT-METHODS")
                self.assertEqual(ranked["recommended_next"]["issue"],1062)
                self.assertEqual(ranked["recommended_next"]["stage"],
                                 "HOLD_INDEPENDENT_METHODS_REVIEW")
                self.assertEqual(ranked["recommended_next"]["blocked_by_gates"],
                                 ["INDEPENDENT_METHODS_AND_SOURCE_REVIEW"])
                self.assertTrue(ranked["external_verification_required"])
                self.assertEqual(ranked["execution"],"NOT_PERFORMED")
                self.assertEqual(ranked["promotion"],"NOT_AUTHORIZED")
                self.assertEqual(ranked["scientific_verdict"],"NOT_EVALUATED")
        with redirect_stdout(io.StringIO()) as stdout:
            self.assertEqual(rc.main([
                "recommend","--generation","I3","--format","json",
                "--at-sha","b"*40],self.root),0)
        cmd=json.loads(stdout.getvalue())
        self.assertEqual(cmd["recommended_next"]["issue"],1062)
        self.assertFalse(cmd["i3_scientific_route"]["scientific_world_authorized"])

    def test_drift_of_permission_source_or_engine_fails_closed(self):
        changed = copy.deepcopy(self.surface)
        for key in changed["governance"]:
            changed = copy.deepcopy(self.surface)
            changed["governance"][key] = True
            with self.subTest(flag=key):
                self.write(rc.I3_ROUTING_FILE, changed)
                state=rc.research_state(self.root,at_sha="a"*40)
                result=rc.recommendations(state,self.program,2)
                self.assertEqual(result["status"],"I3_BLOCKED_SOURCE_REVIEW")
                self.assertIsNone(result["recommended_next"])
        self.write(rc.I3_ROUTING_FILE, self.surface)
        contract=copy.deepcopy(self.contract)
        contract["entrypoints"]={"birth":"unverified"}
        self.write("src/i3/engine.json", contract)
        self.assertEqual(rc.i3_scientific_route(self.root,self.registry)["status"],
                         "I3_SOURCE_REVIEW_REQUIRED")

    def test_missing_or_malformed_surface_never_falls_back_to_i2(self):
        path=self.root/rc.I3_ROUTING_FILE
        path.unlink()
        state=rc.research_state(self.root,at_sha="a"*40)
        ranked=rc.recommendations(state,self.program,5)
        self.assertIsNone(ranked["recommended_next"])
        self.assertEqual(ranked["status"],"I3_BLOCKED_SOURCE_REVIEW")
        path.write_text("not json",encoding="utf-8")
        ranked=rc.recommendations(rc.research_state(self.root,at_sha="a"*40),
                                  self.program,5)
        self.assertIsNone(ranked["recommended_next"])

    def test_reference_not_selected_does_not_invent_i3_recommendation(self):
        reg=copy.deepcopy(self.registry)
        reg.pop("reference_generation")
        self.write(rc.REGISTRY,reg)
        state=rc.research_state(self.root,at_sha="a"*40)
        ranked=rc.recommendations(state,self.program,5)
        self.assertEqual(ranked["status"],"PROVISIONAL_RESEARCH_ADVICE")
        self.assertIsNone(ranked["recommended_next"])
        self.assertEqual(ranked["total_proposals"],0)
        self.assertEqual(state["i3_scientific_route"]["status"],
                         "I3_SOURCE_REVIEW_REQUIRED")

    def test_not_an_independent_review_or_source_graph_approval(self):
        state=rc.research_state(self.root,at_sha="a"*40)
        ranked=rc.recommendations(state,self.program,5)
        self.assertEqual(state["questions"],[])
        self.assertEqual(state["gates"],[])
        self.assertEqual(state["findings"],[])
        self.assertTrue(ranked["recommended_next"]["human_review_required"])
        self.assertEqual(ranked["recommended_next"]["unverified_sources"],
                         [rc.I3_ROUTING_FILE])
        self.assertNotIn("SCIENTIFICALLY_ESTABLISHED",
                         json.dumps(ranked,sort_keys=True))


if __name__ == "__main__":
    unittest.main()
