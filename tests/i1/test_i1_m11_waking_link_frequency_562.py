"""#562: frequency, not just worst-case complexity, of waking-link scans.

Observe unforced mortal M11 runs using the authentic world-preset runner.
The output is a read-only scientific diagnostic, not a new I1 input or a
proof of long-life performance. Scan volume is an UPPER BOUND because the
legacy check short-circuits on a matching closed episode.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[2]
PRESETS = (
    ("empty-land", 246, 24),
    ("oasis", 247, 24),
    ("hazard-edge", 248, 24),
)


def summarize_natural_waking_link_work(report, *, preset, requested_steps):
    assert report["status"] == "COMPLETED_WITHOUT_SCIENTIFIC_VERDICT"
    assert len(report["lives"]) == 1
    steps = report["lives"][0]["steps"]
    assert 1 <= len(steps) <= requested_steps
    closed_count = 0
    total_links = 0
    link_steps = 0
    scan_candidate_upper_bound = 0
    close_counts = []
    for ordinal, step in enumerate(steps, 1):
        assert step["world_step"] == ordinal
        closure = step["autobiographical_sleep_custody_467"][
            "episodes_closed_during_step"]
        assert type(closure) is list
        closed_count += len(closure)
        close_counts.append(closed_count)
        audit = step["sleep_site_recall_custody_467"]
        count = audit["waking_link_count"]
        links = audit["waking_links"]
        assert type(count) is int and count >= 0
        assert type(links) is list and count == len(links)
        assert all(type(link["waking_cue_ref"]) is str
                   and type(link["waking_cue_episode_ref"]) is str
                   for link in links)
        total_links += count
        link_steps += int(count > 0)
        # The reference any(...) potentially examines every closed
        # episode per paid link, but may stop at an earlier match.
        scan_candidate_upper_bound += count * closed_count
    return {
        "preset": preset,
        "requested_world_steps": requested_steps,
        "observed_world_steps": len(steps),
        "closed_episodes_at_end": closed_count,
        "max_closed_episodes": max(close_counts),
        "paid_waking_link_checks": total_links,
        "steps_with_waking_link_checks": link_steps,
        "max_historical_episode_predicates": scan_candidate_upper_bound,
        "diagnostic_is_upper_bound_not_observed_scan_count": True,
    }


class NaturalWakingLinkScanFrequency562(unittest.TestCase):
    def test_genuine_m11_paid_link_frequency_no_forced_behavior(self):
        with TemporaryDirectory() as folder:
            rows = []
            for preset, seed, requested_steps in PRESETS:
                output = Path(folder) / preset
                proc = subprocess.run([
                    sys.executable,
                    str(ROOT / "tools/run_i1_world_preset.py"),
                    "--preset", preset,
                    "--seed", str(seed),
                    "--steps", str(requested_steps),
                    "--lives", "1", "--custody", "m11",
                    "--output-dir", str(output),
                ], cwd=ROOT, env=os.environ.copy(), text=True,
                   capture_output=True, timeout=300)
                self.assertEqual(proc.returncode, 0,
                                 proc.stdout + proc.stderr)
                report_path = output / "report.json"
                self.assertTrue(report_path.is_file())
                report = json.loads(report_path.read_text())
                row = summarize_natural_waking_link_work(
                    report, preset=preset, requested_steps=requested_steps)
                self.assertLessEqual(row["steps_with_waking_link_checks"],
                                     row["observed_world_steps"])
                self.assertGreaterEqual(
                    row["max_historical_episode_predicates"],
                    row["paid_waking_link_checks"]
                    if row["closed_episodes_at_end"] else 0,
                )
                rows.append(row)
            self.assertEqual(
                [row["preset"] for row in rows],
                [preset for preset, _, _ in PRESETS])
            self.assertGreater(sum(row["observed_world_steps"] for row in rows),
                               0)
            print("I1_NATURAL_WAKING_LINK_SCAN_FREQ_562=" + json.dumps({
                "evidence": "unforced-m11-observer-only",
                "no_claim_of_cognitive_effect": True,
                "no_claim_of_realized_speedup": True,
                "rows": rows,
            }, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
