"""Natural WAL owner sensor is strictly observational."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json,subprocess,sys,unittest
ROOT=Path(__file__).resolve().parents[2]
class OwnerNonInterference(unittest.TestCase):
    def test_same_natural_birth_with_without_owner_observation(self):
        with TemporaryDirectory() as temp:
            a=Path(temp)/"baseline";b=Path(temp)/"observed"
            for out,extra in ((a,()),(b,("--observe-owner-digests",))):
                run=subprocess.run([sys.executable,str(ROOT/"tools/run_i1_world_preset.py"),
                    "--preset","oasis","--seed","246","--steps","12","--lives","1","--custody","wal",
                    "--output-dir",str(out),*extra],cwd=ROOT,capture_output=True,text=True,timeout=180)
                self.assertEqual(run.returncode,0,run.stdout+"\n"+run.stderr)
            ar=json.loads((a/"report.json").read_text())
            br=json.loads((b/"report.json").read_text())
            self.assertEqual((a/"life-01.wal").read_bytes(),(b/"life-01.wal").read_bytes())
            self.assertEqual(ar["lives"][0]["journal_head"],br["lives"][0]["journal_head"])
            for plain,obs in zip(ar["lives"][0]["steps"],br["lives"][0]["steps"]):
                sensor=obs.pop("owner_observation")
                self.assertEqual(plain,obs)
                self.assertEqual(set(sensor["before"]),set(sensor["after"]))
                self.assertEqual(set(sensor["before"]),
                    {"value_needs","causal_model","perception","metacognition_health","slow_history"})
                self.assertTrue(all(len(x)==64 for x in sensor["after"].values()))
