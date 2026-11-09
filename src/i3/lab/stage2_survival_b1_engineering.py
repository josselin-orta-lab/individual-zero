"""B1 exact-path ENGINEERING G/R smoke on new prospective-type F0 worlds.

96 fixed, public-preview independent *candidate* pairs x FIXED/GATE; real
funded Mind+World actions, temporary sealed originals and reduction.
Biological outcomes are NEVER returned, uploaded, interpreted or admitted
to science. This transport MUST NOT open B1 scientific/validation/reserve
or reuse the consumed Stage-2.1 DEVELOPMENT 80/81 route.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import sys

from . import stage2_survival_b1_sampling as SAMPLE
from . import stage2_survival_b1_worldspec_audit as SPECS
from . import two_phase_panel as TP
from ..modules.genome import generation_zero
from . import stage2_admission as GUARD
from ..runtime.life import run_life

SCHEMA = "i3-b1-newworld-paired-engineering-gr/v1"
PROTOCOL = "B1_FIXED_FIRST_96_PUBLIC_PREVIEW_ENGINEERING_ONLY"
COHORT = "engineering"
PAIRS = 96
LIVES = 2 * PAIRS
HORIZON = SAMPLE.HORIZON
POLICIES = SAMPLE.POLICIES
I3 = Path(__file__).resolve().parents[1]


def source_fingerprint() -> str:
    """Bind this engineering transport to all executable I3 source bytes."""
    paths = (sorted((I3 / "modules").glob("*.py"))
             + sorted((I3 / "runtime").glob("*.py"))
             + sorted((I3 / "lab").glob("*.py")))
    if not paths or not (I3 / "lab" / "stage2_survival_b1_sampling.py") in paths:
        raise ValueError("missing required source footprint")
    manifest = [(path.relative_to(I3).as_posix(),
                 sha256(path.read_bytes()).hexdigest()) for path in paths]
    return sha256(json.dumps(manifest, sort_keys=True,
                             separators=(",", ":")).encode()).hexdigest()


def cases() -> list[dict]:
    """Immutable policy schedule: first 96 units of fixed PUBLIC preview."""
    proposal = SAMPLE.preview(SAMPLE.PREVIEW_WITNESS)
    SAMPLE.verify_preview(proposal, SAMPLE.PREVIEW_WITNESS)
    selected = proposal["proposed_units"][:PAIRS]
    if len(selected) != PAIRS:
        raise ValueError("incomplete engineering pair allocation")
    output = [
        {
            "pair_id": unit["pair_id"], "index": unit["ordinal"],
            "cohort": COHORT, "family": unit["family"],
            "world_seed": unit["world_seed"],
            "genome_seed": unit["genome_seed"],
            "life_seed": unit["life_seed"], "policy": arm,
        }
        for unit in selected for arm in POLICIES
    ]
    if len(output) != LIVES:
        raise ValueError("invalid engineering schedule")
    return output


def _match_case(case: dict, expected: dict) -> None:
    if type(case) is not dict or case != expected:
        raise PermissionError("not an exactly allocated B1 engineering case")
    if case["cohort"] != "engineering":
        raise PermissionError("B1 World experiments are engineering only")
    if case["family"] not in SAMPLE.FAMILIES:
        raise PermissionError("unknown B1 ecology")
    if (type(case["world_seed"]) is not int or
            not SAMPLE.WORLD_BASE <= case["world_seed"] <
            SAMPLE.WORLD_BASE + (1 << SAMPLE.SEED_BITS)):
        raise PermissionError("world seed not in B1 synthetic engineering scope")
    if case["policy"] not in POLICIES:
        raise PermissionError("unknown B1 policy")


def _run_case(expected_cases: list, fingerprint: str):
    def run(case: dict) -> dict:
        # Exact allocation verification happens before constructing a World,
        # a genome, an individual or minting a ticket.
        ordinal = case.get("index") if isinstance(case, dict) else None
        if type(ordinal) is not int or not 0 <= ordinal < PAIRS:
            raise PermissionError("engineering case index not in the fixed 96")
        pos = 2 * ordinal + POLICIES.index(case.get("policy")) if (
            case.get("policy") in POLICIES) else -1
        if pos < 0:
            raise PermissionError("policy outside B1 public preview")
        _match_case(case, expected_cases[pos])
        spec = SPECS._construct_f0_spec(case["family"], case["world_seed"])
        ticket = GUARD.admit_b1_newworld_engineering(
            family=case["family"], index=ordinal,
            world_seed=case["world_seed"], spec=spec,
            transport_fingerprint=fingerprint)
        experimental = case["policy"] == "p13_replay_gate_v1"
        life = run_life(
            generation_zero(case["genome_seed"]), spec, case["life_seed"],
            HORIZON, protocol=PROTOCOL, decision_policy=case["policy"],
            admission=ticket if experimental else None)
        life["admission_receipt"] = ticket.receipt()
        return life
    return run


def _reduce_for_structural_check(identity: dict, life: dict) -> dict:
    """Transient only: never return a biological outcome to the caller."""
    manifest = life["manifest"]
    return {
        "pair_id": identity["pair_id"],
        "policy": identity["policy"],
        "source_sha256": manifest["source"]["sha256"],
        "world_sha256": manifest["world_sha256"],
        "genome_sha256": sha256(json.dumps(
            manifest["genome"], sort_keys=True,
            separators=(",", ":")).encode()).hexdigest(),
        "life_seed": manifest["life_seed"],
    }


def _invariants(fingerprint):
    def check(identity: dict, life: dict) -> dict[str, bool]:
        receipt = life["admission_receipt"]
        ca = life["cognitive_accounting"]
        manifest = life["manifest"]
        is_gate = identity["policy"] == "p13_replay_gate_v1"
        policy = manifest.get("experimental_policy", {}).get("name", "reference")
        return {
            "exact_paid_energy": ca["totals"]["energy"]["unpaid"] <= 1e-12,
            "exact_paid_vigilance": ca["totals"]["vigilance"]["unpaid"] <= 1e-12,
            "no_cognitive_shortfall": ca["shortfall_steps"] == 0,
            "cognitive_account_settled": ca["status"] == "SETTLED_FOR_DECLARED_WORK",
            "within_horizon": type(life["steps_lived"]) is int
                              and 1 <= life["steps_lived"] <= HORIZON,
            "observed_arm_matches": policy == identity["policy"],
            "gate_summary_only_for_gate": ("replay_gate" in life) == is_gate,
            "receipt_cohort_engineering": receipt["cohort"] == COHORT,
            "receipt_matches_family_index": receipt["family"] == identity["family"]
                                            and receipt["index"] == identity["index"],
            "receipt_matches_world": receipt["world_seed"] == identity["world_seed"]
                                     and receipt["world_sha256"] == manifest["world_sha256"]
                                     and receipt["world_name"] == life["world"],
            "receipt_matches_source": receipt["transport_fingerprint"] == fingerprint,
            "original_matched_seed": manifest["life_seed"] == identity["life_seed"],
            "valid_terminal_label": life["terminal"] in ("dead", "censored"),
            "no_extra_science_arm": identity["policy"] in POLICIES,
        }
    return check


def rehearse() -> dict:
    """Execute fixed 192 ENGINEERING lives via existing sealed G/R, not science."""
    scheduled = cases()
    fingerprint = source_fingerprint()
    report = TP.sealed_rehearsal(scheduled, _run_case(scheduled, fingerprint),
                                 _reduce_for_structural_check,
                                 _invariants(fingerprint))
    report.update({
        "runner": SCHEMA, "source_fingerprint": fingerprint,
        "protocol_id": PROTOCOL, "cohort": COHORT,
        "pair_count": PAIRS, "unique_worlds_expected": PAIRS,
        "public_root_synthetic": True,
        "world_source_external_attestation": False,
        "observed_survival_results_published": False,
        "independent_pairs_proven": False,
        "scientific_lives": 0,
        "scientific_admission": "BLOCKED",
        "scientific_verdict": "NOT_ISSUED",
    })
    return report


def execute(*_args, **_kwargs):
    """No scientific entrypoint is created by this engineering prototype."""
    raise PermissionError("B1 prospective science remains unadmitted")


def main(argv):
    if len(argv) != 2 or argv[1] != "rehearse":
        raise SystemExit("usage: python -m i3.lab.stage2_survival_b1_engineering rehearse")
    result = rehearse()
    # Structural-only original proof; no biology (survival, death, action,
    # genome, location, cognition scores) is emitted or persisted.
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main(sys.argv)
