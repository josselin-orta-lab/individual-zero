"""Generated-I1 contract tests of the existing first-person owner (#341)."""
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate


class LivedSite341(unittest.TestCase):
    def test_generated_i1_owner(self):
        with TemporaryDirectory() as directory:
            out = Path(directory) / "generated"
            generate(out)
            code = r"""
from i1.experimental.lived_water import I1LivedWaterOwner
from i1.experimental.witnessed_site_samples import site_samples
from dataclasses import FrozenInstanceError
from types import SimpleNamespace

w = I1LivedWaterOwner(life_id="i1:test", enabled=True)
def observe(sent, before, later, first, followup):
    w.record_applied(sent_world_step=sent, before_water=before, x=2, y=3,
                     command_hash="command", option_ref="option",
                     first_capture_hash=first)
    return w.observe_followup(observed_world_step=sent+1, x=2, y=3,
                              observed_water=later, current_water_source=True,
                              followup_capture_hash=followup, paid_uc=True)
assert observe(1, 10, 15, "first", "later")["admitted"]
assert observe(3, 20, 22, "first2", "later2")["admitted"]
samples = site_samples(w, life_id="i1:test", site=(2,3), now_step=4)
assert tuple(s.observed_gain for s in samples) == (5.0, 2.0)
assert site_samples(w, life_id="i1:test", site=(1,1), now_step=4) == ()
try:
    samples[0].observed_gain = 99
except FrozenInstanceError:
    pass
else:
    raise AssertionError("sample must be immutable")
for kwargs in ({"life_id":"i1:other"}, {"now_step":3}, {"site":(True, 3)}):
    k = dict(life_id="i1:test", site=(2,3), now_step=4)
    k.update(kwargs)
    try: site_samples(w, **k)
    except ValueError: pass
    else: raise AssertionError("invalid first-person request accepted")

impostor = SimpleNamespace(life_id="i1:test", enabled=True, examples=w.examples)
try:
    site_samples(impostor, life_id="i1:test", site=(2,3), now_step=4)
except ValueError: pass
else: raise AssertionError("unowned examples accepted")

# A corrupted duplicate-capture record must never turn into evidence.
w._examples[1]["followup_capture_hash"] = "first2"
try:
    site_samples(w, life_id="i1:test", site=(2,3), now_step=4)
except ValueError: pass
else: raise AssertionError("identical capture receipts accepted")
print("I1_341_OK")
"""
            result = subprocess.run(
                [sys.executable, "-B", "-c", code],
                env={"PYTHONPATH": str(out) + ":" + str(ROOT / "src"),
                     "PYTHONDONTWRITEBYTECODE": "1"},
                cwd=ROOT, text=True, capture_output=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
