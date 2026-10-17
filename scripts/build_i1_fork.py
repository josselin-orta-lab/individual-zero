"""Build a separately importable I1 descendant without editing I0 or lab.

The checked-in src/i1 tree is the exact source snapshot from the approved
I0 main SHA. This build mechanically namespaces that copy and the complete
laboratory runtime in a separate output directory. No src/i0 or src/lab file
is written. The I1-generated WorldBody alone receives versioned physical deprivation
by default, and the generated mortal Stage11Sleep entrypoint activates the
natural sleep policy for every new I1 birth. Reference I0 and Lab are unchanged.

Output is disposable build code, not an archived living individual.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import shutil
import tokenize

SOURCE_MAIN_SHA = "8ce8711b2d5f86b184d66fcee1d95a3e39f30836"
SOURCE_ROOT = Path(__file__).resolve().parents[1] / "src"
GENERATED_SCHEMA = "i1-namespaced-source-build-v1"
IMPORTS = (
    (re.compile(r"(?m)^(\s*from\s+)i0(?=[.\s])"), r"\1i1"),
    (re.compile(r"(?m)^(\s*import\s+)i0(?=[.\s,])"), r"\1i1"),
    (re.compile(r"(?m)^(\s*from\s+)lab(?=[.\s])"), r"\1i1lab"),
    (re.compile(r"(?m)^(\s*import\s+)lab(?=[.\s,])"), r"\1i1lab"),
)
BIRTH_ID = re.compile(r'(?m)^(\s*individual_id\s*=\s*["\'])i0')


def rewrite(text: str) -> str:
    for pattern, replacement in IMPORTS:
        text = pattern.sub(replacement, text)
    return BIRTH_ID.sub(r"\1i1", text)



def i1_m11_bounded_journal_source(source: str) -> str:
    """Avoid whole-journal tuple materialization in I1 M11 and cold restore.

    Journal verification, hash checks, durable-intent fencing, state capture,
    commit ordering and published owner isolation remain unchanged.
    """
    substitutions = (
        (
            "        runtime.journal.append(\n",
            "        appended = runtime.journal.append(\n",
        ),
        (
            "        if runtime.journal.entries[-1].as_dict() != entry:\n",
            "        if appended.as_dict() != entry:\n",
        ),
        (
            'or len(runtime.journal.entries) != image["journal"]["count"]',
            'or runtime.journal.entry_count != image["journal"]["count"]',
        ),
        (
            "                or runtime.journal.entries\n",
            "                or runtime.journal.entry_count\n",
        ),
        (
            "                or base.journal_count != len(self._runtime.journal.entries)):\n",
            "                or base.journal_count != self._runtime.journal.entry_count):\n",
        ),
        (
            "                for event in candidate.journal.entries[base.journal_count:]\n",
            "                for event in candidate.journal.entries_since(base.journal_count)\n",
        ),
    )
    for before, after in substitutions:
        if source.count(before) != 1:
            raise ValueError("unreviewed I1 M11 journal-copy anchor")
        source = source.replace(before, after)
    return source


def i1_m11_active_publication_custody_source(source: str) -> str:
    """Generated M11 must preserve h <-> active Value/Needs identity.

    A torn or inconsistent publication cannot become the canonical current
    mortal state merely because both owner snapshots deserialize separately.
    Only the exact canonical natural I1 actor participates in this contract.
    """
    verification = '''def _verify_i1_active_publication_custody(runtime: Any) -> None:
    from .i1_natural_runtime import I1Runtime
    if type(runtime) is not I1Runtime:
        return
    from .i1_active_value_needs import validate_advisory_rows
    history = runtime.slow_history.read_committed()
    if type(history) is not dict or type(history.get("forms")) is not dict:
        raise RecoveryBlocked("missing canonical I1 consolidated active forms")
    forms = history["forms"]
    from .i1_cognitive_publication import (
        build_consolidated_owner_form, validate_owner_rows,
    )
    required = {"value_needs", "causal_model", "perception", "metacognition_health"}
    if set(forms) not in (set(), required):
        raise RecoveryBlocked("unapproved I1 active owner publication")
    expected = forms.get("value_needs", [])
    witnessed = history.get("procedural")
    if type(witnessed) is not list or any(type(row) is not dict for row in witnessed):
        raise RecoveryBlocked("invalid committed procedural source")
    if type(expected) is not list:
        raise RecoveryBlocked("invalid committed active Value/Needs form")
    validate_advisory_rows(expected)
    authorized = sorted(
        (row for row in witnessed if row.get("state") == "compiled_private"),
        key=lambda row: row["id"],
    )
    expected_bytes = canonical_causal_bytes(expected)
    if (expected_bytes != canonical_causal_bytes(authorized)
            or expected_bytes != canonical_causal_bytes(
                runtime.value_needs.active_observed_procedures()
            )):
        raise RecoveryBlocked("I1 active owner and consolidated history diverged")
    names = ("causal_model", "perception", "metacognition_health")
    for name in names:
        published = forms.get(name, [])
        # The recomputation is read-only and immediately serialized for
        # parity. Keep published owner snapshots detached elsewhere.
        recomputed = (
            build_consolidated_owner_form(history, name, detach_evidence=False)
            if forms else []
        )
        live = runtime._i1_active_owner_views[name].observed_consolidated()
        validate_owner_rows(name, published)
        validate_owner_rows(name, live)
        published_bytes = canonical_causal_bytes(published)
        if (published_bytes != canonical_causal_bytes(recomputed)
                or published_bytes != canonical_causal_bytes(live)):
            # An empty private history must NEVER conceal a live published
            # owner form. This parity applies before the first publication
            # and to every authentic later SQLite generation.
            raise RecoveryBlocked("I1 active owner differs from published lived evidence")


'''
    anchor = "def _runtime_image(runtime: Any, *, individual_id: str) -> dict[str, Any]:\n"
    if source.count(anchor) != 1:
        raise ValueError("unreviewed M11 registered owner capture")
    source = source.replace(anchor, verification + anchor)
    original_capture = "    image = capture_registered_current_state(\n"
    if source.count(original_capture) != 1:
        raise ValueError("unreviewed M11 owner image source")
    source = source.replace(
        original_capture,
        "    _verify_i1_active_publication_custody(runtime)\n" + original_capture,
    )
    cold_anchor = (
        "    # Complete ledger bytes correspond to the current *generation*, not any\n"
    )
    if source.count(cold_anchor) != 1:
        raise ValueError("unreviewed M11 restored owner sync boundary")
    return source.replace(
        cold_anchor,
        "    _verify_i1_active_publication_custody(runtime)\n" + cold_anchor,
    )


def generate(output: Path) -> dict[str, object]:
    output = output.resolve()
    # A mis-specified output must never clobber the checked-in cognition.
    if output == SOURCE_ROOT or SOURCE_ROOT in output.parents:
        raise ValueError("I1 build output must not be inside src/")
    if not (SOURCE_ROOT / "i0").is_dir() or not (SOURCE_ROOT / "i1").is_dir():
        raise ValueError("both baseline I0 and I1 source snapshot are required")
    if not (SOURCE_ROOT / "lab").is_dir():
        raise ValueError("independent laboratory runtime source unavailable")
    if output.exists() and any(output.iterdir()):
        raise FileExistsError("I1 output must be an empty directory")
    manifest: dict[str, object] = {
        "schema": GENERATED_SCHEMA,
        "i0_baseline_sha": SOURCE_MAIN_SHA,
        "build_mode": "independent_i1_and_i1lab_packages",
        "oracle_or_bench_transferred_into_individual": False,
        "files": {},
    }
    for input_package, output_package in (("i1", "i1"), ("lab", "i1lab")):
        source = SOURCE_ROOT / input_package
        dest = output / output_package
        for file in sorted(source.rglob("*.py")):
            relative = file.relative_to(source)
            if input_package == "i1" and relative.parts[0] == "runtime":
                continue  # Built into i1lab below, never twice in generated i1.
            if input_package == "lab" and relative.as_posix() in {"world.py", "journal.py", "journal_views.py", "consolidation_lived_evidence.py", "consolidation_postcut_journal.py", "sqlite_life_store.py", "sqlite_runtime_custody.py", "consolidation_publication.py", "stage10_runtime.py", "stage4_runtime.py", "stage11_runtime.py"}:
                continue  # Versioned native I1 world, journal and lived views.
            contents = file.read_text(encoding="utf-8")
            transformed = rewrite(contents)
            # Only i1_natural_runtime.I1Runtime installs the natural sleep
            # policy. Do not rewrite the common Stage11Sleep ancestor, which
            # would silently change historical A2.38/A2.39 ablation births.
            # I1-only M11 custody: admit ONLY the exact canonical I1
            # runtime, not any experimental Stage12 subclass with unknown
            # mutable owners or unregistered cold-state behavior. Retain the
            # existing exact Stage12 type and all M11 admission criteria.
            # Never alter the canonical src/lab or src/i0 M11 implementation.
            if output_package == "i1lab" and relative.as_posix() == "m11_transactional_mortal.py":
                required = "type(runtime) is Stage12Runtime"
                canonical = (
                    "(type(runtime) is Stage12Runtime "
                    "or type(runtime) is I1Runtime)"
                )
                if transformed.count(required) != 3:
                    raise ValueError("unreviewed I1 M11 runtime type gate")
                transformed = transformed.replace(required, canonical)
                import_anchor = "from .stage12_runtime import Stage12Runtime"
                if transformed.count(import_anchor) != 3:
                    raise ValueError("unreviewed I1 M11 local import scope")
                lines = transformed.splitlines(keepends=True)
                transformed = "".join(
                    line.replace(
                        import_anchor,
                        import_anchor + "\n"
                        + line[:len(line) - len(line.lstrip())]
                        + "from .i1_natural_runtime import I1Runtime",
                    ) if import_anchor in line else line
                    for line in lines
                )
                if transformed.count("from .i1_natural_runtime import I1Runtime") != 3:
                    raise ValueError("canonical I1 M11 import scopes not generated")
                # This private-copy walker must discover immutable proxies
                # in the I1/i1lab owner graph, not accidentally scan only I0.
                original_modules = 'mod.startswith("i0.") or mod.startswith("lab.")'
                if transformed.count(original_modules) != 1:
                    raise ValueError("unreviewed M11 frozen-proxy owner traversal")
                transformed = transformed.replace(
                    original_modules,
                    'mod.startswith("i1.") or mod.startswith("i1lab.")',
                )

                required_line = '        getattr(runtime, "_stage12_detector_policy", None),'
                if transformed.count(required_line) != 1:
                    raise ValueError("unreviewed I1 M11 constructor fingerprint")
                transformed = transformed.replace(
                    required_line,
                    required_line + '\n'
                    + '        getattr(runtime, "_i1_model_contract", None),',
                )
                # D1 water is a separate I1-only canonical cognitive owner.
                # Legacy I1 M11 birth hashes are unchanged when D1 is absent.
                cold_anchor = '        if (key == "metacognition_health"'
                if transformed.count(cold_anchor) != 1:
                    raise ValueError("unreviewed I1 water M11 cold owner hook")
                transformed = transformed.replace(
                    cold_anchor,
                    '        if key == "i1_lived_water_model":\n'
                    '            owner.install_m11_cold_state(\n'
                    '                deepcopy(value), capability=_M11_COLD_OWNER_TOKEN)\n'
                    '        elif (key == "metacognition_health"',
                )
                hash_anchor = (
                    '    return sha256_hex(canonical_causal_bytes('
                    '_contract_value(configuration)))'
                )
                if transformed.count(hash_anchor) != 1:
                    raise ValueError("unreviewed I1 M11 birth contract signature")
                transformed = transformed.replace(
                    hash_anchor,
                    '    if getattr(runtime, "_i1_water_contract", None) is not None:\n'
                    '        configuration = (*configuration,\n'
                    '            ("i1-water-firstperson-birth-v1", runtime._i1_water_contract))\n'
                    + hash_anchor,
                )
                # The canonical natural actor exposes three authoritative
                # owner views in the M11 roster. Their private cold installers
                # must receive the same authenticated M11 capability. Bind the
                # exact I1Runtime type in this separate cold-install function,
                # not only in birth/cold-factory admission scopes.
                cold_owner_anchor = (
                    '    current_owner_ids = {o.owner_id: o for o in runtime.causal_owners}\n'
                )
                if transformed.count(cold_owner_anchor) != 1:
                    raise ValueError("unreviewed M11 cold owner import scope")
                transformed = transformed.replace(
                    cold_owner_anchor,
                    '    from .i1_natural_runtime import I1Runtime\n'
                    + cold_owner_anchor,
                )
                cold_hook = '        if key == "i1_lived_water_model":'
                if transformed.count(cold_hook) != 1:
                    raise ValueError("unreviewed M11 active owner cold installer")
                transformed = transformed.replace(
                    cold_hook,
                    '        if (key in ("causal_model", "perception",'
                    ' "metacognition_health") and type(runtime) is I1Runtime):\n'
                    '            owner.install_m11_cold_state(\n'
                    '                deepcopy(value), capability=_M11_COLD_OWNER_TOKEN)\n'
                    '        elif key == "i1_lived_water_model":',
                )
                transformed = i1_m11_active_publication_custody_source(transformed)
                transformed = i1_m11_bounded_journal_source(transformed)
            # No stale absolute Python imports may silently reach I0.
            for line in transformed.splitlines():
                stripped = line.lstrip()
                if (re.match(r"^(from|import)\s+i0(?:\.|\s|$)", stripped)
                        or re.match(r"^(from|import)\s+lab(?:\.|\s|$)", stripped)):
                    raise ValueError("unisolated Python import in " + str(file))
            target = dest / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(transformed, encoding="utf-8")
            manifest["files"][str(target.relative_to(output))] = {
                "source_path": str(file.relative_to(SOURCE_ROOT)),
                "source_sha256": sha256(contents.encode()).hexdigest(),
                "built_sha256": sha256(transformed.encode()).hexdigest(),
            }
    # I1-only model/runtime overlays are namespaced source, not part of I0.
    overlays = SOURCE_ROOT / "i1" / "runtime"
    if overlays.exists():
        for file in sorted(overlays.glob("*.py")):
            if file.name == "__init__.py":
                continue  # Preserve the authentic isolated Lab package root.
            transformed = rewrite(file.read_text(encoding="utf-8"))
            target = output / "i1lab" / file.name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(transformed, encoding="utf-8")
            manifest["files"][str(target.relative_to(output))] = {
                "source_path": str(file.relative_to(SOURCE_ROOT)),
                "source_sha256": sha256(file.read_bytes()).hexdigest(),
                "built_sha256": sha256(transformed.encode()).hexdigest(),
            }
    # The build manifest contains source identity, but no hidden knowledge,
    # no actual birth and no scientific validation assertion.
    (output / "i1_build_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = generate(args.output)
    print(json.dumps({
        "schema": result["schema"],
        "source_main_sha": result["i0_baseline_sha"],
        "generated_python_modules": len(result["files"]),
        "output": str(args.output.resolve()),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
