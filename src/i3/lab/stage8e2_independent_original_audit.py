"""Stage8-E2 independent, read-only ORIGINAL gzip generation auditor.

Does NOT import the Stage8-E2 native runner or its archive writer. Source and
expected native case identities must be frozen independently. This verifies
original compressed and decoded SHA-256 and every physically paid original
before producing the six-life parent fitness input. Zero new lives.
"""
from __future__ import annotations

from hashlib import sha256
import gzip
import io
import json
from pathlib import Path
import re

from i3.lab import stage6_light_native_custody_preflight as C

SCHEMA = "i3-stage8e2-independent-original-gzip-readonly/v0"
MANIFEST_SCHEMA = "i3-two-phase-panel/v1"
NAME = re.compile(r"life-[0-9]+\.json\.gz\Z")
MAX_MANIFEST = 64_000_000
MAX_PACKED = 2_000_000
MAX_DECODED = 2_000_000


def _read_limited_gzip(packed: bytes) -> bytes:
    if len(packed) > MAX_PACKED:
        raise ValueError("oversized compressed native original")
    with gzip.GzipFile(fileobj=io.BytesIO(packed)) as z:
        raw = z.read(MAX_DECODED + 1)
        if len(raw) > MAX_DECODED or z.read(1):
            raise ValueError("oversized decompressed native original")
    return raw



TRACE_BASE = frozenset(("t", "action", "param", "option", "body", "pos", "dead"))
TRACE_EXTRAS = frozenset(("cognitive_work", "cognitive_accounting",
                          "funding_phases", "info"))


def _digest_canonical(value: object) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                             allow_nan=False, ensure_ascii=False).encode("utf-8")).hexdigest()


def verify_first_person_chains(life: dict) -> None:
    """Independently recompute the native bodily trace and paid-work chains.

    No engine replay: the original first-person records supply the applied
    actions, body, position and work. The unchained diagnostic info field
    remains original-gzip protected, but is not covered by native trace_head.
    """
    trace = life.get("trace")
    if (type(trace) is not list or
            type(life.get("genome")) is not str or
            type(life.get("world")) is not str or
            type(life.get("life_seed")) is not int or
            type(life.get("horizon")) is not int or
            type(life.get("manifest_id")) is not str):
        raise ValueError("missing first-person cryptographic trace seed")
    seed = [life["genome"], life["world"], life["life_seed"], life["horizon"]]
    trace_head = sha256(json.dumps(
        seed, separators=(",", ":")).encode("utf-8")).hexdigest()
    evidence_head = life["manifest_id"]
    for i, step in enumerate(trace, start=1):
        if (type(step) is not dict or set(step) != TRACE_BASE | TRACE_EXTRAS
                or type(step.get("t")) is not int or step["t"] != i
                or type(step.get("cognitive_work")) is not dict
                or type(step.get("cognitive_accounting")) is not dict
                or type(step.get("funding_phases")) is not dict):
            raise ValueError("foreign or out-of-order native paid-work step")
        core = {field: step[field] for field in TRACE_BASE}
        trace_head = sha256((
            trace_head + json.dumps(
                core, separators=(",", ":"), sort_keys=True,
            )
        ).encode("utf-8")).hexdigest()
        evidence_head = _digest_canonical({
            "previous": evidence_head, "record": core,
            "work": step["cognitive_work"],
            "accounting": step["cognitive_accounting"],
            "funding_phases": step["funding_phases"],
        })
    # The native engine extends evidence_head with a FINAL terminal/funding
    # digest after the last physically applied step.
    evidence_head = _digest_canonical({
        "previous": evidence_head,
        "terminal": life.get("terminal"),
        "accounting": life.get("cognitive_accounting"),
    })
    if (len(trace) != life.get("steps_lived")
            or trace_head != life.get("trace_head")
            or evidence_head != life.get("evidence_head")):
        raise ValueError("body trace or paid cognitive evidence chain was modified")


def audit_original_generation(archive_dir: str | Path, expected_cases: list[dict],
                              *, source_pin: str, source_head: str,
                              protocol: str, generation: int) -> dict:
    """Fail closed unless every original and original-level checksum matches."""
    root = Path(archive_dir)
    if root.is_symlink() or not root.is_dir():
        raise ValueError("missing native archive")
    manifest_path = root / "MANIFEST.json"
    seal_path = root / "MANIFEST.sha256"
    if (manifest_path.is_symlink() or seal_path.is_symlink()
            or not manifest_path.is_file() or not seal_path.is_file()):
        raise ValueError("missing/redirected native generation seal")
    if manifest_path.stat().st_size > MAX_MANIFEST:
        raise ValueError("oversized native manifest")
    manifest_bytes = manifest_path.read_bytes()
    manifest_sha = sha256(manifest_bytes).hexdigest()
    if seal_path.read_text(encoding="ascii").strip() != manifest_sha:
        raise ValueError("original manifest SHA mismatch")
    manifest = json.loads(manifest_bytes)
    if (type(expected_cases) is not list or
            type(manifest) is not dict or manifest.get("schema") != MANIFEST_SCHEMA
            or manifest.get("status") != "GENERATED"
            or manifest.get("failure") is not None
            or type(manifest.get("files")) is not list
            or type(manifest.get("planned")) is not int
            or manifest["planned"] != len(expected_cases)
            or type(manifest.get("generated")) is not int
            or manifest["generated"] != len(expected_cases)
            or len(manifest["files"]) != len(expected_cases)):
        raise ValueError("incomplete native archive before original audit")
    def key(identity):
        return tuple(identity[k] for k in (
            "population", "generation", "arm", "slot", "family", "repeat"))
    expected = {}
    for identity in expected_cases:
        if type(identity) is not dict or identity.get("generation") != generation:
            raise ValueError("unbound expected source identity")
        k = key(identity)
        if k in expected:
            raise ValueError("duplicated planned identity")
        expected[k] = identity
    observed, scores = set(), []
    for i, row in enumerate(manifest["files"]):
        name = f"life-{i:03d}.json.gz"
        if (type(row) is not dict or
                set(row) != {"file", "sha256", "uncompressed_sha256", "identity"}
                or row["file"] != name or not NAME.fullmatch(name)
                or not C._hash(row["sha256"])
                or not C._hash(row["uncompressed_sha256"])):
            raise ValueError("foreign original manifest row")
        path = root / name
        if path.is_symlink() or not path.is_file():
            raise ValueError("missing or redirected original gzip")
        packed = path.read_bytes()
        if sha256(packed).hexdigest() != row["sha256"]:
            raise ValueError("original compressed hash mismatch")
        raw = _read_limited_gzip(packed)
        if sha256(raw).hexdigest() != row["uncompressed_sha256"]:
            raise ValueError("original decoded hash mismatch")
        body = json.loads(raw)
        if (type(body) is not dict or set(body) != {"identity", "life"}
                or body["identity"] != row["identity"]):
            raise ValueError("original packet identity mismatch")
        identity, life = body["identity"], body["life"]
        k = key(identity)
        if k not in expected or k in observed or identity != expected[k]:
            raise ValueError("missing/duplicate/foreign original native identity")
        C._check_native_life(identity, life, source_pin, source_head, protocol)
        if (type(life.get("trace")) is not list
                or len(life["trace"]) != life["steps_lived"]):
            raise ValueError("native first-person trace lost")
        verify_first_person_chains(life)
        observed.add(k)
        scores.append({
            "population": identity["population"],
            "generation": generation, "arm": identity["arm"],
            "slot": identity["slot"], "family": identity["family"],
            "repeat": identity["repeat"],
            "steps_lived": life["steps_lived"], "terminal": life["terminal"],
        })
    if observed != set(expected):
        raise ValueError("incomplete original-level native coverage")
    # One score per archived native original. No per-gene or causal inference.
    return {
        "schema": SCHEMA, "status": "ALL_ORIGINALS_REHASHED_NO_SCIENCE",
        "generation": generation, "original_lives_verified": len(observed),
        "original_manifest_sha256": manifest_sha,
        "six_life_rows": scores,
        "scientific_claim_authorized": False, "native_lives_created": 0,
    }
