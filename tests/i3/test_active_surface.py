"""Static guards for the I3 active-surface contract.

This test protects navigation and stage separation. It does not execute a
scientific falsifier or create any World/life.
"""
from __future__ import annotations

import ast
import importlib.util
import json
import re
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
I3 = ROOT / "src" / "i3"
MANIFEST = I3 / "ACTIVE_SURFACE.json"


class ActiveSurfaceContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(MANIFEST.read_text())

    def test_manifest_declares_current_governance(self):
        self.assertEqual(self.data["schema"], "i3-active-surface/v1")
        self.assertEqual(self.data["current_stage"], "2.1 replay gate")
        self.assertEqual(self.data["canonical_status"], "REPLAY_GATE_CAPACITY_SHOWN")
        self.assertFalse(self.data["governance"]["i3_registered"])
        self.assertEqual(
            self.data["governance"]["adr_0017_world_opening_moratorium"], "LIFTED_2026_11_09")
        self.assertTrue(self.data["governance"]["fresh_lived_worlds_allowed"])
        self.assertTrue(self.data["governance"]["adr_0017_owner_lift_recorded"])
        self.assertEqual(self.data["governance"]["authorized_fresh_lived_scope"],
                         "FROZEN_STAGE2_1_DEVELOPMENT_80_81_ONLY")
        self.assertFalse(self.data["governance"]["scientific_gate_authorized"])
        self.assertEqual(self.data["governance"]["adr_0019"], "ACCEPTED_2026_11_09")
        self.assertEqual(self.data["governance"]["pre_lift_replay_runtime_support_allowed"], "ENGINEERING_COHORT_ONLY")

    def test_every_declared_active_or_compatibility_path_exists(self):
        for key in ("active_science", "active_engineering", "stage1_compatibility_only"):
            for rel in self.data[key]:
                self.assertTrue((ROOT / rel).is_file(), f"missing {key}: {rel}")

    def test_active_stage2_python_does_not_import_stage1_lab_helpers(self):
        paths = [
            p for p in self.data["active_science"]
            if p.endswith(".py")
        ] + [
            p for p in self.data["active_engineering"]
            if p.endswith(".py") and p.startswith("src/i3/")
        ]
        offenders = []
        for rel in paths:
            tree = ast.parse((ROOT / rel).read_text(), filename=rel)
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    if "stage1_" in module:
                        offenders.append((rel, module))
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        if "stage1_" in alias.name:
                            offenders.append((rel, alias.name))
        self.assertEqual(offenders, [])

    def test_replay_gate_dispatch_remains_world_bound_after_owner_lift(self):
        # Owner-lifted scientific dispatch still uses exactly the same
        # WorldSpec-bound admission guard. The synthetic pre-lift condition
        # remains fail-closed in tests; the live pilot is not a unit test.
        runtime = (I3 / "runtime" / "life.py").read_text()
        self.assertIn("p13_replay_gate_v1", runtime)
        self.assertIn("p13_replay_gate_zero_perceived_cost_v1", runtime)
        self.assertLess(runtime.index("verify_admission(admission, spec)"),
                        runtime.index("world = World(spec)"))
        guard = (ROOT / "tests" / "i3" / "test_stage2_exact_transport.py").read_text()
        for name in ("test_every_scientific_cohort_fails_closed_before_any_world",
                     "test_status_ledger_without_lift_or_with_wrong_fingerprint_fails_closed",
                     "test_scientific_execute_fails_before_creating_anything",
                     "test_runtime_refuses_missing_forged_or_misbound_tickets",
                     "test_only_the_guard_mints_tickets"):
            self.assertIn(f"def {name}(", guard)
        self.assertEqual(self.data["governance"]["pre_lift_replay_runtime_support_allowed"],
                         "ENGINEERING_COHORT_ONLY")
        self.assertEqual(self.data["governance"]["adr_0017_world_opening_moratorium"], "LIFTED_2026_11_09")

    def test_status_points_to_canonical_software_result(self):
        status = (I3 / "docs" / "STATUS.md").read_text()
        self.assertIn("REPLAY_GATE_CAPACITY_SHOWN", status)
        self.assertIn("ADR-0017 OWNER LIFT: Stage-2.1 transport "
                      "dcada9e221f79b9450a4f05fecd20e60ac6595bb306aa871f29e45aefea0b6f1",
                      status)

    def test_archived_stage1_modules_resolve_and_active_paths_are_absent(self):
        archived = [
            Path(p) for p in self.data["stage1_compatibility_only"]
            if p.startswith("src/i3/archive/stage1/") and p.endswith(".py")
        ]
        self.assertEqual(len(archived), 31)
        for rel in archived:
            self.assertTrue((ROOT / rel).is_file(), str(rel))
            parts = rel.parts
            self.assertEqual(parts[2:4], ("archive", "stage1"))
            old_path = I3 / parts[4] / parts[-1]
            self.assertFalse(old_path.exists(), f"duplicate active candidate: {old_path}")
            dotted = ".".join(rel.with_suffix("").parts[1:])
            self.assertIsNotNone(importlib.util.find_spec(dotted), dotted)

    def test_repointed_python_imports_never_reference_removed_candidate_paths(self):
        archived = [
            Path(p) for p in self.data["stage1_compatibility_only"]
            if p.startswith("src/i3/archive/stage1/") and p.endswith(".py")
        ]
        old_modules = {
            f"i3.{p.parts[4]}.{p.stem}" for p in archived
        }
        offenders = []
        for root in (I3, ROOT / "tests" / "i3"):
            for path in root.rglob("*.py"):
                parsed = ast.parse(path.read_text(), filename=str(path))
                for node in ast.walk(parsed):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if alias.name in old_modules:
                                offenders.append((str(path), alias.name))
                    elif isinstance(node, ast.ImportFrom):
                        mod = node.module or ""
                        if mod in old_modules:
                            offenders.append((str(path), mod))
                        for alias in node.names:
                            if f"{mod}.{alias.name}" in old_modules:
                                offenders.append((str(path), f"{mod}.{alias.name}"))
        self.assertEqual(offenders, [])

    def test_retained_tests_do_not_open_removed_candidate_source_paths(self):
        archived = [
            Path(p) for p in self.data["stage1_compatibility_only"]
            if p.startswith("src/i3/archive/stage1/") and p.endswith(".py")
        ]
        legacy_fragments = {
            f"i3/{rel.parts[4]}/{rel.name}" for rel in archived
        }
        stale = []
        for path in (ROOT / "tests" / "i3").rglob("*.py"):
            tree = ast.parse(path.read_text(), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    for old in legacy_fragments:
                        if old in node.value:
                            stale.append((str(path), old))
        self.assertEqual(stale, [])

    def test_active_lab_does_not_depend_on_closed_stage1_modules(self):
        offenders = []
        for path in (I3 / "lab").glob("*.py"):
            tree = ast.parse(path.read_text(), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.startswith("i3.archive.stage1"):
                            offenders.append((path.name, alias.name))
                elif isinstance(node, ast.ImportFrom):
                    if (node.module or "").startswith("i3.archive.stage1"):
                        offenders.append((path.name, node.module))
        self.assertEqual(offenders, [], "historical dependencies belong in archive")

    def test_closed_stage2_68_69_runner_is_not_active(self):
        archived = "src/i3/archive/stage2/development_68_69.py"
        self.assertEqual(self.data["archived_noncanonical_transport"], [archived])
        self.assertTrue((ROOT / archived).is_file())
        self.assertFalse((I3 / "lab" / "stage2_replay_gate_development_pilot.py").exists())
        self.assertNotIn(archived, self.data["active_engineering"])

    def test_key_historical_evidence_links_resolve(self):
        pairs = (
            ("src/i3/docs/studies/stage1-affordable-projection-probes/RESULTS.md",
             "../../../archive/stage1/lab/stage1_affordable_projection_probes.py"),
            ("src/i3/docs/studies/stage1-candidate-h-development-58-59/RESULTS.md",
             "PROTOCOL.md"),
        )
        for source, rel in pairs:
            text = (ROOT / source).read_text()
            self.assertIn(f"]({rel})", text)
            self.assertTrue(((ROOT / source).parent / rel).is_file(), source)

    def test_every_i3_module_import_resolves_statically(self):
        import importlib.util
        modules = {"i3"}
        for path in I3.rglob("*.py"):
            rel = path.relative_to(I3).with_suffix("")
            parts = rel.parts
            if parts[-1] == "__init__":
                parts = parts[:-1]
            modules.add(".".join(("i3", *parts)))
        for path in I3.rglob("*.py"):
            rel = path.relative_to(I3).with_suffix("")
            parts = rel.parts
            package = ".".join(("i3", *parts[:-1]))
            tree = ast.parse(path.read_text(), filename=str(path))
            for node in ast.walk(tree):
                targets = []
                if isinstance(node, ast.Import):
                    targets = [a.name for a in node.names]
                elif isinstance(node, ast.ImportFrom):
                    ref = "." * node.level + (node.module or "")
                    resolved = (importlib.util.resolve_name(ref, package)
                                if node.level else (node.module or ""))
                    targets = [resolved]
                for target in targets:
                    if target.startswith("i3."):
                        self.assertIn(target, modules, f"{path}: missing {target}")

    def test_i3_internal_markdown_links_resolve(self):
        broken = []
        for file in I3.rglob("*.md"):
            for match in re.finditer(r"\]\(([^)]+)\)", file.read_text()):
                href = match.group(1).split("#", 1)[0].split(" ", 1)[0]
                if (not href or "://" in href or href.startswith("mailto:")
                        or "{" in href or "}" in href):
                    continue
                target = (file.parent / href).resolve()
                if not target.is_relative_to(I3):
                    continue  # Root-level ADRs/archives belong to the repo, not I3.
                if target.suffix == ".gz":
                    continue  # Exact binary evidence is checked by its hash custody.
                if not target.exists():
                    broken.append((str(file.relative_to(ROOT)), href))
        self.assertEqual(broken, [])

    def test_active_runtime_loads_historical_candidates_lazily(self):
        runtime = ast.parse((I3 / "runtime" / "life.py").read_text())
        top_level = []
        for node in runtime.body:
            if isinstance(node, ast.ImportFrom):
                top_level.append(node.module or "")
            elif isinstance(node, ast.Import):
                top_level.extend(a.name for a in node.names)
        self.assertFalse(
            any(name.startswith("i3.archive.stage1") for name in top_level),
            "reference runtime must not eagerly depend on closed Stage-1 code")

    def test_stage1_compatibility_set_is_not_current_science(self):
        current = set(self.data["active_science"])
        compatibility = set(self.data["stage1_compatibility_only"])
        self.assertTrue(compatibility)
        self.assertTrue(current.isdisjoint(compatibility))


if __name__ == "__main__":
    unittest.main()
