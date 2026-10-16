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



def i1_physiology_source(source: str) -> str:
    """Versioned I1-only physical deprivation, never applied to I0 or Lab.

    The generated copy owns the consequences; cognitive code sees only the
    same body telemetry on the next authorized capture. Rates are frozen
    constructor inputs, carried by the normal WorldPhysicsConfig / M11 digest.
    """
    patches = (
        (
            "    shelter_stones_required: int = 4\n",
            "    shelter_stones_required: int = 4\n"
            "    starvation_integrity_damage_per_step: float = 0.5\n"
            "    dehydration_integrity_damage_per_step: float = 1.0\n"
        ),
        (
            "        self.tool_recipe.validate()\n",
            "        for damage in (self.starvation_integrity_damage_per_step,\n"
            "                       self.dehydration_integrity_damage_per_step):\n"
            "            if not 0.0 <= damage <= 100.0 or damage != damage:\n"
            "                raise ValueError('I1 deprivation rates must be finite in [0,100]')\n"
            "        self.tool_recipe.validate()\n"
        ),
        (
            '            "shelter_stones_required": self.shelter_stones_required,\n',
            '            "shelter_stones_required": self.shelter_stones_required,\n'
            '            "starvation_integrity_damage_per_step": self.starvation_integrity_damage_per_step,\n'
            '            "dehydration_integrity_damage_per_step": self.dehydration_integrity_damage_per_step,\n'
        ),
        (
            "        lethal_reasons: list[str] = []\n",
            "        # #231: apply *after* the actual action. Successful eating or\n"
            "        # drinking prevents same-step deprivation. Rest, a failed\n"
            "        # action, and physical hazards do not suspend metabolism.\n"
            "        starvation = (self._config.starvation_integrity_damage_per_step\n"
            "                      if body.food <= 0.0 else 0.0)\n"
            "        dehydration = (self._config.dehydration_integrity_damage_per_step\n"
            "                       if body.water <= 0.0 else 0.0)\n"
            "        if starvation or dehydration:\n"
            "            integrity_before = body.integrity\n"
            "            body = BodyState(\n"
            "                energy=body.energy, food=body.food, water=body.water,\n"
            "                integrity=self._clamp(integrity_before - starvation - dehydration),\n"
            "            )\n"
            "            effects['deprivation_integrity_damage'] = {\n"
            "                'starvation': starvation, 'dehydration': dehydration,\n"
            "                'actual_integrity_loss': integrity_before - body.integrity,\n"
            "            }\n"
            "        lethal_reasons: list[str] = []\n"
        ),
    )
    for original, replacement in patches:
        if source.count(original) != 1:
            raise ValueError("I1 deprivation source anchor changed")
        source = source.replace(original, replacement)
    return source

def i1_default_sleep_source(source: str) -> str:
    """Bind the existing Stage10 physical/sleep policy at every mortal I1 birth.

    Stage11SleepRuntime is the common parent of the living Stage12 I1
    descendants. This generator edits only the separately built i1lab copy,
    never the reference Lab implementation. All descendant constructors
    receive the same immutable versioned physical/sleep configuration.
    """
    anchor = (
        "        stage11_config.validate()\n"
        "        stage10_config.validate()\n"
    )
    replacement = (
        "        from .i1_natural_sleep import enable_natural_sleep_birth\n"
        "        kwargs['world_config'], stage10_config = enable_natural_sleep_birth(\n"
        "            world_config=kwargs['world_config'],\n"
        "            stage10_config=stage10_config,\n"
        "        )\n"
        + anchor
    )
    if source.count(anchor) != 1:
        raise ValueError("unreviewed I1 Stage11Sleep birth entrypoint")
    return source.replace(anchor, replacement)


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
            contents = file.read_text(encoding="utf-8")
            transformed = rewrite(contents)
            if output_package == "i1lab" and relative.as_posix() == "world.py":
                transformed = i1_physiology_source(transformed)
            if (output_package == "i1lab"
                    and relative.as_posix() == "stage11_sleep_runtime.py"):
                transformed = i1_default_sleep_source(transformed)
            # I1-only M11 custody: accept an explicit Stage12 descendant,
            # but pin the frozen I1 model parameters in the cold-birth digest.
            # Never alter the canonical src/lab or src/i0 M11 implementation.
            if output_package == "i1lab" and relative.as_posix() == "m11_transactional_mortal.py":
                required = "type(runtime) is Stage12Runtime"
                if transformed.count(required) != 3:
                    raise ValueError("unreviewed I1 M11 runtime type gate")
                transformed = transformed.replace(
                    required, "isinstance(runtime, Stage12Runtime)"
                )
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
    overlays = SOURCE_ROOT / "i1_overlays"
    if overlays.exists():
        for file in sorted(overlays.glob("*.py")):
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
