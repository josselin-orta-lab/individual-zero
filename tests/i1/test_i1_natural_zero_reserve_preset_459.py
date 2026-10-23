"""#459: read-only natural M11 depletion postmortem, no scripted commands."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class NaturalM11Depletion459(unittest.TestCase):
    def test_registered_empty_land_after_physical_exhaustion(self):
        with TemporaryDirectory(prefix="i1-459-") as temp:
            code = r"""
from pathlib import Path
from tempfile import TemporaryDirectory
from run_i1_world_preset import execute
from i1lab.sqlite_life_store import SQLiteLifeLedger

with TemporaryDirectory(prefix="i1-459-empty-") as d:
    output = Path(d) / "natural-m11"
    report = execute(
        preset_name="empty-land", seed=246, steps=55,
        lives=1, custody="m11", output_dir=output,
    )
    assert report["status"] == "COMPLETED_WITHOUT_SCIENTIFIC_VERDICT", report
    assert report["environment"]["world_physics_digest_kind"] == "input_prebirth_config"
    life = report["lives"][0]
    assert life["effective_birth_physics"]["zero_reserve_lethal"] is True
    assert "v3-zero-reserve-lethal" in life["effective_birth_physics"]["version"]
    assert life["effective_birth_physics"]["digest"] != report["environment"]["world_physics_digest"]
    assert life["steps"]
    assert len(life["steps"]) <= 55
    assert [row["generation"] for row in life["steps"]] == list(
        range(1, len(life["steps"]) + 1))
    assert all(row["body_after"]["integrity"] > 0 for row in life["steps"])
    assert all(row["terminal_reasons"] == [] for row in life["steps"][:-1])
    last = life["steps"][-1]
    audit = SQLiteLifeLedger.audit_read_only(
        path=str(output / life["custody_file"]),
        expected_individual_id=life["individual_id"],
    )
    assert audit.generation == len(life["steps"])
    assert audit.journal_head == life["journal_head"]
    if life["lifecycle"] == "dead":
        assert last["lifecycle"] == "dead"
        assert any(x in last["terminal_reasons"]
                   for x in ("zero_water", "zero_food")), last
        assert (last["body_after"]["water"] == 0
                or last["body_after"]["food"] == 0)
        assert not audit.may_recover
    else:
        # Missing physical exposure is not a false forced death.
        assert life["lifecycle"] == "active"
        assert all(row["body_after"]["water"] > 0
                   and row["body_after"]["food"] > 0
                   for row in life["steps"])
    print("I1_459_M11_OBSERVED", life["lifecycle"], len(life["steps"]),
          last["terminal_reasons"], last["body_after"])
"""
            # The world runner creates its own generated I1 fork.
            process = subprocess.run(
                [sys.executable, "-B", "-c", code],
                env={"PYTHONPATH": str(ROOT / "tools") + ":" + str(ROOT / "src")},
                cwd=ROOT, text=True, capture_output=True, check=False,
            )
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertIn("I1_459_M11_OBSERVED", process.stdout)


if __name__ == "__main__":
    unittest.main()
