"""A1 M11 decision join: adversarial failures must never establish exposure."""
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate


class A1DecisionJoinTests(unittest.TestCase):
    def test_m11_stage8_alignment_and_adversarial_rejection(self):
        with TemporaryDirectory() as d:
            generated = Path(d) / "generated"
            generate(generated)
            program = r"""
from copy import deepcopy
from i1_eco_a1_decision_join import verify_decision_alignment

ev = [
 {"kind":"td_update_published", "t_monde":1,
  "data":{"updated_signatures":["primitive:attendre"]}},
 {"kind":"stage8_option_evaluation", "t_monde":2, "cycle":1,
  "data":{"option_ref":"opt","learning_signature":"primitive:attendre",
          "learned_value_status":"unlearned","learned_value":None}},
 {"kind":"competition_cycle","t_monde":2,"cycle":1,
  "data":{"traces":[{"option_ref":"opt"}]}},
 {"kind":"command_admitted", "t_monde":1,
  "data":{"option_ref":"a","primitive":"attendre","command_hash":"h1"}},
 {"kind":"command_experienced", "t_monde":1,
  "primitive":"attendre","command_hash":"h1"},
 {"kind":"command_admitted", "t_monde":2,
  "data":{"option_ref":"opt","primitive":"attendre","command_hash":"h2"}},
 {"kind":"command_experienced", "t_monde":2,
  "primitive":"attendre","command_hash":"h2"},
]
read = {"source":"stage8_direct","step":2,"cycle":1,
        "option_ref":"opt","signature":"primitive:attendre",
        "original_status":"learned","original_value":2.0,
        "original_evidence":0.5,"update_count":2,"masked":True}
report=verify_decision_alignment(
    events=ev, reads=[read], adapters=[],
    mode="td_read_masked", generation=2)
assert report["stage8_direct_joined"] == 1
assert report["masked_read_count"] == 1
assert report["scope"].startswith("M11_ANCHORED_EXTERNAL")
def fails(events, reads, adapters, mode):
    try:
        verify_decision_alignment(
            events=events,reads=reads,adapters=adapters,
            mode=mode,generation=2)
    except ValueError:
        return
    raise AssertionError("adversarial input accepted")
bad = deepcopy(ev)
bad[1]["data"]["learned_value_status"]="learned"
fails(bad, [read], [], "td_read_masked")
bad = deepcopy(ev)
bad[0]["data"]["updated_signatures"] = ["other"]
fails(bad, [read], [], "td_read_masked")
bad = deepcopy(ev)
bad[2]["data"]["traces"]=[]
fails(bad, [read], [], "td_read_masked")
badread = dict(read, option_ref="forged")
fails(ev, [badread], [], "td_read_masked")
badread = dict(read, masked=False)
fails(ev, [badread], [], "td_read_masked")
badread = dict(read, original_value=float("nan"))
fails(ev, [badread], [], "td_read_masked")
bad = deepcopy(ev)
bad[5]["data"]["command_hash"] = "wrong"
fails(bad, [read], [], "td_read_masked")
"""
            env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
                       PYTHONPATH=os.pathsep.join((
                           str(generated), str(ROOT / "src"),
                           str(ROOT / "tools"))))
            run = subprocess.run(
                [sys.executable, "-B", "-c", program],
                cwd=ROOT, env=env, text=True,
                capture_output=True, timeout=120)
            self.assertEqual(run.returncode, 0,
                             run.stdout + run.stderr)


if __name__ == "__main__":
    unittest.main()
