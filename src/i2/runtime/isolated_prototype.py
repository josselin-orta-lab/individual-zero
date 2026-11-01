"""Bounded, INTERNAL-ONLY I2 causal prototype, never the registered I2 engine.

The existing I2 v5 cognitive SQLite owner charges UC and records Competition
and Action Control. One in-transaction callback commits exactly one local
body effect plus an explicit internal admission, never external motor I/O.
The chosen outcome becomes evidence ONLY at a later first-person capture.

No independent M11 monotone witness, birth attestation, crash recovery,
external actuator, statistical study or natural-learning claim is provided.
A new process may inspect the journal, but cannot resume this prototype.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, replace
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
import tempfile
from uuid import uuid4

from i2.modules.local_survival_reflex import LocalEnergySurvivalReflex
from i2.modules.two_step_survival_plan import assess_collect_then_eat
from i2.modules.survival_plan_viability import PlanAssessment, assess_last_resort
from i2.modules.action_control_boundary import SafetyFinding
from i2.modules.chosen_outcome_study import (
    ChosenOutcomeValuationStudy, ObservedChosenResult, observed_chosen_scores,
)
from i2.modules.cognitive_cycle_fixture import (
    CognitiveCycleFixture, CommitAcknowledgmentLost, FaultInjected, ZERO_HASH,
)
from i2.modules.intention_continuity import FirstPersonCapture
from i2.modules.intention_ingress import ObservationClaim, INTAKE_UC
from i2.modules.competition_preview import UC_PER_CANDIDATE, MAX_VALUE_MAGNITUDE
from i2.modules.action_control_boundary import CONTROL_UC

COLLECT = "affordance:collect:berry_a"
EAT = "affordance:eat:berry_a"
DRINK = "affordance:drink:water"
# Existing I2 study comparator, NOT an endogenous discovered value function.
PRIORS = {COLLECT: 3, EAT: 4, DRINK: 1}
MAX_STEPS = 8
# In-process research-world cadence; not calibrated biology or real time.
WORLD_COGNITIVE_PERIOD = 2
WORLD_TICK_LIMIT = 32
FIRST_STEP = 10
STEP_GAP = 8
SCENARIOS = {
    "stable": (6,) * MAX_STEPS,
    "adverse": (-8,) * MAX_STEPS,
    "neutral": (0,) * MAX_STEPS,
    "reversal": (6, 6, 6, -8, -8, -8, -8, -8),
    # Blind negative-to-positive change at world tick 7. This schedule is
    # exogenous researcher-defined world physics; NEVER a cognitive cue.
    # Locked separately from the original seven-case viability battery.
    "restoration": (-8, -8, -8, 6, 6, 6, 6, 6),
}


def _exogenous_phase(physical_ticks: int, count: int) -> int:
    """Hidden SCRIPTED world clock, never a personal sensory input.

    The first food phase lasts through physical tick 2, the next through
    tick 4, and so on. At zero ticks the first phase holds; once a finite
    scripted horizon ends, the last externally specified payoff persists.
    A cognitive choice may NOT advance this clock or select a payoff epoch.
    """
    if (type(physical_ticks) is not int or physical_ticks < 0 or
            type(count) is not int or count < 1):
        raise PrototypeRefusal("invalid exogenous world phase request")
    return min(max(0, (physical_ticks - 1) // WORLD_COGNITIVE_PERIOD),
               count - 1)


def _exogenous_food_impulse(impulses: tuple[int, ...],
                           physical_ticks: int) -> int:
    return impulses[_exogenous_phase(physical_ticks, len(impulses))]


class PrototypeRefusal(ValueError):
    """Untrusted, inconsistent, stale or terminal local research operation."""


def _json(item: object) -> str:
    return json.dumps(item, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _offers(inventory: int, resources: int) -> tuple[str, ...]:
    actions = [DRINK]
    if resources:
        actions.append(COLLECT)
    if inventory:
        actions.append(EAT)
    return tuple(sorted(actions))


def _admission(life: str, seq: int, action: str, head: str) -> str:
    return "internal:i2:admission:" + sha256(
        _json([life, seq, action, head]).encode("ascii")
    ).hexdigest()


class _ObservationPort:
    def __init__(self, life_ref: str):
        self.life_ref = life_ref
        self.digest: str | None = None

    def verify(self, *, life_ref: str, claim: ObservationClaim, digest: str) -> bool:
        return life_ref == self.life_ref and digest == self.digest == claim.digest()


class _CurrentPort:
    def __init__(self):
        self.capture_ref: str | None = None

    def verify_current(self, *, life_ref: str, frame: object, advice: object) -> bool:
        return frame.life_ref == life_ref and frame.capture_ref == self.capture_ref


class _SafetyPort:
    def __init__(self):
        self.veto = False
        self.energy_reflex: LocalEnergySurvivalReflex | None = None

    def check(self, *, life_ref: str, frame: object, candidate_ref: str,
              control_receipt_ref: str) -> SafetyFinding:
        reflex = self.energy_reflex
        if (reflex is None or frame.capture_ref != reflex.claim.capture.ref or
                frame.claim_digest != reflex.claim.digest() or
                life_ref != reflex.claim.life_ref):
            raise PrototypeRefusal("safety lacks current owner-bound survival reflex")
        offered = [c.semantic_ref for c in frame.candidates
                   if c.candidate_ref == candidate_ref]
        if len(offered) != 1:
            raise PrototypeRefusal("reflex safety candidate is not in paid frame")
        # The reflex changes paid *priority*, never the safety veto.
        # Explicit safety constraints still take precedence over exploration.
        return SafetyFinding(
            life_ref, frame.frame_ref, frame.capture_ref, candidate_ref,
            control_receipt_ref, self.veto,
            "evidence:i2:internal-safety-review",
        )


class _TerminalPort:
    def verify_terminal(self, **kwargs: object) -> bool:
        return False  # No independent terminal witness exists here.


class _UnusedValuation:
    def evaluate_batch(self, **kwargs: object) -> tuple:
        raise PrototypeRefusal("valuation is unavailable during journal inspection")


class _ToyPlanSource:
    """Only energy-local facts: COLLECT and DRINK never restore energy now.

    A new, unrecognized affordance is never labeled not viable. This is
    fixed toy body semantics, not a learned multi-step planner or oracle.
    """
    def __init__(self, claim: ObservationClaim, reflex: LocalEnergySurvivalReflex):
        self.claim, self.reflex = claim, reflex

    def verify(self, *, life_ref: str, claim: ObservationClaim, digest: str) -> bool:
        return (claim == self.claim and life_ref == claim.life_ref
                and digest == claim.digest())

    def verify_plan(self, *, claim: ObservationClaim, plan: PlanAssessment) -> bool:
        return (claim == self.claim and plan.evidence_ref == self.reflex.evidence_ref
                and plan.state == ("NOT_VIABLE" if plan.semantic_ref in
                    (COLLECT, DRINK) else "UNKNOWN"))

    def priority(self) -> str | None:
        if EAT not in self.claim.capture.accessible_semantics:
            return None
        plans = tuple(PlanAssessment(
            ref, "NOT_VIABLE" if ref in (COLLECT, DRINK) else "UNKNOWN",
            self.reflex.evidence_ref)
            for ref in self.claim.capture.accessible_semantics if ref != EAT)
        decision = assess_last_resort(
            claim=self.claim, reflex=self.reflex.snapshot(),
            reflex_source=self.reflex, observation_source=self,
            plan_source=self, food_semantic_ref=EAT, plans=plans)
        return (EAT if decision.status == "LAST_RESORT_RISK_RECONSIDERATION"
                else None)


class _LastResortValuation(ChosenOutcomeValuationStudy):
    """A categorical last-resort priority in the *paid* existing batch.

    Does not change the original H2 scores or infer hidden food payoff.
    Only the current capture-bound local energy source can request EAT.
    Its priority is marked in the published subjective value's evidence ref.
    """

    def __init__(self, *, reflex: LocalEnergySurvivalReflex, **kwargs: object):
        super().__init__(**kwargs)
        if reflex.claim != self.claim:
            raise PrototypeRefusal("foreign or stale survival priority")
        self.reflex = reflex

    def evaluate_batch(self, *, frame: object, receipts: tuple) -> tuple:
        values = super().evaluate_batch(frame=frame, receipts=receipts)
        priority = _ToyPlanSource(self.claim, self.reflex).priority()
        if priority is None:
            return values
        by_semantic = {
            c.candidate_ref: c.semantic_ref for c in frame.candidates
        }
        candidates = [v for v in values if by_semantic[v.candidate_ref] == priority]
        if len(candidates) != 1:
            raise PrototypeRefusal("last-resort food absent from paid batch")
        # If EAT already wins uniquely, no artificial boost is needed.
        competitors = [v.value for v in values
                       if v.candidate_ref != candidates[0].candidate_ref]
        if not competitors or candidates[0].value > max(competitors):
            return values
        top = max(v.value for v in values)
        # Categorical ordering, not a tuned reward or a claim food is safe.
        if top >= MAX_VALUE_MAGNITUDE:
            raise PrototypeRefusal("cannot encode bounded last-resort priority")
        return tuple(
            replace(v, value=top + 1,
                    evidence_ref=v.evidence_ref + ":last-resort-energy")
            if v is candidates[0] else v
            for v in values
        )


class _PreviousResults:
    def __init__(self, records: tuple[ObservedChosenResult, ...]):
        self.known = frozenset(records)

    def verify_chosen_result(self, *, result: ObservedChosenResult) -> bool:
        return result in self.known


@dataclass(frozen=True)
class PrototypeStep:
    seq: int
    visible: tuple[str, ...]
    chosen: str | None
    admission_ref: str | None
    control_status: str | None
    before_energy: int
    energy: int
    inventory: int
    resources: int
    terminal: bool
    actual_uc_spent: int
    remaining_uc: int
    external_motor_authority: str = "NONE"


class IsolatedI2:
    """Single local state owner, bounded in-process only, no cold resumption."""

    def __init__(self, path: Path, life_ref: str, genesis_ref: str, *,
                 inspection_only: bool = False) -> None:
        self.path = Path(path)
        self.life_ref = life_ref
        self.genesis_ref = genesis_ref
        self.inspection_only = inspection_only
        self.halted = False
        self.observations = _ObservationPort(life_ref)
        self.current = _CurrentPort()
        self.safety = _SafetyPort()

    @classmethod
    def create(cls, path: Path, *, learning: bool, impulses: tuple[int, ...],
               initial_uc: int = 60, initial_energy: int = 40,
               resources: int = 8,
               last_resort_exploration: bool = False) -> IsolatedI2:
        if (type(learning) is not bool or
                type(last_resort_exploration) is not bool or
                type(impulses) is not tuple or
                not 1 <= len(impulses) <= MAX_STEPS or
                any(type(n) is not int or not -8 <= n <= 8 for n in impulses)
                or type(initial_uc) is not int or not 0 <= initial_uc <= 1000
                or type(initial_energy) is not int or not 1 <= initial_energy <= 100
                or type(resources) is not int or not 0 <= resources <= 32):
            raise PrototypeRefusal("invalid bounded isolated prototype configuration")
        identity = uuid4().hex
        obj = cls(path, "i2:prototype:life:" + identity,
                  "i2:prototype:genesis:" + identity)
        try:
            CognitiveCycleFixture.create(
                path=obj.path, life_ref=obj.life_ref, synthetic_uc=initial_uc,
                observation_source=obj.observations, valuation_source=_UnusedValuation(),
                current_source=obj.current, safety_source=obj.safety,
                genesis_ref=obj.genesis_ref, terminal_source=_TerminalPort(),
            )
        except FileExistsError as exc:
            raise PrototypeRefusal("refuse reused or existing local identity file") from exc
        # Cognition creates the only SQLite owner. A partially initialized
        # genesis remains unusable: inspection requires both complete schemas.
        with obj._connect() as db:
            db.executescript("""
                CREATE TABLE proto_meta(
                    id INTEGER PRIMARY KEY CHECK(id=1),
                    life_ref TEXT NOT NULL, genesis_ref TEXT NOT NULL,
                    learning INTEGER NOT NULL CHECK(learning IN (0,1)),
                    last_resort_exploration INTEGER NOT NULL
                        CHECK(last_resort_exploration IN (0,1)),
                    impulses_json TEXT NOT NULL,
                    initial_energy INTEGER NOT NULL, initial_resources INTEGER NOT NULL);
                CREATE TABLE proto_state(
                    id INTEGER PRIMARY KEY CHECK(id=1),
                    revision INTEGER NOT NULL, energy INTEGER NOT NULL,
                    inventory INTEGER NOT NULL, resources INTEGER NOT NULL,
                    terminal INTEGER NOT NULL CHECK(terminal IN (0,1)),
                    tick_count INTEGER NOT NULL DEFAULT 0 CHECK(tick_count>=0));
                CREATE TABLE proto_ticks(
                    seq INTEGER PRIMARY KEY,
                    after_revision INTEGER NOT NULL CHECK(after_revision>=0),
                    before_energy INTEGER NOT NULL, energy INTEGER NOT NULL,
                    terminal INTEGER NOT NULL CHECK(terminal IN (0,1)),
                    remaining_uc INTEGER NOT NULL,
                    cognition_head TEXT NOT NULL);
                CREATE TABLE proto_steps(
                    seq INTEGER PRIMARY KEY, capture_ref TEXT NOT NULL UNIQUE,
                    capture_step INTEGER NOT NULL UNIQUE,
                    offered_json TEXT NOT NULL, action_ref TEXT,
                    admission_ref TEXT UNIQUE, control_status TEXT,
                    observed_step INTEGER NOT NULL, before_energy INTEGER NOT NULL,
                    net INTEGER NOT NULL, energy INTEGER NOT NULL,
                    inventory INTEGER NOT NULL, resources INTEGER NOT NULL,
                    terminal INTEGER NOT NULL, remaining_uc INTEGER NOT NULL,
                    cognition_head TEXT NOT NULL UNIQUE);
            """)
            db.execute("BEGIN IMMEDIATE")
            db.execute("INSERT INTO proto_meta VALUES(1,?,?,?,?,?,?,?)", (
                obj.life_ref, obj.genesis_ref, int(learning),
                int(last_resort_exploration), _json(impulses),
                initial_energy, resources))
            db.execute("INSERT INTO proto_state VALUES(1,0,?,0,?,0,0)",
                       (initial_energy, resources))
            db.commit()
        obj.audit()
        return obj

    @classmethod
    def inspect(cls, path: Path) -> IsolatedI2:
        """Read-only cold audit; intentionally NO cold restart of action authority."""
        path = Path(path)
        if path.is_symlink() or not path.is_file():
            raise PrototypeRefusal("absent or linked SQLite prototype")
        with sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True) as db:
            row = db.execute(
                "SELECT life_ref,genesis_ref FROM proto_meta WHERE id=1"
            ).fetchone()
        if row is None:
            raise PrototypeRefusal("incomplete local genesis")
        obj = cls(path, row[0], row[1], inspection_only=True)
        obj.audit()
        return obj

    def _connect(self) -> sqlite3.Connection:
        if self.path.is_symlink() or not self.path.is_file():
            raise PrototypeRefusal("absent or linked SQLite prototype")
        db = sqlite3.connect(self.path.resolve().as_uri() + "?mode=rw",
                             uri=True, timeout=5)
        db.execute("PRAGMA busy_timeout=5000")
        db.execute("PRAGMA synchronous=FULL")
        return db

    def _read(self) -> tuple[dict, dict, tuple[dict, ...]]:
        with self._connect() as db:
            db.row_factory = sqlite3.Row
            meta = db.execute("SELECT * FROM proto_meta WHERE id=1").fetchone()
            state = db.execute("SELECT * FROM proto_state WHERE id=1").fetchone()
            rows = db.execute("SELECT * FROM proto_steps ORDER BY seq").fetchall()
        if (meta is None or state is None or
                (meta["life_ref"], meta["genesis_ref"]) !=
                (self.life_ref, self.genesis_ref)):
            raise PrototypeRefusal("foreign or incomplete prototype identity")
        return dict(meta), dict(state), tuple(dict(r) for r in rows)

    def _fixture(self, valuation: object) -> CognitiveCycleFixture:
        return CognitiveCycleFixture.reopen(
            path=self.path, life_ref=self.life_ref,
            observation_source=self.observations, valuation_source=valuation,
            current_source=self.current, safety_source=self.safety,
            genesis_ref=self.genesis_ref, terminal_source=_TerminalPort(),
        )

    def _claim(self, index: int, energy: int, inventory: int,
               resources: int, records: tuple[dict, ...], *,
               physical_ticks: int) -> ObservationClaim:
        offered = _offers(inventory, resources)
        refs = [f"evidence:i2:capture:{index}", f"evidence:i2:energy:{energy}"]
        refs.extend(f"evidence:i2:outcome:{r['seq']}" for r in records
                    if r["action_ref"] is not None)
        return ObservationClaim(
            self.life_ref,
            FirstPersonCapture(
                FIRST_STEP + STEP_GAP * index + physical_ticks,
                f"capture:i2:{index}",
                "goal:food", offered),
            f"source:i2:previous-commit:{index}",
            tuple(sorted(refs)),
        )

    def _history(self, records: tuple[dict, ...]) -> tuple[ObservedChosenResult, ...]:
        return tuple(ObservedChosenResult(
            self.life_ref, r["capture_ref"], r["action_ref"],
            r["observed_step"], f"evidence:i2:outcome:{r['seq']}", r["net"],
        ) for r in records if r["action_ref"] is not None)

    def audit(self) -> dict:
        """Check whole local world/cognition/UC causal replay, NOT external M11."""
        meta, state, rows = self._read()
        cognition = self._fixture(_UnusedValuation()).audit()
        if (state["revision"] != len(rows) or cognition["committed"] != len(rows)
                or len(rows) > len(json.loads(meta["impulses_json"]))
                or cognition["motor_authority"] != "NONE"
                or cognition["synthetic_terminal"]):
            raise PrototypeRefusal("world and paid cognition revisions diverge")
        impulses = tuple(json.loads(meta["impulses_json"]))
        with self._connect() as db:
            capacity = db.execute("SELECT capacity FROM identity WHERE id=1").fetchone()[0]
            events = db.execute(
                "SELECT seq,capture_ref,physical_step,event_hash,event_json "
                "FROM events ORDER BY seq").fetchall()
            db.row_factory = sqlite3.Row
            ticks = tuple(dict(row) for row in db.execute(
                "SELECT seq,after_revision,before_energy,energy,terminal,"
                "remaining_uc,cognition_head FROM proto_ticks ORDER BY seq"))
        if len(events) != len(rows) or state["tick_count"] != len(ticks):
            raise PrototypeRefusal("missing cognitive source event")
        energy, inventory, resources = (
            meta["initial_energy"], 0, meta["initial_resources"])
        used_uc = 0
        earlier: list[dict] = []
        terminal = False
        tick_cursor = 0

        def replay_metabolism(after_revision: int, previous_head: str) -> None:
            nonlocal energy, terminal, tick_cursor
            while (tick_cursor < len(ticks) and
                   ticks[tick_cursor]["after_revision"] == after_revision):
                tick = ticks[tick_cursor]
                if (terminal or tick["seq"] != tick_cursor + 1 or
                        tick["before_energy"] != energy or
                        tick["remaining_uc"] != capacity - used_uc or
                        tick["cognition_head"] != previous_head):
                    raise PrototypeRefusal("autonomic tick or UC provenance mismatch")
                energy = max(0, energy - 1)
                terminal = energy == 0
                if tick["energy"] != energy or tick["terminal"] != int(terminal):
                    raise PrototypeRefusal("autonomic energy not replayable")
                tick_cursor += 1

        for i, (row, saved) in enumerate(zip(rows, events)):
            previous_head = ZERO_HASH if i == 0 else events[i - 1][3]
            replay_metabolism(i, previous_head)
            if terminal or row["seq"] != i + 1 or saved[0] != i + 1:
                raise PrototypeRefusal("post-terminal or nonsequential transition")
            claim = self._claim(i, energy, inventory, resources, tuple(earlier),
                                physical_ticks=tick_cursor)
            event = json.loads(saved[4])
            if (row["capture_ref"] != claim.capture.ref or
                    row["capture_step"] != claim.capture.step or
                    row["offered_json"] != _json(claim.capture.accessible_semantics)
                    or row["observed_step"] != claim.capture.step + 1
                    or row["before_energy"] != energy
                    or row["cognition_head"] != saved[3]
                    or saved[1:3] != (claim.capture.ref, claim.capture.step)
                    or event["claim_digest"] != claim.digest()
                    or event["claim"]["source_event_ref"] != claim.source_event_ref
                    or tuple(event["claim"]["subjective_evidence_refs"]) !=
                       claim.subjective_evidence_refs
                    or event["claim"]["capture"]["accessible_semantics"] !=
                       list(claim.capture.accessible_semantics)):
                raise PrototypeRefusal("first-person chronology or body provenance mismatch")
            frame, review = event["frame"], event["control_review"]
            status = None if review is None else review["status"]
            # Reject a local journal that bypassed the survival constraint.
            # This recomputes from prior committed body state, without reading
            # a hidden food phase or trusting the saved safety label.
            safety = event["safety_finding"]
            if safety is not None and frame is not None:
                selected_semantics = [
                    c["semantic_ref"] for c in frame["candidates"]
                    if c["candidate_ref"] == safety["candidate_ref"]
                ]
                if len(selected_semantics) != 1:
                    raise PrototypeRefusal("unbound reflex safety candidate")
                local_reflex = LocalEnergySurvivalReflex(claim, energy)
                if (local_reflex.last_resort_food_priority() == EAT and
                        selected_semantics[0] != EAT and
                        safety["evidence_ref"] == local_reflex.evidence_ref):
                    raise PrototypeRefusal("reflex evidence forged as veto")
            action = None
            if status == "REVIEWED_NOT_ADMITTED":
                if frame is None or review is None:
                    raise PrototypeRefusal("unbound control admission")
                selected = [
                    c["semantic_ref"] for c in frame["candidates"]
                    if c["candidate_ref"] == review["suggested_candidate_ref"]
                ]
                safety = event["safety_finding"]
                control = event["control_receipt"]
                if (len(selected) != 1 or selected[0] not in claim.capture.accessible_semantics
                        or safety is None or safety["veto"] is not False
                        or control is None or
                        control["ref"] != review["control_receipt_ref"]):
                    raise PrototypeRefusal("action lacks paid fresh safety review")
                action = selected[0]
            elif review is not None and review["suggested_candidate_ref"] is not None:
                raise PrototypeRefusal("veto or abstention used an action")
            admission = _admission(self.life_ref, i + 1, action, saved[3]) if action else None
            if (row["action_ref"] != action or row["admission_ref"] != admission
                    or row["control_status"] != status):
                raise PrototypeRefusal("internal motor admission mismatch")
            if frame is not None:
                history = self._history(tuple(earlier)) if meta["learning"] else ()
                scores = observed_chosen_scores(
                    claim=claim, results=history, source=_PreviousResults(history),
                    priors=PRIORS,
                )
                mapped = {c["candidate_ref"]: c["semantic_ref"]
                          for c in frame["candidates"]}
                values = event["advice"]["values"]
                priority = (_ToyPlanSource(
                    claim, LocalEnergySurvivalReflex(claim, energy)).priority()
                    if meta["last_resort_exploration"] else None)
                priority_applied = False
                if priority in mapped.values():
                    competing = [scores[k] for k in mapped.values() if k != priority]
                    if competing and scores[priority] <= max(competing):
                        top = max(scores[k] for k in mapped.values())
                        if top >= MAX_VALUE_MAGNITUDE:
                            raise PrototypeRefusal("last-resort score cannot be bounded")
                        scores[priority] = top + 1
                        priority_applied = True
                if (len(values) != len(mapped) or any(
                        v["candidate_ref"] not in mapped
                        or v["value"] != scores[mapped[v["candidate_ref"]]]
                        or (v["evidence_ref"].endswith(":last-resort-energy") !=
                            (priority_applied and
                             mapped[v["candidate_ref"]] == priority))
                        for v in values)):
                    raise PrototypeRefusal("unobserved or unbound priority influenced paid score")
            before = energy
            cost = 1 if action is None else 2
            impulse = 0
            if action == COLLECT:
                if resources <= 0:
                    raise PrototypeRefusal("collected absent resource")
                resources -= 1
                inventory += 1
            elif action == EAT:
                if inventory <= 0:
                    raise PrototypeRefusal("ate absent inventory")
                inventory -= 1
                impulse = _exogenous_food_impulse(impulses, tick_cursor)
            elif action not in (None, DRINK):
                raise PrototypeRefusal("unknown physical action")
            energy = max(0, min(100, energy - cost + impulse))
            terminal = energy == 0
            used_uc += event["intake_uc"] + event["competition_uc"] + event["control_uc"]
            if (row["net"] != energy - before or row["energy"] != energy
                    or row["inventory"] != inventory or row["resources"] != resources
                    or row["terminal"] != int(terminal)
                    or row["remaining_uc"] != capacity - used_uc):
                raise PrototypeRefusal("body effect or paid UC not replayable")
            earlier.append(row)
        last_head = ZERO_HASH if not events else events[-1][3]
        replay_metabolism(len(rows), last_head)
        if tick_cursor != len(ticks):
            raise PrototypeRefusal("autonomic event ordered after unknown revision")
        if (state["energy"], state["inventory"], state["resources"],
                state["terminal"]) != (energy, inventory, resources, int(terminal)):
            raise PrototypeRefusal("head state contradicts causal journal")
        if cognition["remaining_synthetic_uc"] != capacity - used_uc:
            raise PrototypeRefusal("separate or free synthetic UC")
        return {"life_ref": self.life_ref, "genesis_ref": self.genesis_ref,
                "revision": len(rows), "physical_ticks": tick_cursor,
                "energy": energy, "inventory": inventory,
                "resources": resources, "terminal": terminal,
                "remaining_uc": capacity - used_uc, "actual_uc_spent": used_uc,
                "motor_scope": "INTERNAL_ONLY", "m11_authenticated": False,
                "engine_registered": False, "science": "NOT_ESTABLISHED"}

    def decision_evidence(self) -> tuple[dict, ...]:
        """Researcher-only readout of AUDITED predecision states and paid scores.

        This is a read-only inspection surface, not a sensor or a new state
        owner. It never feeds the subject or changes its policy. A local
        replay check is NOT an external M11 attestation.
        """
        head = self.audit()
        meta, _, rows = self._read()
        with self._connect() as db:
            capacity = db.execute(
                "SELECT capacity FROM identity WHERE id=1"
            ).fetchone()[0]
            saved = db.execute(
                "SELECT seq,event_hash,event_json FROM events ORDER BY seq"
            ).fetchall()
            tick_revisions = tuple(row[0] for row in db.execute(
                "SELECT after_revision FROM proto_ticks ORDER BY seq"))
        if len(rows) != head["revision"] or len(saved) != len(rows):
            raise PrototypeRefusal("decision inspection crossed a revision")
        inventory, resources = 0, meta["initial_resources"]
        remaining = capacity
        experienced: list[dict] = []
        output = []
        for row, (seq, digest, payload) in zip(rows, saved):
            if seq != row["seq"] or digest != row["cognition_head"]:
                raise PrototypeRefusal("unbound decision inspection")
            event = json.loads(payload)
            frame, advice = event["frame"], event["advice"]
            values = {}
            if frame is not None:
                if advice is None:
                    raise PrototypeRefusal("missing paid competition evidence")
                refs = {c["candidate_ref"]: c["semantic_ref"]
                        for c in frame["candidates"]}
                for v in advice["values"]:
                    if v["candidate_ref"] not in refs:
                        raise PrototypeRefusal("unbound candidate valuation")
                    values[refs[v["candidate_ref"]]] = v["value"]
                if len(values) != len(refs):
                    raise PrototypeRefusal("incomplete paid valuation readout")
            elif advice is not None:
                raise PrototypeRefusal("advice without paid frame")
            spent = (event["intake_uc"] + event["competition_uc"] +
                     event["control_uc"])
            # Diagnostic from the same already audited predecision energy.
            # It cannot select/veto an action or alter an existing score.
            claim = self._claim(
                seq - 1, row["before_energy"], inventory, resources,
                tuple(rows[:seq - 1]),
                physical_ticks=sum(1 for revision in tick_revisions if revision < seq),
            )
            reflex = LocalEnergySurvivalReflex(claim, row["before_energy"])
            if event["claim_digest"] != claim.digest():
                raise PrototypeRefusal("reflex capture diverges from committed event")
            # Public, audited clock-only feasibility under the known fixed
            # two-tick cognition cadence. This remains a researcher readout.
            delay = WORLD_COGNITIVE_PERIOD
            plan = assess_collect_then_eat(
                claim=claim, energy=row["before_energy"],
                inventory=inventory, resources=resources,
                ticks_before_second_action=delay,
            )
            output.append({
                "two_step_collect_eat": {
                    "status": plan.status,
                    "ticks_before_second_action": delay,
                    "pre_food_energy": plan.guaranteed_pre_food_energy,
                    "food_outcome": plan.food_outcome,
                    "motor_authority": plan.motor_authority,
                    "researcher_only": True,
                },
                "survival_reflex": {
                    "state": reflex.state,
                    "evidence_ref": reflex.evidence_ref,
                    "claim_digest": reflex.snapshot().claim_digest,
                    "authority": "LOCAL_NON_MOTOR_ONLY",
                },
                "seq": seq,
                "physical_ticks_before": sum(
                    1 for revision in tick_revisions if revision < seq),
                # RESEARCHER-ONLY explanation, never in the subject's
                # current claim, subjective evidence or valuation source.
                "exogenous_food_phase": _exogenous_phase(
                    sum(1 for revision in tick_revisions if revision < seq),
                    len(json.loads(meta["impulses_json"]))),
                "before_energy": row["before_energy"],
                "before_inventory": inventory,
                "before_resources": resources,
                "visible": tuple(json.loads(row["offered_json"])),
                "subjective_outcomes_available": tuple(
                    dict(item) for item in experienced
                ),
                "outcomes_used_by_valuation": (
                    tuple(dict(item) for item in experienced)
                    if meta["learning"] else ()
                ),
                "candidate_scores": dict(sorted(values.items())),
                "last_resort_priority_applied": any(
                    v["evidence_ref"].endswith(":last-resort-energy")
                    for v in (advice["values"] if advice is not None else ())
                ),
                "chosen": row["action_ref"],
                "control_status": row["control_status"],
                "internal_admission": row["admission_ref"] is not None,
                "uc_before": remaining,
                "uc_spent": spent,
                "uc_remaining": row["remaining_uc"],
                "energy_after": row["energy"],
                "inventory_after": row["inventory"],
                "resources_after": row["resources"],
                "terminal": bool(row["terminal"]),
            })
            remaining -= spent
            if remaining != row["remaining_uc"]:
                raise PrototypeRefusal("decision readout invented free UC")
            if row["action_ref"] is not None:
                experienced.append({
                    "seq": seq, "action": row["action_ref"],
                    "observed_net": row["net"],
                    "observed_step": row["observed_step"],
                })
            inventory, resources = row["inventory"], row["resources"]
        return tuple(output)

    def _apply(self, *, conn: sqlite3.Connection, seq: int, claim: ObservationClaim,
               frame: dict | None, control_review: dict | None,
               remaining_uc: int, event_head: str) -> None:
        """Private v5 same-COMMIT hook; not a reusable external motor executor."""
        if not conn.in_transaction:
            raise PrototypeRefusal("physical effect outside owner transaction")
        meta = conn.execute(
            "SELECT life_ref,genesis_ref,impulses_json FROM proto_meta WHERE id=1"
        ).fetchone()
        state = conn.execute(
            "SELECT revision,energy,inventory,resources,terminal,tick_count "
            "FROM proto_state WHERE id=1").fetchone()
        if (meta is None or meta[:2] != (self.life_ref, self.genesis_ref)
                or state is None or state[0] + 1 != seq or state[4]):
            raise PrototypeRefusal("foreign, stale or terminal internal actuation")
        prior = tuple(dict(zip(
            ("seq", "capture_ref", "action_ref", "observed_step", "net"),
            r)) for r in conn.execute(
                "SELECT seq,capture_ref,action_ref,observed_step,net "
                "FROM proto_steps ORDER BY seq"))
        expected = self._claim(state[0], state[1], state[2], state[3], prior,
                               physical_ticks=state[5])
        if claim != expected:
            raise PrototypeRefusal("capture not issued from previous committed world")
        event_row = conn.execute(
            "SELECT event_json,event_hash FROM events WHERE seq=?", (seq,)
        ).fetchone()
        if event_row is None or event_row[1] != event_head:
            raise PrototypeRefusal("unbound cognitive COMMIT")
        event = json.loads(event_row[0])
        if (event["claim_digest"] != claim.digest() or
                event["control_review"] != control_review or event["frame"] != frame
                or conn.execute("SELECT remaining_uc FROM account WHERE id=1")
                       .fetchone()[0] != remaining_uc):
            raise PrototypeRefusal("unbound safety, source or UC account")
        action = None
        admission = None
        status = None if control_review is None else control_review["status"]
        if status == "REVIEWED_NOT_ADMITTED":
            if frame is None:
                raise PrototypeRefusal("missing candidate frame")
            selected = [c["semantic_ref"] for c in frame["candidates"]
                        if c["candidate_ref"] == control_review["suggested_candidate_ref"]]
            safety, receipt = event["safety_finding"], event["control_receipt"]
            if (len(selected) != 1 or selected[0] not in expected.capture.accessible_semantics
                    or safety is None or safety["veto"] is not False
                    or receipt is None or
                    receipt["ref"] != control_review["control_receipt_ref"]):
                raise PrototypeRefusal("no fresh paid internal action clearance")
            action = selected[0]
            admission = _admission(self.life_ref, seq, action, event_head)
        elif control_review is not None and control_review["suggested_candidate_ref"] is not None:
            raise PrototypeRefusal("vetoed or ambiguous advice cannot act")
        energy, inventory, resources = state[1:4]
        before = energy
        cost = 1 if action is None else 2
        impulse = 0
        if action == COLLECT:
            resources -= 1
            inventory += 1
        elif action == EAT:
            inventory -= 1
            # Exogenous conditions belong to the WORLD physical clock.
            # Two subjects acting at the same tick see the same hidden
            # food payoff despite different numbers of earlier decisions.
            impulse = _exogenous_food_impulse(
                tuple(json.loads(meta[2])), state[5])
        elif action not in (None, DRINK):
            raise PrototypeRefusal("invalid physical action")
        if inventory < 0 or resources < 0:
            raise PrototypeRefusal("physical resource underflow")
        energy = max(0, min(100, energy - cost + impulse))
        terminal = int(energy == 0)
        conn.execute(
            "UPDATE proto_state SET revision=?,energy=?,inventory=?,resources=?,"
            "terminal=? WHERE id=1", (seq, energy, inventory, resources, terminal))
        conn.execute("INSERT INTO proto_steps VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
            seq, claim.capture.ref, claim.capture.step,
            _json(claim.capture.accessible_semantics), action, admission, status,
            claim.capture.step + 1, before, energy - before, energy,
            inventory, resources, terminal, remaining_uc, event_head,
        ))

    def advance_physics(self, *, fault: str | None = None) -> dict:
        """Advance one metabolic tick even with ZERO UC and no cognition.

        Externally scheduled toy physical time, NOT a real-time Scheduler.
        Runs inside the SAME owner SQLite database and transaction. Never
        consults Competition, consumes hidden impulses, or gains motor authority.
        A lost COMMIT acknowledgment halts this in-process executor.
        """
        if self.inspection_only or self.halted:
            raise PrototypeRefusal("prototype is inspection-only or halted")
        if fault not in (None, "before_commit", "after_commit"):
            raise PrototypeRefusal("invalid physical tick fault")
        prior = self.audit()
        if prior["terminal"]:
            raise PrototypeRefusal("terminal body cannot advance")
        if prior["physical_ticks"] >= WORLD_TICK_LIMIT:
            raise PrototypeRefusal("physical research horizon exhausted")
        db = self._connect()
        try:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute(
                "SELECT revision,energy,inventory,resources,terminal,tick_count "
                "FROM proto_state WHERE id=1").fetchone()
            account = db.execute(
                "SELECT committed,remaining_uc,chain_head "
                "FROM account WHERE id=1").fetchone()
            if (row is None or account is None or row[4] or
                    row[0] != prior["revision"] or
                    row[1] != prior["energy"] or
                    row[5] != prior["physical_ticks"] or
                    account[0] != row[0] or
                    account[1] != prior["remaining_uc"]):
                raise PrototypeRefusal("stale or terminal physical owner")
            energy = max(0, row[1] - 1)
            terminal = int(energy == 0)
            tick_seq = row[5] + 1
            db.execute(
                "UPDATE proto_state SET energy=?,terminal=?,tick_count=? "
                "WHERE id=1", (energy, terminal, tick_seq))
            db.execute(
                "INSERT INTO proto_ticks VALUES(?,?,?,?,?,?,?)",
                (tick_seq, row[0], row[1], energy, terminal,
                 account[1], account[2]))
            if fault == "before_commit":
                raise FaultInjected("physical tick rolled back before COMMIT")
            db.execute("COMMIT")
            if fault == "after_commit":
                raise CommitAcknowledgmentLost(
                    "physical tick may be committed; inspect only, never retry")
        except BaseException as exc:
            if db.in_transaction:
                db.execute("ROLLBACK")
            if isinstance(exc, (sqlite3.Error, CommitAcknowledgmentLost)):
                self.halted = True
            raise
        finally:
            db.close()
        try:
            verified = self.audit()
        except BaseException:
            self.halted = True
            raise
        if (verified["physical_ticks"] != prior["physical_ticks"] + 1 or
                verified["revision"] != prior["revision"] or
                verified["remaining_uc"] != prior["remaining_uc"] or
                verified["energy"] != energy):
            self.halted = True
            raise PrototypeRefusal("ambiguous physical tick after COMMIT")
        return {
            "seq": tick_seq, "after_cognitive_revision": prior["revision"],
            "before_energy": row[1], "energy": energy,
            "terminal": bool(terminal), "remaining_uc": verified["remaining_uc"],
            "cognition_committed": False, "external_motor_authority": "NONE",
        }

    def run_world(self, *, ticks: int = 12) -> dict:
        """Run a fixed internal world cadence without per-tick operator calls.

        This synchronous bounded runner owns WHEN the body ticks and WHEN
        cognition is eligible, but uses only the existing SQLite state
        owner. No extra world truth or externally admitted motor commands.
        The operator chooses a *maximum observation horizon*, never an
        action or a hidden payoff. A physical tick always precedes any
        cognitive opportunity, including when UC is exhausted.

        This is NOT a background clock, a real-time scheduler, M11, a
        scientific survival test or independently authenticated execution.
        """
        if type(ticks) is not int or not 1 <= ticks <= WORLD_TICK_LIMIT:
            raise PrototypeRefusal("invalid bounded world observation horizon")
        if self.inspection_only or self.halted:
            raise PrototypeRefusal("world execution unavailable")
        started = self.audit()
        if started["terminal"]:
            raise PrototypeRefusal("terminal individual cannot run a world")
        trace: list[dict] = []
        meta, _, _ = self._read()
        exogenous_count = len(json.loads(meta["impulses_json"]))
        for _ in range(ticks):
            previous = self.audit()
            if (previous["terminal"] or
                    previous["physical_ticks"] >= WORLD_TICK_LIMIT):
                break
            # The world always advances before any possible cognition.
            tick = self.advance_physics()
            state = self.audit()
            due = tick["seq"] % WORLD_COGNITIVE_PERIOD == 0
            action = None
            cognitive = None
            if tick["terminal"]:
                reason = "PHYSICAL_TERMINAL"
            elif not due:
                reason = "NO_COGNITIVE_WINDOW"
            else:
                meta, body, _ = self._read()
                if state["revision"] >= len(json.loads(meta["impulses_json"])):
                    reason = "COGNITIVE_HORIZON_EXHAUSTED"
                else:
                    # Reserve all costs, including a safety review, using
                    # the ACTUAL I2-owned port price constants. Avoid an
                    # incompletely paid cognitive attempt or free action.
                    available = _offers(body["inventory"], body["resources"])
                    required_uc = (
                        INTAKE_UC + len(available) * UC_PER_CANDIDATE +
                        CONTROL_UC
                    )
                    if state["remaining_uc"] < required_uc:
                        reason = "COGNITION_UNFUNDED"
                    else:
                        try:
                            cognitive = self.step()
                        except BaseException:
                            # A tick may already be committed. An unknown
                            # action cannot be replayed or skipped casually.
                            self.halted = True
                            raise
                        action = cognitive.chosen
                        reason = ("COGNITIVE_ACTION_COMMITTED" if action
                                  else "COGNITIVE_ABSTENTION_COMMITTED")
            final = self.audit()
            trace.append({
                "physical_tick": tick["seq"],
                "researcher_only_food_phase": _exogenous_phase(
                    tick["seq"], exogenous_count),
                "before_tick_energy": tick["before_energy"],
                "after_tick_energy": tick["energy"],
                "cognitive_due": due,
                "cognitive_committed": cognitive is not None,
                "reason": reason,
                "selected_action": action,
                "internal_admission": (
                    cognitive.admission_ref if cognitive else None),
                "physical_end_energy": final["energy"],
                "cognitive_revision": final["revision"],
                "remaining_uc": final["remaining_uc"],
                "terminal": final["terminal"],
            })
            if final["terminal"]:
                break
        ending = self.audit()
        status = (
            "MODELED_TERMINAL" if ending["terminal"] else
            "RESEARCH_HORIZON_CENSORED" if
            ending["physical_ticks"] >= WORLD_TICK_LIMIT else
            "BOUNDED_OBSERVATION_END_NONTERMINAL"
        )
        return {
            "status": status,
            "scheduler": "IN_PROCESS_FIXED_CADENCE_RESEARCH_ONLY",
            "cognitive_period_ticks": WORLD_COGNITIVE_PERIOD,
            "tick_limit": WORLD_TICK_LIMIT,
            "started_at_physical_tick": started["physical_ticks"],
            "requested_additional_ticks": ticks,
            "trace": tuple(trace),
            "audit": ending,
            "m11_authenticated": False,
            "scientific_verdict": "NOT_ESTABLISHED",
            "external_motor_authority": "NONE",
        }

    def step(self, *, veto: bool = False, fault: str | None = None) -> PrototypeStep:
        if self.inspection_only or self.halted:
            raise PrototypeRefusal("prototype is inspection-only or halted")
        if type(veto) is not bool:
            raise PrototypeRefusal("invalid internal safety veto")
        before = self.audit()
        meta, state, records = self._read()
        if state["terminal"] or state["revision"] >= len(json.loads(meta["impulses_json"])):
            raise PrototypeRefusal("terminal or completed bounded research run")
        index = state["revision"]
        claim = self._claim(index, state["energy"], state["inventory"],
                            state["resources"], records,
                            physical_ticks=state["tick_count"])
        self.observations.digest = claim.digest()
        self.current.capture_ref = claim.capture.ref
        self.safety.veto = veto
        self.safety.energy_reflex = LocalEnergySurvivalReflex(claim, state["energy"])
        past = self._history(records) if meta["learning"] else ()
        evaluator = (_LastResortValuation if meta["last_resort_exploration"]
                     else ChosenOutcomeValuationStudy)
        valuation_args = dict(
            claim=claim, results=past, source=_PreviousResults(past),
            priors=PRIORS,
        )
        valuation = (evaluator(reflex=self.safety.energy_reflex, **valuation_args)
                     if meta["last_resort_exploration"] else
                     evaluator(**valuation_args))
        fixture = self._fixture(valuation)
        try:
            if index == 0:
                # The initial *intention*, never a motor action, must be
                # grounded in the currently observed affordance set. A
                # resource-empty world cannot open "collect" by fiat.
                initial_semantic = (
                    COLLECT if COLLECT in claim.capture.accessible_semantics
                    else claim.capture.accessible_semantics[0]
                )
                receipt = fixture.open(
                    claim=claim, semantic_ref=initial_semantic,
                    evidence_ref=f"evidence:i2:capture:{index}", ttl_steps=64,
                    _fault_at=fault, _g1_lab_hook=self._apply)
            else:
                receipt = fixture.observe(
                    claim=claim, _fault_at=fault, _g1_lab_hook=self._apply)
        except CommitAcknowledgmentLost:
            # Commit MAY have happened. Never replay the same action.
            self.halted = True
            raise
        except sqlite3.Error:
            # Unknown local commit boundary. Inspection only.
            self.halted = True
            raise
        after = self.audit()
        if (after["revision"] != before["revision"] + 1
                or after["actual_uc_spent"] <= before["actual_uc_spent"]):
            self.halted = True
            raise PrototypeRefusal("ambiguous post-commit physical/UC outcome")
        _, _, rows = self._read()
        row = rows[-1]
        return PrototypeStep(
            seq=row["seq"], visible=claim.capture.accessible_semantics,
            chosen=row["action_ref"], admission_ref=row["admission_ref"],
            control_status=row["control_status"],
            before_energy=row["before_energy"], energy=row["energy"],
            inventory=row["inventory"], resources=row["resources"],
            terminal=bool(row["terminal"]),
            actual_uc_spent=before["remaining_uc"] - after["remaining_uc"],
            remaining_uc=row["remaining_uc"],
        )


def paired_decision_contrast(
    observational: tuple[dict, ...], fixed: tuple[dict, ...],
) -> dict:
    """Describe the first difference, not estimate a general learning effect.

    Only an identical *predecision* environment, personal outcome history and
    UC budget permits a policy-rule attribution. Later trajectory contrasts
    after a first different action are confounded by changed world states.
    """
    prechoice_fields = (
        "before_energy", "before_inventory", "before_resources", "visible",
        "physical_ticks_before", "uc_before", "subjective_outcomes_available",
    )
    common = min(len(observational), len(fixed))
    for i in range(common):
        observed, control = observational[i], fixed[i]
        if observed["chosen"] == control["chosen"]:
            continue
        before_matched = all(
            observational[j]["chosen"] == fixed[j]["chosen"]
            and observational[j]["energy_after"] == fixed[j]["energy_after"]
            and observational[j]["inventory_after"] == fixed[j]["inventory_after"]
            and observational[j]["resources_after"] == fixed[j]["resources_after"]
            and observational[j]["uc_spent"] == fixed[j]["uc_spent"]
            for j in range(i)
        )
        same_context = all(observed[k] == control[k] for k in prechoice_fields)
        matched = before_matched and same_context
        scores_changed = {
            semantic: {
                "observational": observed["candidate_scores"].get(semantic),
                "fixed": control["candidate_scores"].get(semantic),
            }
            for semantic in sorted(
                set(observed["candidate_scores"]) |
                set(control["candidate_scores"])
            )
            if observed["candidate_scores"].get(semantic) !=
               control["candidate_scores"].get(semantic)
        }
        status = (
            "MATCHED_PRECHOICE_PROGRAMMED_VALUATION_CONTRAST"
            if matched and scores_changed else
            "SAME_SCORES_UNEXPLAINED_CHOICE_DIFFERENCE"
            if matched else "UNMATCHED_PRECHOICE_NO_CAUSAL_ATTRIBUTION"
        )
        return {
            "classification": status,
            "first_divergence_seq": observed["seq"],
            "matched_prechoice": matched,
            "observational_action": observed["chosen"],
            "fixed_action": control["chosen"],
            "candidate_score_differences": scores_changed,
            "not_a_natural_learning_or_survival_verdict": True,
        }
    return {
        "classification": (
            "NO_ACTION_DIVERGENCE_IN_OBSERVED_HORIZON"
            if len(observational) == len(fixed) else
            "UNEQUAL_EXPOSURE_NO_CAUSAL_ATTRIBUTION"
        ),
        "first_divergence_seq": None,
        "matched_prechoice": None,
        "observational_action": None,
        "fixed_action": None,
        "candidate_score_differences": {},
        "not_a_natural_learning_or_survival_verdict": True,
    }


def demo(scenario: str, *, steps: int = 6,
         last_resort_exploration: bool = False) -> dict:
    """Tiny disposable engineering smoke only, NOT a scientific replicate."""
    if scenario not in SCENARIOS or type(steps) is not int or not 1 <= steps <= MAX_STEPS:
        raise PrototypeRefusal("unknown or unbounded demo")
    if scenario in ("reversal", "restoration"):
        raise PrototypeRefusal(
            "hidden world change requires physical world ticks: use --world / world_demo")
    with tempfile.TemporaryDirectory(prefix="i2-isolated-prototype-") as root:
        arms = {}
        for learning, label in ((True, "observed_chosen"), (False, "fixed")):
            individual = IsolatedI2.create(
                Path(root) / (label + ".sqlite"), learning=learning,
                impulses=SCENARIOS[scenario][:steps],
                last_resort_exploration=last_resort_exploration)
            trace = []
            while len(trace) < steps:
                outcome = individual.step()
                trace.append(asdict(outcome))
                if outcome.terminal:
                    break
            arms[label] = {
                "trace": trace,
                "decisions": individual.decision_evidence(),
                "audit": individual.audit(),
            }
    return {"status": "ISOLATED_RESEARCH_PROTOTYPE_ONLY",
            "scenario": scenario,
            "last_resort_exploration": last_resort_exploration,
            "arms": arms,
            "behavioral_contrast": paired_decision_contrast(
                arms["observed_chosen"]["decisions"], arms["fixed"]["decisions"]),
            "scientific_verdict": "NOT_ESTABLISHED",
            "m11_authenticated": False, "active_engine": False}


def world_endpoint(execution: dict) -> dict:
    """Descriptive observed endpoint, never generalized survival evidence.

    Caller supplies the same owner-audited single-run report. No new state
    owner, alternative body physics, hidden payoff, or policy update.
    """
    trace = execution["trace"]
    audit = execution["audit"]
    terminal = audit["terminal"]
    return {
        "observed_physical_ticks": len(trace),
        "ending_physical_tick": audit["physical_ticks"],
        "modeled_terminal_observed": terminal,
        "modeled_death_tick": (
            trace[-1]["physical_tick"] if terminal else None
        ),
        "right_censored": not terminal,
        "ending_energy": audit["energy"],
        "ending_inventory": audit["inventory"],
        "remaining_uc": audit["remaining_uc"],
        "actual_uc_spent": audit["actual_uc_spent"],
        "paid_decisions": audit["revision"],
        "admitted_internal_actions": sum(
            row["internal_admission"] is not None for row in trace
        ),
        "unfunded_cognitive_windows": sum(
            row["reason"] == "COGNITION_UNFUNDED" for row in trace
        ),
        "world_status": execution["status"],
        "real_world_survival": "NOT_ESTABLISHED",
    }


def paired_world_endpoints(observed: dict, fixed: dict) -> dict:
    """Do not turn unequal terminal observations into a fitness claim."""
    o, f = observed, fixed
    same_window = o["ending_physical_tick"] == f["ending_physical_tick"]
    both_observed_alive = (
        not o["modeled_terminal_observed"] and
        not f["modeled_terminal_observed"]
    )
    if o["paid_decisions"] == f["paid_decisions"] == 0:
        interpretation = "NO_PAID_COGNITIVE_EXPOSURE"
    elif same_window and both_observed_alive:
        interpretation = "COMMON_WINDOW_NONTERMINAL_DESCRIPTIVE_ONLY"
    else:
        interpretation = "TERMINAL_OR_UNEQUAL_EXPOSURE_NO_COMMON_END_ENERGY"
    return {
        "classification": interpretation,
        "learned_modeled_death_tick": o["modeled_death_tick"],
        "fixed_modeled_death_tick": f["modeled_death_tick"],
        "observed_at_same_tick": same_window,
        "ending_energy_difference": (
            o["ending_energy"] - f["ending_energy"]
            if same_window and both_observed_alive else None
        ),
        "ending_energy_is_not_survival_evidence": True,
        "generalized_survival_benefit": "NOT_ESTABLISHED",
        "natural_autonomous_learning": "NOT_ESTABLISHED",
    }


def world_demo(scenario: str, *, ticks: int = 12,
               initial_uc: int = 60, initial_energy: int = 40,
               resources: int = 8,
               last_resort_exploration: bool = False) -> dict:
    """Disposable paired engineering smoke for the world-owned cadence."""
    if (type(last_resort_exploration) is not bool or
            scenario not in SCENARIOS or type(ticks) is not int or
            not 1 <= ticks <= WORLD_TICK_LIMIT or
            type(initial_uc) is not int or not 0 <= initial_uc <= 1000 or
            type(initial_energy) is not int or not 1 <= initial_energy <= 100 or
            type(resources) is not int or not 0 <= resources <= 32):
        raise PrototypeRefusal("invalid bounded world smoke")
    with tempfile.TemporaryDirectory(prefix="i2-world-schedule-") as root:
        arms = {}
        for learning, label in ((True, "observed_chosen"), (False, "fixed")):
            individual = IsolatedI2.create(
                Path(root) / (label + ".sqlite"), learning=learning,
                impulses=SCENARIOS[scenario], initial_uc=initial_uc,
                initial_energy=initial_energy, resources=resources,
                last_resort_exploration=last_resort_exploration)
            execution = individual.run_world(ticks=ticks)
            arms[label] = {
                "execution": execution,
                "endpoint": world_endpoint(execution),
                "decisions": individual.decision_evidence(),
                "audit": individual.audit(),
            }
    return {
        "status": "SYNCHRONOUS_BOUNDED_WORLD_RESEARCH_ONLY",
        "scenario": scenario,
        "last_resort_exploration": last_resort_exploration,
        "exogenous_regime_clock": "PHYSICAL_TICKS_NOT_COGNITIVE_REVISIONS",
        "arms": arms,
        "first_choice_contrast": paired_decision_contrast(
            arms["observed_chosen"]["decisions"],
            arms["fixed"]["decisions"],
        ),
        "world_endpoint_contrast": paired_world_endpoints(
            arms["observed_chosen"]["endpoint"],
            arms["fixed"]["endpoint"],
        ),
        "scientific_verdict": "NOT_ESTABLISHED",
        "m11_authenticated": False,
        "active_engine": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", choices=sorted(SCENARIOS), default="adverse")
    parser.add_argument("--steps", type=int, default=6)
    parser.add_argument("--world", action="store_true",
                        help="Use world-owned bounded physical cadence")
    parser.add_argument("--ticks", type=int, default=12)
    parser.add_argument("--initial-uc", type=int, default=60)
    parser.add_argument("--initial-energy", type=int, default=40)
    parser.add_argument("--resources", type=int, default=8)
    parser.add_argument("--last-resort", action="store_true",
                        help="Opt into researcher-specified emergency food priority")
    args = parser.parse_args()
    if args.world:
        print(_json(world_demo(args.scenario, ticks=args.ticks,
                               initial_uc=args.initial_uc,
                               initial_energy=args.initial_energy,
                               resources=args.resources,
                               last_resort_exploration=args.last_resort)))
    else:
        print(_json(demo(args.scenario, steps=args.steps,
                         last_resort_exploration=args.last_resort)))


if __name__ == "__main__":
    main()
