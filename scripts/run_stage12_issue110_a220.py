"""A2.20 preregistered independent laboratory, never an I0 runtime module."""
from dataclasses import asdict, replace
from copy import deepcopy
from pathlib import Path
import argparse
import json
import random
import subprocess

from i0.interfaces import PrimitiveCommand
from i0.modules.perception import SymbolicPerception
from i0.modules.stage12_goal_agency import GoalAgencyService
from lab.determinism import canonical_causal_bytes, sha256_hex
from lab.stage11_reference_fixture import build_stage11_reference_runtime
from lab.world import WorldBody, WorldLayout, Position

SEEDS = range(111, 119)
PATTERNS = ("stay_stay", "passive_stay", "stay_passive", "passive_passive")


def digest(value):
    return sha256_hex(canonical_causal_bytes(value))


class EvidenceLedger:
    """External append-only evidence with hash custody and strict provenance."""

    def __init__(self, original):
        original.validate()
        if original.subjective_agency != "self" or not original.cue_ref:
            raise ValueError("original self judgement and cue required")
        self.original = original.as_dict()
        self.events = []
        self.last_hash = digest({"schema": "a220-ledger-v1", "original": self.original})
        self.last_step = original.observed_world_step
        self.seen = {original.cue_ref}
        self.revised = False

    def append(self, *, before, after, command, cue_ref):
        if (command.primitive != "attendre" or command.parameters
                or after.t_monde != before.t_monde + 1
                or before.t_monde != self.last_step
                or not isinstance(cue_ref, str) or not cue_ref.strip()
                or cue_ref in self.seen):
            raise ValueError("invalid or duplicate first-person source")
        passive = (before.x, before.y) != (after.x, after.y)
        event_type = ("revision_to_unknown" if passive and not self.revised
                      else "additional_passive_evidence" if passive
                      else "no_new_agency_evidence")
        event = {
            "sequence": len(self.events) + 1,
            "prior_hash": self.last_hash, "event": event_type,
            "initial_assessment_ref": self.original["assessment_ref"],
            "source_cue_ref": cue_ref,
            "before_step": before.t_monde, "observed_step": after.t_monde,
            "before_percept_sha": digest(asdict(before)),
            "after_percept_sha": digest(asdict(after)),
            "command_hash": digest(command.as_dict()),
            "epistemic_label": "unknown" if self.revised or passive else "self",
        }
        h = digest(event)
        self.events.append({**event, "hash": h})
        self.last_hash, self.last_step = h, after.t_monde
        self.seen.add(cue_ref)
        self.revised |= passive
        return event_type

    def export(self):
        return {"schema": "a220-ledger-v1", "original": deepcopy(self.original),
                "events": deepcopy(self.events), "head_hash": self.last_hash,
                "label": "unknown" if self.revised else "self"}

    @staticmethod
    def audit(image):
        if type(image) is not dict or set(image) != {"schema", "original", "events", "head_hash", "label"}:
            raise ValueError("invalid immutable ledger")
        if image["schema"] != "a220-ledger-v1":
            raise ValueError("invalid schema")
        from i0.modules.stage12_goal_agency import GoalAgencyJudgement
        original = GoalAgencyJudgement.from_dict(image["original"])
        if original.subjective_agency != "self" or not original.cue_ref:
            raise ValueError("invalid original")
        prior = digest({"schema": "a220-ledger-v1", "original": image["original"]})
        seen = {original.cue_ref}
        last_step = original.observed_world_step
        revised = False
        allowed = {"revision_to_unknown", "additional_passive_evidence", "no_new_agency_evidence"}
        if type(image["events"]) is not list:
            raise ValueError("events not list")
        for number, row in enumerate(image["events"], 1):
            if type(row) is not dict or set(row) != {
                    "sequence", "prior_hash", "event", "initial_assessment_ref",
                    "source_cue_ref", "before_step", "observed_step",
                    "before_percept_sha", "after_percept_sha", "command_hash",
                    "epistemic_label", "hash"}:
                raise ValueError("invalid row")
            value = {k: v for k, v in row.items() if k != "hash"}
            if (row["event"] not in allowed
                    or row["sequence"] != number
                    or row["prior_hash"] != prior
                    or row["initial_assessment_ref"] != original.assessment_ref
                    or row["before_step"] != last_step
                    or row["observed_step"] != last_step + 1
                    or not isinstance(row["source_cue_ref"], str)
                    or not row["source_cue_ref"] or row["source_cue_ref"] in seen
                    or row["command_hash"] != digest(PrimitiveCommand("attendre", {}).as_dict())
                    or not all(isinstance(row[f], str) and len(row[f]) == 64 for f in (
                        "before_percept_sha", "after_percept_sha"))
                    or row["hash"] != digest(value)):
                raise ValueError("bad provenance, time, hash or duplicate")
            if row["event"] == "revision_to_unknown":
                if revised:
                    raise ValueError("duplicate revision")
                revised = True
            if row["event"] == "additional_passive_evidence" and not revised:
                raise ValueError("reinforcement before revision")
            if row["epistemic_label"] != ("unknown" if revised else "self"):
                raise ValueError("invalid epistemic state")
            prior, last_step = row["hash"], row["observed_step"]
            seen.add(row["source_cue_ref"])
        if image["head_hash"] != prior or image["label"] != ("unknown" if revised else "self"):
            raise ValueError("invalid terminal state")
        return True


def capture(world, step):
    return SymbolicPerception().capture(
        local_state=world.capture_local(t_monde=step).as_dict(),
        telemetry=world.telemetry())


def trial(config, seed, cause, pattern):
    rng = random.Random(seed * 991)
    p = Position(rng.randint(5, 17), rng.randint(5, 17))
    first = p.moved("east")
    world = WorldBody(config=replace(config, initial_position=p),
                      layout=WorldLayout(water_sources=frozenset({first})))
    owner = GoalAgencyService()
    c1 = capture(world, 1)
    move = PrimitiveCommand("se_deplacer", {"direction": "east"})
    owner.preregister(
        assessment_ref=f"assessment:{seed}:{cause}:{pattern}",
        intent_ref=f"intent:{seed}:{cause}:{pattern}",
        life_id=f"lab:{seed}:{cause}:{pattern}",
        goal_ref="goal:water", option_ref="option:move",
        command_hash=digest(move.as_dict()), world_step=1,
        measure="spatial_distance", command=move, capture=c1,
        spatial_target=(first.x, first.y, "water"))
    physics = []
    external = []
    if cause == "confounded":
        payload = {"primitive": "se_deplacer", "schedule": [True]}
        world.apply_scenario_event("set_action_failure_schedule", payload)
        external.append({"step": 1, "operation": "set_action_failure_schedule", "payload": payload})
    t1 = world.apply(move, t_monde=1)
    physics.append({"step": 1, "hash": digest(t1.as_dict()), "effects": dict(t1.effects)})
    if cause == "confounded":
        assert t1.effects.get("scenario_forced_failure") == "se_deplacer"
        assert world.position == p
        payload = {"position": first.as_dict()}
        world.apply_scenario_event("set_position", payload)
        external.append({"step": 1, "operation": "set_position", "payload": payload})
    else:
        assert t1.effects.get("movement") == "moved"
        assert world.position == first
    c2 = capture(world, 2)
    original = owner.evaluate(capture=c2, world_step=2,
                              cue_ref=f"original:{seed}:{cause}:{pattern}",
                              paid=True)
    assert original and original.subjective_agency == "self"
    ledger = EvidenceLedger(original)
    perceptions = [asdict(c1), asdict(c2)]
    before = c2
    sequence = []
    for idx, mode in enumerate(pattern.split("_"), 2):
        wait = PrimitiveCommand("attendre", {})
        transition = world.apply(wait, t_monde=idx)
        assert transition.effects.get("rest") == "attendre"
        physics.append({"step": idx, "hash": digest(transition.as_dict()),
                        "effects": dict(transition.effects)})
        if mode == "passive":
            target = world.position.moved("east")
            payload = {"position": target.as_dict()}
            world.apply_scenario_event("set_position", payload)
            external.append({"step": idx, "operation": "set_position", "payload": payload})
        after = capture(world, idx + 1)
        before_original = deepcopy(owner.export_causal_state())
        marker = ledger.append(before=before, after=after, command=wait,
                               cue_ref=f"cue:{seed}:{cause}:{pattern}:{idx+1}")
        assert owner.export_causal_state() == before_original
        sequence.append(marker)
        perceptions.append(asdict(after))
        before = after
    image = ledger.export()
    assert EvidenceLedger.audit(image)
    assert image["original"] == original.as_dict()
    return {"seed": seed, "cause": cause, "pattern": pattern,
            "perceptions": perceptions, "ledger": image,
            "physical_transitions": physics, "external_interventions": external,
            "sequence": sequence}


def adversarial(row):
    image = row["ledger"]
    assert EvidenceLedger.audit(image)
    def reject(modifier):
        mutated = deepcopy(image)
        modifier(mutated)
        try:
            EvidenceLedger.audit(mutated)
        except ValueError:
            return
        raise AssertionError("forged ledger accepted")
    reject(lambda x: x["original"].__setitem__("subjective_agency", "world"))
    reject(lambda x: x["events"][0].__setitem__("source_cue_ref", x["original"]["cue_ref"]))
    reject(lambda x: x["events"][0].__setitem__("observed_step", 99))
    reject(lambda x: x["events"][0].__setitem__("event", "revision_to_world"))
    reject(lambda x: x["events"][0].__setitem__("before_percept_sha", "0" * 64))
    reject(lambda x: x.__setitem__("head_hash", "0" * 64))
    reject(lambda x: x["events"].append(deepcopy(x["events"][0])))
    reject(lambda x: x["events"][0].__setitem__("epistemic_label", "world"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=False)
    config = build_stage11_reference_runtime().world.config
    rows = []
    for seed in SEEDS:
        for pattern in PATTERNS:
            normal = trial(config, seed, "normal", pattern)
            confounded = trial(config, seed, "confounded", pattern)
            assert normal["perceptions"] == confounded["perceptions"]
            assert normal["ledger"]["label"] == confounded["ledger"]["label"]
            assert [x["event"] for x in normal["ledger"]["events"]] == [
                x["event"] for x in confounded["ledger"]["events"]]
            assert normal["physical_transitions"][0]["effects"] != confounded["physical_transitions"][0]["effects"]
            for row in (normal, confounded):
                rows.append(row)
                adversarial(row)
                (args.output_dir / f'{seed}-{pattern}-{row["cause"]}.json').write_text(
                    json.dumps(row, sort_keys=True, indent=2) + "\n")
    revised = [r for r in rows if r["ledger"]["label"] == "unknown"]
    counter = {}
    for row in rows:
        counter[row["pattern"]] = counter.get(row["pattern"], 0) + 1
    summary = {
        "schema": "stage12-a220-evidence-ledger-v1",
        "code_sha": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "seeds": list(SEEDS), "physical_worlds": len(rows),
        "real_physical_transitions": sum(len(r["physical_transitions"]) for r in rows),
        "initial_external_relocations": sum(
            e["operation"] == "set_position" and e["step"] == 1
            for r in rows for e in r["external_interventions"]),
        "passive_relocations": sum(
            e["operation"] == "set_position" and e["step"] > 1
            for r in rows for e in r["external_interventions"]),
        "per_pattern_worlds": counter, "reconsidered_histories": len(revised),
        "reconsidered_correct_initial_self": sum(r["cause"] == "normal" for r in revised),
        "reconsidered_incorrect_initial_self": sum(r["cause"] == "confounded" for r in revised),
        "revision_events": sum(
            e["event"] == "revision_to_unknown" for r in rows for e in r["ledger"]["events"]),
        "reinforcement_events": sum(
            e["event"] == "additional_passive_evidence" for r in rows for e in r["ledger"]["events"]),
        "production_revisions": 0, "autonomous_lives": 0, "ga06_probe_pairs": 0,
        "runtime_policy_changed": False, "stage12": "PARTIAL", "operator_reception": False,
    }
    assert (summary["physical_worlds"], summary["real_physical_transitions"],
            summary["initial_external_relocations"], summary["passive_relocations"],
            summary["reconsidered_histories"],
            summary["reconsidered_correct_initial_self"],
            summary["reconsidered_incorrect_initial_self"],
            summary["revision_events"], summary["reinforcement_events"]) == (
                64, 192, 32, 64, 48, 24, 24, 48, 16)
    assert all(v == 16 for v in counter.values())
    (args.output_dir / "a220-summary.json").write_text(json.dumps(summary, sort_keys=True, indent=2) + "\n")
    print("A220_SUMMARY " + json.dumps(summary, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
