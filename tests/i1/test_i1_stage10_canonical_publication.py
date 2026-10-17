"""Exercise the actual Stage10 publication entrypoint (issue #255).

An invalid candidate is intentionally deferred before any publication commit.
This detects the old local-variable UnboundLocalError for both runtime types.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate


class Stage10CanonicalPublicationTests(unittest.TestCase):
    def test_parity_accepts_only_exact_assignment_move(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("i1_parity", ROOT / "scripts/test_i1_artifact_parity.py")
        parity = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(parity)
        before = (b"    def publish(self):\n"
                  b"        coordinator = Stage10PublicationCoordinator(\n"
                  b"            owner=True)\n"
                  b"        canonical = type(self).__name__ == \"I1Runtime\"\n"
                  b"        if ((not canonical and candidate.get(\"forms\")\n"
                  b"            return None\n")
        after = (b"    def publish(self):\n"
                 b"        canonical = type(self).__name__ == \"I1Runtime\"\n"
                 b"        coordinator = Stage10PublicationCoordinator(\n"
                 b"            owner=True)\n"
                 b"        if ((not canonical and candidate.get(\"forms\")\n"
                 b"            return None\n")
        self.assertTrue(parity._approved_stage10_initialization_move(before, after))
        self.assertFalse(parity._approved_stage10_initialization_move(before, after + b" # other change"))
        self.assertFalse(parity._approved_stage10_initialization_move(before, before))

    def test_publication_selects_exact_owner_views_before_validating_candidate(self):
        with TemporaryDirectory() as directory:
            generated = Path(directory) / "generated"
            generate(generated)
            code = """
from types import SimpleNamespace
from unittest.mock import patch
import i1lab.stage10_runtime as stage10

seen = []
class Coordinator:
    REQUIRED = frozenset({"value_needs", "causal_model",
                          "perception", "metacognition_health"})
    def __init__(self, *, journal, history, slot, owners):
        seen.append(owners)
class Transaction:
    id = "regression-not-published"
    def validated_candidate(self, *, validator):
        candidate = {"forms": {"extra-unregistered-owner": []}}
        assert validator(candidate)
        return candidate
def owner(owner_id):
    return SimpleNamespace(owner_id=owner_id)
def exercise(name):
    events = []
    fake = type(name, (), {})()
    fake.journal = object()
    fake.value_needs = owner("value_and_needs")
    fake.slow_history = SimpleNamespace(
        read_committed=lambda: {"forms": {}})
    fake.consolidation = object()
    fake._meta_custody = owner("metacognition_health")
    fake.causal_model = owner("causal_model")
    fake.stage3 = SimpleNamespace(perception=owner("perception"))
    fake._i1_active_owner_views = {
        key: owner(key) for key in (
            "metacognition_health", "causal_model", "perception")}
    fake._write = lambda **event: events.append(event)
    with patch.object(stage10, "Stage10PublicationCoordinator", Coordinator):
        stage10.Stage10Runtime._publish_live_consolidation(
            fake, tx=Transaction(), world_step=1)
    assert len(events) == 1, events
    assert events[0]["kind"] == "stage10_consolidation_publication_deferred"
    assert events[0]["data"]["reason"] == "active_form_rebase_not_implemented"
    return fake

natural = exercise("I1Runtime")
assert seen[0]["perception"] is natural._i1_active_owner_views["perception"]
assert seen[0]["causal_model"] is natural._i1_active_owner_views["causal_model"]
assert seen[0]["metacognition_health"] is natural._i1_active_owner_views["metacognition_health"]
generic = exercise("Stage10Runtime")
assert seen[1]["perception"] is generic.stage3.perception
assert seen[1]["causal_model"] is generic.causal_model
assert seen[1]["metacognition_health"] is generic._meta_custody
print("STAGE10_CANONICAL_OWNER_REGRESSION_OK")
"""
            process = subprocess.run(
                [sys.executable, "-c", code], capture_output=True,
                text=True, check=False, env={
                    "PYTHONPATH": str(generated) + ":" + str(ROOT / "src"),
                })
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertIn("STAGE10_CANONICAL_OWNER_REGRESSION_OK", process.stdout)


if __name__ == "__main__":
    unittest.main()
