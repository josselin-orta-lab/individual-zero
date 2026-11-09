"""Deterministic durable bundle custody for the Stage-1 omega campaign.

Pure filesystem/ZIP tooling. No I3 runtime, World, genome or scientific
arithmetic is imported here. The bundle is suitable for a durable GitHub
prerelease asset while Actions artifacts remain redundant working copies.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import zipfile

SCHEMA = "i3-stage1-omega-evidence-bundle/v1"
MANIFEST = "BUNDLE_MANIFEST.json"
FIXED_DATE = (1980, 1, 1, 0, 0, 0)
FILE_MODE = 0o100644 << 16


def _canonical(value) -> bytes:
    return (json.dumps(
        value, sort_keys=True, separators=(",", ":"),
        ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def _digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def _entry(name: str, data: bytes) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, FIXED_DATE)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = FILE_MODE
    info.create_system = 3
    return info


def _source_files(root: Path, output: Path) -> list[tuple[str, bytes]]:
    root = root.resolve()
    output = output.resolve()
    if not root.is_dir():
        raise ValueError("evidence root must be a directory")
    try:
        output.relative_to(root)
    except ValueError:
        pass
    else:
        raise ValueError("bundle output must be outside evidence root")

    rows = []
    for path in sorted(root.rglob("*"), key=lambda p: p.as_posix()):
        if path.is_symlink():
            raise ValueError("symlinks are forbidden in evidence custody")
        if path.is_dir():
            continue
        if not path.is_file():
            raise ValueError("unsupported evidence filesystem entry")
        relative = path.relative_to(root).as_posix()
        if (not relative or relative == MANIFEST or relative.startswith("/")
                or ".." in Path(relative).parts):
            raise ValueError("unsafe or reserved evidence path")
        rows.append((relative, path.read_bytes()))
    if not rows:
        raise ValueError("evidence bundle cannot be empty")
    return rows


def bundle_directory(root, output, *, label: str) -> dict:
    """Create a byte-deterministic ZIP and return its custody receipt."""
    if type(label) is not str or not label.strip():
        raise ValueError("nonempty evidence label required")
    root = Path(root)
    output = Path(output)
    rows = _source_files(root, output)

    inventory = [{
        "path": name,
        "bytes": len(data),
        "sha256": _digest(data),
    } for name, data in rows]
    tree_sha = _digest(_canonical(inventory))
    manifest = {
        "schema": SCHEMA,
        "label": label,
        "file_count": len(inventory),
        "total_uncompressed_bytes":
            sum(row["bytes"] for row in inventory),
        "tree_sha256": tree_sha,
        "files": inventory,
    }
    manifest_bytes = _canonical(manifest)

    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(
            output, "w", compression=zipfile.ZIP_DEFLATED,
            compresslevel=9, strict_timestamps=True) as archive:
        archive.writestr(_entry(MANIFEST, manifest_bytes), manifest_bytes)
        for name, data in rows:
            archive.writestr(_entry(name, data), data)

    bundle_bytes = output.read_bytes()
    return {
        "schema": "i3-stage1-omega-evidence-bundle-receipt/v1",
        "label": label,
        "bundle_file": output.name,
        "bundle_bytes": len(bundle_bytes),
        "bundle_sha256": _digest(bundle_bytes),
        "tree_sha256": tree_sha,
        "file_count": len(inventory),
        "total_uncompressed_bytes":
            manifest["total_uncompressed_bytes"],
    }


def verify_bundle(path) -> dict:
    """Verify an existing bundle without trusting ZIP metadata or filenames."""
    path = Path(path)
    raw = path.read_bytes()
    try:
        with zipfile.ZipFile(path, "r") as archive:
            infos = archive.infolist()
            names = [info.filename for info in infos]
            if len(names) != len(set(names)):
                raise ValueError("duplicate ZIP member")
            if names.count(MANIFEST) != 1:
                raise ValueError("exactly one bundle manifest required")
            if any(
                    name.startswith("/") or ".." in Path(name).parts
                    for name in names):
                raise ValueError("unsafe ZIP member")
            try:
                manifest = json.loads(
                    archive.read(MANIFEST).decode("utf-8"))
            except (KeyError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise ValueError("invalid bundle manifest") from exc

            if (type(manifest) is not dict
                    or manifest.get("schema") != SCHEMA
                    or type(manifest.get("label")) is not str
                    or not manifest["label"].strip()
                    or type(manifest.get("files")) is not list):
                raise ValueError("invalid bundle manifest contract")
            inventory = manifest["files"]
            expected_names = [row.get("path") for row in inventory]
            if (len(expected_names) != len(set(expected_names))
                    or set(names) != {MANIFEST, *expected_names}):
                raise ValueError("bundle members and manifest disagree")

            rebuilt = []
            for row in inventory:
                if (type(row) is not dict
                        or set(row) != {"path", "bytes", "sha256"}
                        or type(row["path"]) is not str
                        or type(row["bytes"]) is not int
                        or row["bytes"] < 0
                        or type(row["sha256"]) is not str
                        or len(row["sha256"]) != 64):
                    raise ValueError("invalid inventory row")
                data = archive.read(row["path"])
                if len(data) != row["bytes"] or _digest(data) != row["sha256"]:
                    raise ValueError("bundle member digest mismatch")
                rebuilt.append({
                    "path": row["path"],
                    "bytes": row["bytes"],
                    "sha256": row["sha256"],
                })

            tree_sha = _digest(_canonical(rebuilt))
            if (manifest.get("file_count") != len(rebuilt)
                    or manifest.get("total_uncompressed_bytes")
                    != sum(row["bytes"] for row in rebuilt)
                    or manifest.get("tree_sha256") != tree_sha):
                raise ValueError("bundle aggregate manifest mismatch")
    except zipfile.BadZipFile as exc:
        raise ValueError("invalid ZIP evidence bundle") from exc

    return {
        "schema": "i3-stage1-omega-evidence-bundle-verification/v1",
        "status": "VERIFIED",
        "label": manifest["label"],
        "bundle_file": path.name,
        "bundle_bytes": len(raw),
        "bundle_sha256": _digest(raw),
        "tree_sha256": tree_sha,
        "file_count": len(rebuilt),
        "total_uncompressed_bytes":
            sum(row["bytes"] for row in rebuilt),
    }


__all__ = [
    "FIXED_DATE", "MANIFEST", "SCHEMA",
    "bundle_directory", "verify_bundle",
]
