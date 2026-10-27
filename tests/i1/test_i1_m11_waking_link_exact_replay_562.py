"""#562: read-only exact replay of historical wake-link predicate counts.

The observer exports authenticated post-commit Memory images as usual. Capture
these images in the operator process only, and replay the exact legacy any()
predicate over each step's published paid waking links. Compare complete M11
reports with an uninstrumented independently born twin.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[2]
PROGRAM = r'''
import json
import sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path.cwd() / "tools"))
import run_i1_world_preset as runner
from i1_m11_memory_image import CommittedMemoryImage

mode, output = sys.argv[1:]
original = CommittedMemoryImage.after_step
images = []

def capture(self, owner, *, episode_count):
    result = original(self, owner, episode_count=episode_count)
    # Detached committed image; never reaches Memory or its decision policy.
    images.append(result["episodes"])
    return result

if mode == "observer":
    with patch.object(CommittedMemoryImage, "after_step", capture):
        report = runner.execute(
            preset_name="empty-land", seed=246, steps=24,
            lives=1, custody="m11", output_dir=Path(output))
elif mode == "reference":
    report = runner.execute(
        preset_name="empty-land", seed=246, steps=24,
        lives=1, custody="m11", output_dir=Path(output))
else:
    raise ValueError("unrecognized experiment")

if mode == "observer":
    steps = report["lives"][0]["steps"]
    assert len(steps) == len(images)
    inspected = 0
    linked = 0
    upper = 0
    for step, episodes in zip(steps, images):
        links = step["sleep_site_recall_custody_467"]["waking_links"]
        for link in links:
            linked += 1
            upper += len(episodes)
            matches = 0
            for episode in episodes:
                inspected += 1
                if (link["waking_cue_ref"] in episode["event_refs"]
                    and episode["id"] == link["waking_cue_episode_ref"]):
                    matches += 1
                    break
            assert matches == 1, (
                "original waking-link provenance unexpectedly unproven",
                link["waking_cue_ref"], link["waking_cue_episode_ref"])
    assert linked > 0, "natural reference preset lost its wake-link cohort"
    assert 0 < inspected <= upper
    print("I1_EXACT_WAKE_LINK_WORK_562=" + json.dumps({
        "evidence": "natural-M11-operator-replay",
        "steps": len(steps),
        "links": linked,
        "legacy_episode_predicates_replayed": inspected,
        "all_episode_upper_bound": upper,
        "no_cognitive_change": True,
        "no_timing_claim": True,
    }, sort_keys=True))
'''

class ExactNaturalWakeLinkReplay562(unittest.TestCase):
    def test_exact_short_circuit_work_and_complete_report_noninterference(self):
        with TemporaryDirectory() as tmp:
            reports = []
            for mode in ("reference", "observer"):
                out = Path(tmp) / mode
                p = subprocess.run(
                    [sys.executable, "-c", PROGRAM, mode, str(out)],
                    cwd=ROOT, env=os.environ.copy(),
                    capture_output=True, text=True, timeout=240)
                self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
                report = json.loads((out / "report.json").read_text())
                self.assertEqual(
                    report["status"], "COMPLETED_WITHOUT_SCIENTIFIC_VERDICT")
                reports.append(report)
                if mode == "observer":
                    row = [s for s in p.stdout.splitlines()
                           if s.startswith("I1_EXACT_WAKE_LINK_WORK_562=")]
                    self.assertEqual(len(row), 1, p.stdout)
                    result = json.loads(row[0].split("=", 1)[1])
                    self.assertGreater(result["links"], 0)
                    self.assertLessEqual(
                        result["legacy_episode_predicates_replayed"],
                        result["all_episode_upper_bound"])
                    print(row[0])
            self.assertEqual(reports[0], reports[1],
                             "passive observation changed M11 life report")

if __name__ == "__main__":
    unittest.main()
