"""I1-only first-person consolidation forms for the four real cognitive owners.

A published form is evidence available to its owner, NOT a new causal/safety
status, precision estimate, kappa calibration or motor permission. The P-42
sixth pass builds these forms only from its *already validated* private
autobiographical candidate. Stage10 publishes them atomically and rebases
on the current online owner state without replaying online learning.
"""
from __future__ import annotations

from copy import deepcopy
from string import hexdigits

from .determinism import canonical_causal_bytes, sha256_hex

SCHEMA = "i1-active-owner-lived-observations-v1"
FORM_KINDS = frozenset({"causal_model", "perception", "metacognition_health"})
REPLAY_KIND = {
    "perception": "world_transition_experienced",
    "metacognition_health": "agency_comparison",
}
MAX_VISIBLE_REPLAY_REFS = 64
_ALLOWED_UPDATES = {
    "causal_model": frozenset({
        "causal_inference_status_published",
        "causal_safety_status_published",
        "causal_prediction_corrections_published",
    }),
    "perception": frozenset({"perceptual_precision_update_published"}),
    "metacognition_health": frozenset({"kappa_update_published"}),
}


def _validate_ref_list(value):
    if (type(value) is not list or not value
            or any(type(v) is not str or not v for v in value)
            or len(value) != len(set(value))):
        raise ValueError("invalid first-person event or episode provenance")


def validate_owner_rows(owner_id, rows):
    """Only precisely bounded, provenance-labelled *unverified* evidence."""
    if owner_id not in FORM_KINDS or type(rows) is not list:
        raise ValueError("invalid active cognitive owner form")
    seen = set()
    for item in rows:
        if type(item) is not dict:
            raise ValueError("active cognitive form must be a mapping")
        if owner_id == "causal_model":
            if set(item) != {
                "id", "predicate", "status", "source_episode_refs",
                "source_event_refs", "expires_at_step", "validated_for_safety",
            }:
                raise ValueError("unreviewed causal hypothesis fields")
            predicate = item["predicate"]
            if (type(predicate) is not dict
                    or set(predicate) != {
                        "primitive", "parameters", "observed_field", "observed_value",
                    } or type(predicate["primitive"]) is not str
                    or type(predicate["parameters"]) is not dict
                    or type(predicate["observed_field"]) is not str
                    or type(predicate["observed_value"]) is not str
                    or item["status"] != "hypothese_causale"
                    or item["validated_for_safety"] is not False
                    or type(item["expires_at_step"]) is not int
                    or item["expires_at_step"] < 1):
                raise ValueError("private association is not causal or safety proof")
            _validate_ref_list(item["source_episode_refs"])
            _validate_ref_list(item["source_event_refs"])
            ref = "hyp:" + sha256_hex(canonical_causal_bytes(predicate))[:28]
            if item["id"] != ref:
                raise ValueError("causal hypothesis identifier mismatches observation")
        else:
            if set(item) != {
                "episode_ref", "event_ref", "event_kind",
                "projection_digest", "verification_status",
                "lived_observation",
            }:
                raise ValueError("unreviewed perceptual/metacognitive claim")
            if (type(item["episode_ref"]) is not str or not item["episode_ref"]
                    or type(item["event_ref"]) is not str or not item["event_ref"]
                    or item["event_kind"] != REPLAY_KIND[owner_id]
                    or item["verification_status"] != "observed_not_verified"
                    or type(item["projection_digest"]) is not str
                    or len(item["projection_digest"]) != 64
                    or any(char not in hexdigits for char in item["projection_digest"])):
                raise ValueError("unverified event is not an authorized lived record")
            observation = item["lived_observation"]
            if owner_id == "perception":
                if (type(observation) is not dict
                        or set(observation) != {"position", "body"}
                        or type(observation["position"]) is not list
                        or len(observation["position"]) != 2
                        or any(type(x) is not int for x in observation["position"])
                        or type(observation["body"]) is not dict
                        or set(observation["body"])
                            != {"energy", "food", "water", "integrity"}
                        or any(type(x) not in (int, float)
                               for x in observation["body"].values())):
                    raise ValueError("invalid first-person physical observation")
            elif (type(observation) is not dict
                    or set(observation) != {"status", "attribution"}
                    or observation["status"] not in {
                        "conforming", "nonconforming", "indeterminable",
                    }
                    or type(observation["attribution"]) is not str
                    or not observation["attribution"]):
                raise ValueError("invalid first-person agency judgement")
            ref = item["event_ref"]
        if ref in seen:
            raise ValueError("duplicate active owner evidence identifier")
        seen.add(ref)
        canonical_causal_bytes(item)
    ids = [item["id"] if owner_id == "causal_model" else item["event_ref"]
           for item in rows]
    if ids != sorted(ids):
        raise ValueError("active evidence must have deterministic identity order")
    if owner_id != "causal_model" and len(rows) > MAX_VISIBLE_REPLAY_REFS:
        raise ValueError("active lived-replay index exceeded explicit bound")


def build_consolidated_owner_form(candidate, owner_id):
    """Rebuild only ONE owner's admissible form from private lived evidence.

    The paid sixth pass assembles all four with this same function. During
    Stage10's owner rebase, each canonical owner checks its own source only;
    it must not repeatedly copy and validate the other three owners' rows.
    """
    if (type(candidate) is not dict
            or type(candidate.get("hypotheses")) is not list
            or type(candidate.get("private_replay_observations", [])) is not list
            or type(candidate.get("procedural")) is not list):
        raise ValueError("unvalidated private six-pass evidence")
    if owner_id == "value_needs":
        return sorted(
            (deepcopy(row) for row in candidate["procedural"]
             if type(row) is dict and row.get("state") == "compiled_private"),
            key=lambda row: row["id"],
        )
    if owner_id == "causal_model":
        rows = sorted(
            (deepcopy(row) for row in candidate["hypotheses"]),
            key=lambda row: row["id"],
        )
        validate_owner_rows(owner_id, rows)
        return rows
    if owner_id not in REPLAY_KIND:
        raise ValueError("unknown active cognitive publication owner")
    matching = []
    wanted = REPLAY_KIND[owner_id]
    for row in candidate.get("private_replay_observations", []):
        if type(row) is not dict:
            raise ValueError("unreviewed private replay row")
        if row.get("event_kind") != wanted:
            continue
        if type(row.get("lived_observation")) is not dict:
            raise ValueError("active observation must originate in lived replay")
        matching.append({
            "episode_ref": row["episode_ref"],
            "event_ref": row["event_ref"],
            "event_kind": wanted,
            "projection_digest": row["projection_digest"],
            "lived_observation": deepcopy(row["lived_observation"]),
            "verification_status": "observed_not_verified",
        })
    # A bounded owner-specific live view; the full private record remains h.
    matching.sort(key=lambda item: item["event_ref"])
    rows = matching[-MAX_VISIBLE_REPLAY_REFS:]
    rows.sort(key=lambda item: item["event_ref"])
    validate_owner_rows(owner_id, rows)
    return rows


def build_consolidated_owner_forms(candidate):
    """Assemble the same four owner-specific forms at the paid sixth pass."""
    return {
        owner: build_consolidated_owner_form(candidate, owner)
        for owner in (
            "value_needs", "causal_model", "perception", "metacognition_health",
        )
    }


class ActiveConsolidatedOwner:
    """One causal owner wrapper, *not* a second writer or motor authority.

    The actual CausalModel/Perception/Stage12 Metacognition owner remains
    the only writer for online learning. All Stage10 publication does is
    atomically augment that SAME owner's registered snapshot with verified
    advisory evidence. Its normal live restoration is strictly equality-only
    for the underlying owner; M11 has a separate private cold capability.
    """

    def __init__(self, original, owner_id):
        if owner_id not in FORM_KINDS or original.owner_id != owner_id:
            raise ValueError("active I1 wrapper must have exact canonical owner")
        self.owner_id = owner_id
        self._canonical_owner = original
        self._active_observations = []
        self._m11_cold_installed = False

    def __getattr__(self, name):
        return getattr(self._canonical_owner, name)

    def observed_consolidated(self):
        return deepcopy(self._active_observations)

    def export_causal_state(self):
        return {
            "schema": SCHEMA,
            "owner_id": self.owner_id,
            "canonical_owner": self._canonical_owner.export_causal_state(),
            "observed_consolidated": deepcopy(self._active_observations),
        }

    def _unpack(self, state):
        if (type(state) is not dict
                or set(state) != {
                    "schema", "owner_id", "canonical_owner", "observed_consolidated",
                } or state["schema"] != SCHEMA
                or state["owner_id"] != self.owner_id):
            raise ValueError("incompatible active I1 owner snapshot schema")
        rows = deepcopy(state["observed_consolidated"])
        validate_owner_rows(self.owner_id, rows)
        canonical_causal_bytes(state["canonical_owner"])
        return rows

    def restore_causal_state(self, state):
        """Stage10 may add advisory forms, but may never rewind online owners."""
        rows = self._unpack(state)
        if (canonical_causal_bytes(state["canonical_owner"])
                != canonical_causal_bytes(
                    self._canonical_owner.export_causal_state()
                )):
            raise ValueError("I1 active publication cannot rewind online learning")
        self._active_observations = rows

    def install_m11_cold_state(self, state, *, capability):
        """One-time genuine cold import from authenticated SQLite generation."""
        from .m11_transactional_mortal import _M11_COLD_OWNER_TOKEN
        if capability is not _M11_COLD_OWNER_TOKEN or self._m11_cold_installed:
            raise ValueError("untrusted or repeated M11 cold import")
        rows = self._unpack(state)
        if self.owner_id == "metacognition_health":
            self._canonical_owner.install_m11_cold_state(
                deepcopy(state["canonical_owner"]), capability=capability,
            )
        else:
            self._canonical_owner.restore_causal_state(
                deepcopy(state["canonical_owner"])
            )
        if (canonical_causal_bytes(self._canonical_owner.export_causal_state())
                != canonical_causal_bytes(state["canonical_owner"])):
            raise ValueError("M11 installed owner differs from verified state")
        self._active_observations = rows
        self._m11_cold_installed = True

    def prepare_stage10_owner_rebase(self, candidate, baseline, updates):
        """Rebase solely the attached notes onto live online-owner baseline."""
        if (type(candidate) is not dict
                or type(candidate.get("forms")) is not dict
                or type(baseline) is not dict
                or baseline.get("schema") != SCHEMA
                or baseline.get("owner_id") != self.owner_id):
            raise ValueError("I1 published owner candidate not versioned")
        expected = build_consolidated_owner_form(candidate, self.owner_id)
        proposed = candidate["forms"].get(self.owner_id)
        if canonical_causal_bytes(expected) != canonical_causal_bytes(proposed):
            raise ValueError("I1 active owner would publish unverified source")
        validate_owner_rows(self.owner_id, proposed)
        if any(update.owner_id != self.owner_id
               or update.kind not in _ALLOWED_UPDATES[self.owner_id]
               for update in updates):
            raise ValueError("unreconciled online owner update after sleep cut")
        prepared = deepcopy(baseline)
        prepared["observed_consolidated"] = deepcopy(proposed)
        # The full inner online-owner state including kappa/precision/causal
        # revisions and sleep/health MUST remain byte-for-byte current.
        if (canonical_causal_bytes(prepared["canonical_owner"])
                != canonical_causal_bytes(baseline["canonical_owner"])):
            raise ValueError("online learning changed in advisory rebase")
        return prepared
