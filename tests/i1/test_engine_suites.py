"""The suite executor must obey the engine's own executable contract."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from run_engine_checks import plan


class EngineSuiteContractTests(unittest.TestCase):
    def test_current_i1_test_suites_are_declared(self):
        expected = {"structure", "smoke", "full", "m11", "source"}
        contract = json.loads((ROOT / "src/i1/engine.json").read_text())
        self.assertEqual(set(contract["validation"]["suites"]), expected)
        for name in expected:
            with self.subTest(suite=name):
                planned = plan("I1", name)
                self.assertTrue(planned)

    def test_smoke_and_full_contracts_supply_required_junit_paths(self):
        for suite in ("smoke", "full"):
            with self.subTest(suite=suite):
                commands = plan("I1", suite)
                self.assertEqual(len(commands), 1)
                argv = commands[0]
                self.assertEqual(argv[0], "scripts/test_i1_ci.py")
                self.assertEqual(argv.count("--junit"), 1)
                target = argv[argv.index("--junit") + 1]
                self.assertTrue(target.startswith("reports/i1-"))
                self.assertTrue(target.endswith(".xml"))

    def test_only_active_registered_generation_runs(self):
        for engine in ("I0", "I2", "experimental", "i1"):
            with self.subTest(engine=engine), self.assertRaises(ValueError):
                plan(engine, "structure")
        with self.assertRaises(ValueError):
            plan("I1", "unknown_suite")

    def test_script_escape_or_disallowed_module_is_rejected(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "config").mkdir()
            (root / "src/i1").mkdir(parents=True)
            (root / "src/i1/lab").mkdir()
            (root / "src/i1/runtime").mkdir()
            (root / "docs/engines/i1").mkdir(parents=True)
            (root / "tests/i1").mkdir(parents=True)
            (root / "scripts").mkdir()
            for item in ("check_engine_repository.py", "check_engine_contracts.py"):
                (root / "scripts" / item).write_text("# placeholder\n")
            (root / "config/engine-registry.json").write_bytes(
                (ROOT / "config/engine-registry.json").read_bytes())
            contract = json.loads((ROOT / "src/i1/engine.json").read_text())
            for argv in (["../private.py", "arg"], ["-m", "subprocess", "--test"]):
                with self.subTest(argv=argv):
                    contract["validation"]["suites"]["structure"] = [argv]
                    (root / "src/i1/engine.json").write_text(json.dumps(contract))
                    with self.assertRaises(ValueError):
                        plan("I1", "structure", root=root)


if __name__ == "__main__":
    unittest.main()
