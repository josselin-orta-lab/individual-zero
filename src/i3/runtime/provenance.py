"""Observer-only input/source manifests. No world facts are sent to the mind.

File hashes describe on-disk source, not authentication or an attestation of
arbitrary monkey-patched code. Git HEAD is context, not proof of clean bytes.
"""
from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path
import platform
import subprocess

from i3.modules.genome import canonical as canonical_genome
from i3.modules.world import WorldSpec


def canonical(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False)


def digest(value) -> str:
    return sha256(canonical(value).encode("utf-8")).hexdigest()


def world_snapshot(spec: WorldSpec) -> dict:
    """Full initial world, including hidden laws/effects/scheduled changes."""
    data = {"name": spec.name, "width": spec.width, "height": spec.height,
            "spawn": spec.spawn, "body": spec.body, "laws": asdict(spec.laws),
            "water": [[list(pos), asdict(src)] for pos, src in sorted(spec.water.items())],
            "food": [[list(pos), asdict(src)] for pos, src in sorted(spec.food.items())],
            "token_effects": sorted(spec.token_effects.items()),
            "changes": spec.changes}
    # Detach nested mutable inputs; preserve scheduled-event order.
    return json.loads(canonical(data))


def source_snapshot() -> dict:
    engine = Path(__file__).resolve().parents[1]
    files = {p.relative_to(engine).as_posix(): sha256(p.read_bytes()).hexdigest()
             for p in sorted(engine.rglob("*.py"))}
    head = None
    dirty = None
    try:
        result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=engine,
                                text=True, capture_output=True, timeout=2)
        if result.returncode == 0:
            head = result.stdout.strip()
            status = subprocess.run(
                ["git", "status", "--porcelain", "--untracked-files=all", "--", "."],
                cwd=engine, text=True, capture_output=True, timeout=2)
            if status.returncode == 0:
                dirty = bool(status.stdout.strip())
    except (OSError, subprocess.TimeoutExpired):
        pass  # Source bytes still identify an exported, non-Git checkout.
    return {"files": files, "sha256": digest(files), "git_head": head,
            "working_tree_dirty": dirty}


def build_manifest(genome, spec, life_seed, horizon, protocol):
    if type(life_seed) is not int:
        raise ValueError("life_seed must be an integer")
    if type(protocol) is not str or not protocol.strip():
        raise ValueError("nonempty protocol identifier required")
    world = world_snapshot(spec)
    return {"schema": "i3-life-manifest/v2", "execution_model": "i3-funded-v2", "protocol": protocol,
            "source": source_snapshot(),
            "python": {"implementation": platform.python_implementation(),
                       "version": platform.python_version()},
            "world": world, "world_sha256": digest(world),
            "genome": json.loads(canonical_genome(genome)),
            "life_seed": life_seed, "horizon": horizon}
