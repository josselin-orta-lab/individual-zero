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
from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
import tempfile
from uuid import uuid4

from i2.modules.action_control_boundary import SafetyFinding
from i2.modules.chosen_outcome_study import (
    ChosenOutcomeValuationStudy, ObservedChosenResult, observed_chosen_scores,
)
from i2.modules.cognitive_cycle_fixture import (
    CognitiveCycleFixture, CommitAcknowledgmentLost,
)
from i2.modules.intention_continuity import FirstPersonCapture
from i2.modules.intention_ingress import ObservationClaim

COLLECT = "affordance:collect:berry_a"
EAT = "affordance:eat:berry_a"
DRINK = "affordance:drink:water"
# Existing I2 study comparator, NOT an endogenous discovered value function.
PRIORS = {COLLECT: 3, EAT: 4, DRINK: 1}
MAX_STEPS = 8
FIRST_STEP = 10
STEP_GAP = 8
SCENARIOS = {
    "stable": (6,) * MAX_STEPS,
    "adverse": (-8,) * MAX_STEPS,
    "neutral": (0,) * MAX_STEPS,
    "reversal": (6, 6, 6, -8, -8, -8, -8, -8),
}


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

    def check(self, *, life_ref: str, frame: object, candidate_ref: str,
              control_receipt_ref: str) -> SafetyFinding:
        return SafetyFinding(
            life_ref, frame.frame_ref, frame.capture_ref, candidate_ref,
            control_receipt_ref, self.veto, "evidence:i2:internal-safety-review",
        )


class _TerminalPort:
    def verify_terminal(self, **kwargs: object) -> bool:
        return False  # No independent terminal witness exists here.


class _UnusedValuation:
    def evaluate_batch(self, **kwargs: object) -> tuple:
        raise PrototypeRefusal("valuation is unavailable during journal inspection")


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
               resources: int = 8) -> IsolatedI2:
        if (type(learning) is not bool or type(impulses) is not tuple or
                not 1 <= len(impulses) <= MAX_STEPS or
                any(type(n) is not int or not -8 <= n <= 8 for n in impulses)
                or type(initial_uc) is not int or not 1 <= initial_uc <= 1000
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
                    impulses_json TEXT NOT NULL,
                    initial_energy INTEGER NOT NULL, initial_resources INTEGER NOT NULL);
                CREATE TABLE proto_state(
                    id INTEGER PRIMARY KEY CHECK(id=1),
                    revision INTEGER NOT NULL, energy INTEGER NOT NULL,
                    inventory INTEGER NOT NULL, resources INTEGER NOT NULL,
                    terminal INTEGER NOT NULL CHECK(terminal IN (0,1)));
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
            db.execute("INSERT INTO proto_meta VALUES(1,?,?,?,?,?,?)", (
                obj.life_ref, obj.genesis_ref, int(learning), _json(impulses),
                initial_energy, resources))
            db.execute("INSERT INTO proto_state VALUES(1,0,?,0,?,0)",
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
               resources: int, records: tuple[dict, ...]) -> ObservationClaim:
        offered = _offers(inventory, resources)
        refs = [f"evidence:i2:capture:{index}", f"evidence:i2:energy:{energy}"]
        refs.extend(f"evidence:i2:outcome:{r['seq']}" for r in records
                    if r["action_ref"] is not None)
        return ObservationClaim(
            self.life_ref,
            FirstPersonCapture(
                FIRST_STEP + STEP_GAP * index, f"capture:i2:{index}",
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
        if len(events) != len(rows):
            raise PrototypeRefusal("missing cognitive source event")
        energy, inventory, resources = (
            meta["initial_energy"], 0, meta["initial_resources"])
        used_uc = 0
        earlier: list[dict] = []
        terminal = False
        for i, (row, saved) in enumerate(zip(rows, events)):
            if terminal or row["seq"] != i + 1 or saved[0] != i + 1:
                raise PrototypeRefusal("post-terminal or nonsequential transition")
            claim = self._claim(i, energy, inventory, resources, tuple(earlier))
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
                if (len(values) != len(mapped) or any(
                        v["candidate_ref"] not in mapped
                        or v["value"] != scores[mapped[v["candidate_ref"]]]
                        for v in values)):
                    raise PrototypeRefusal("unobserved outcome influenced paid score")
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
                impulse = impulses[i]
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
        if (state["energy"], state["inventory"], state["resources"],
                state["terminal"]) != (energy, inventory, resources, int(terminal)):
            raise PrototypeRefusal("head state contradicts causal journal")
        if cognition["remaining_synthetic_uc"] != capacity - used_uc:
            raise PrototypeRefusal("separate or free synthetic UC")
        return {"life_ref": self.life_ref, "genesis_ref": self.genesis_ref,
                "revision": len(rows), "energy": energy, "inventory": inventory,
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
            output.append({
                "seq": seq,
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
            "SELECT revision,energy,inventory,resources,terminal "
            "FROM proto_state WHERE id=1").fetchone()
        if (meta is None or meta[:2] != (self.life_ref, self.genesis_ref)
                or state is None or state[0] + 1 != seq or state[4]):
            raise PrototypeRefusal("foreign, stale or terminal internal actuation")
        prior = tuple(dict(zip(
            ("seq", "capture_ref", "action_ref", "observed_step", "net"),
            r)) for r in conn.execute(
                "SELECT seq,capture_ref,action_ref,observed_step,net "
                "FROM proto_steps ORDER BY seq"))
        expected = self._claim(state[0], state[1], state[2], state[3], prior)
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
            impulse = json.loads(meta[2])[seq - 1]
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
                            state["resources"], records)
        self.observations.digest = claim.digest()
        self.current.capture_ref = claim.capture.ref
        self.safety.veto = veto
        past = self._history(records) if meta["learning"] else ()
        valuation = ChosenOutcomeValuationStudy(
            claim=claim, results=past, source=_PreviousResults(past), priors=PRIORS)
        fixture = self._fixture(valuation)
        try:
            if index == 0:
                receipt = fixture.open(
                    claim=claim, semantic_ref=COLLECT,
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
        "uc_before", "subjective_outcomes_available",
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


def demo(scenario: str, *, steps: int = 6) -> dict:
    """Tiny disposable engineering smoke only, NOT a scientific replicate."""
    if scenario not in SCENARIOS or type(steps) is not int or not 1 <= steps <= MAX_STEPS:
        raise PrototypeRefusal("unknown or unbounded demo")
    with tempfile.TemporaryDirectory(prefix="i2-isolated-prototype-") as root:
        arms = {}
        for learning, label in ((True, "observed_chosen"), (False, "fixed")):
            individual = IsolatedI2.create(
                Path(root) / (label + ".sqlite"), learning=learning,
                impulses=SCENARIOS[scenario][:steps])
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
            "scenario": scenario, "arms": arms,
            "behavioral_contrast": paired_decision_contrast(
                arms["observed_chosen"]["decisions"], arms["fixed"]["decisions"]),
            "scientific_verdict": "NOT_ESTABLISHED",
            "m11_authenticated": False, "active_engine": False}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", choices=sorted(SCENARIOS), default="adverse")
    parser.add_argument("--steps", type=int, default=6)
    args = parser.parse_args()
    print(_json(demo(args.scenario, steps=args.steps)))


if __name__ == "__main__":
    main()
