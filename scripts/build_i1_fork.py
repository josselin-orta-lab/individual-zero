"""Build a separately importable I1 descendant without editing I0 or lab.

The checked-in src/i1 tree is the exact source snapshot from the approved
I0 main SHA. This build mechanically namespaces that copy and the complete
laboratory runtime in a separate output directory. No src/i0 or src/lab file
is written. The *physics implementation* is kept byte-equivalent after
namespace substitutions, and its parity is checked independently.

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
