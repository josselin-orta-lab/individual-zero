"""G1-LAB: disposable, NON-LIVING closed-loop I2 research demonstrator.

The existing v5 synthetic cognition owner and this deterministic internal body
share ONE SQLite database and ONE local COMMIT per capture. There is no birth,
real motor admission, M11 witness, real Scheduler or external physical effect.
Do not import this module from an I2 engine/runtime entrypoint.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import sqlite3
import tempfile

from i2.modules.action_control_boundary import SafetyFinding
from i2.modules.chosen_outcome_study import (
    ChosenOutcomeValuationStudy, ObservedChosenResult,
)
from i2.modules.cognitive_cycle_fixture import CognitiveCycleFixture
from i2.modules.intention_continuity import FirstPersonCapture
from i2.modules.intention_ingress import ObservationClaim

COLLECT = "affordance:collect:berry_a"
EAT = "affordance:eat:berry_a"
DRINK = "affordance:drink:water"
PRIORS = {COLLECT: 3, EAT: 4, DRINK: 1}  # researcher inputs, not learned
STEP_GAP = 8
FIRST_STEP = 10
MAX_CAPTURES = 8
REGIMES = {
    "stable": (8,) * MAX_CAPTURES,
    "adverse": (-8,) * MAX_CAPTURES,
    "neutral": (0,) * MAX_CAPTURES,
    "reversal": (8, 8, 8, -8, -8, -8, -8, -8),
    "recovery": (8, -8, -8, -8, 8, 8, 8, 8),
}


class LabRefusal(ValueError):
    """Refuse unsafe, inconsistent or terminal local lab operations."""


def _json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _visible(inventory: int, resources: int) -> tuple[str, ...]:
    affordances = [DRINK]
    if resources:
        affordances.append(COLLECT)
    if inventory:
        affordances.append(EAT)
    return tuple(sorted(affordances))


class _ObservationPort:
    def __init__(self, life_ref: str):
        self.life_ref = life_ref
        self.expected_digest: str | None = None

    def verify(self, *, life_ref: str, claim: ObservationClaim, digest: str) -> bool:
        return life_ref == self.life_ref and digest == self.expected_digest == claim.digest()


class _CurrentPort:
    def __init__(self):
        self.capture_ref: str | None = None

    def verify_current(self, *, life_ref: str, frame: object, advice: object) -> bool:
        # Synthetic freshness check, NOT M11 or an independent living witness.
        return frame.capture_ref == self.capture_ref and frame.life_ref == life_ref


class _SafetyPort:
    def __init__(self):
        self.veto = False

    def check(self, *, life_ref: str, frame: object, candidate_ref: str,
              control_receipt_ref: str) -> SafetyFinding:
        return SafetyFinding(life_ref, frame.frame_ref, frame.capture_ref,
                             candidate_ref, control_receipt_ref, self.veto,
                             "source:g1-lab-local-veto")


class _TerminalPort:
    def verify_terminal(self, **kwargs: object) -> bool:
        return True  # local fixture test double, NEVER an authentic terminal seal


class _UnusedValuation:
    def evaluate_batch(self, **kwargs: object) -> tuple:
        raise LabRefusal("lab valuation source not yet configured")


class _StoredResultSource:
    """Verifies prior chosen results against committed rows of THIS SQLite owner."""

    def __init__(self, results: tuple[ObservedChosenResult, ...]):
        self.known = frozenset(results)

    def verify_chosen_result(self, *, result: ObservedChosenResult) -> bool:
        return result in self.known


@dataclass(frozen=True)
class LabStep:
    index: int
    capture_step: int
    visible: tuple[str, ...]
    chosen: str | None
    control_status: str | None
    result_net: int
    energy: int
    inventory: int
    resources: int
    terminal: bool
    uc_spent: int
    uc_remaining: int
    motor_authority: str = "NONE"


class IntegratedLab:
    """One-file, one-transaction G1-LAB owner, only for disposable experiments.

    The v5 cognition engine runs the same paid Competition/Action Control
    mechanism as the existing G2 fixture. A private *in-transaction* callback
    applies at most one internal body action (or an abstention). Neither the
    cognitive advice nor this callback confers motor rights outside the lab.
    """

    def __init__(self, path: Path, *, life_ref: str, genesis_ref: str):
        self.path = Path(path)
        self.life_ref = life_ref
        self.genesis_ref = genesis_ref
        self.observation_source = _ObservationPort(life_ref)
        self.current_source = _CurrentPort()
        self.safety_source = _SafetyPort()
        self.terminal_source = _TerminalPort()

    @classmethod
    def create(cls, path: Path, *, life_ref: str, genesis_ref: str,
               learning: bool, deltas: tuple[int, ...],
               initial_uc: int = 60, initial_energy: int = 24,
               resources: int = 12) -> IntegratedLab:
        if (type(learning) is not bool or type(deltas) is not tuple or
                not 1 <= len(deltas) <= MAX_CAPTURES or
                any(type(x) is not int or not -8 <= x <= 8 for x in deltas) or
                type(initial_uc) is not int or not 1 <= initial_uc <= 1000000 or
                type(initial_energy) is not int or not 1 <= initial_energy <= 100 or
                type(resources) is not int or not 0 <= resources <= 100):
            raise LabRefusal("invalid bounded G1-LAB protocol")
        lab = cls(path, life_ref=life_ref, genesis_ref=genesis_ref)
        CognitiveCycleFixture.create(
            path=lab.path, life_ref=life_ref, synthetic_uc=initial_uc,
            observation_source=lab.observation_source,
            valuation_source=_UnusedValuation(),
            current_source=lab.current_source,
            safety_source=lab.safety_source,
            genesis_ref=genesis_ref,
            terminal_source=lab.terminal_source,
        )
        with lab._connect() as db:
            db.executescript("""
                CREATE TABLE g1_lab_meta (
                    id INTEGER PRIMARY KEY CHECK(id=1),
                    life_ref TEXT NOT NULL, genesis_ref TEXT NOT NULL,
                    learning INTEGER NOT NULL, deltas_json TEXT NOT NULL,
                    initial_energy INTEGER NOT NULL, initial_resources INTEGER NOT NULL);
                CREATE TABLE g1_lab_state (
                    id INTEGER PRIMARY KEY CHECK(id=1),
                    revision INTEGER NOT NULL, energy INTEGER NOT NULL,
                    inventory INTEGER NOT NULL, resources INTEGER NOT NULL,
                    terminal INTEGER NOT NULL);
                CREATE TABLE g1_lab_steps (
                    seq INTEGER PRIMARY KEY,
                    capture_ref TEXT NOT NULL UNIQUE, capture_step INTEGER NOT NULL UNIQUE,
                    offered_json TEXT NOT NULL, action_ref TEXT,
                    control_status TEXT, observed_step INTEGER NOT NULL,
                    net INTEGER NOT NULL, before_energy INTEGER NOT NULL,
                    energy INTEGER NOT NULL, inventory INTEGER NOT NULL,
                    resources INTEGER NOT NULL, terminal INTEGER NOT NULL,
                    uc_remaining INTEGER NOT NULL, cognition_head TEXT NOT NULL UNIQUE);
            """)
            db.execute("INSERT INTO g1_lab_meta VALUES(1,?,?,?,?,?,?)", (
                life_ref, genesis_ref, int(learning), _json(deltas),
                initial_energy, resources))
            db.execute("INSERT INTO g1_lab_state VALUES(1,0,?,0,?,0)",
                       (initial_energy, resources))
        lab.audit()
        return lab

    @classmethod
    def reopen(cls, path: Path, *, life_ref: str,
               genesis_ref: str) -> IntegratedLab:
        lab = cls(path, life_ref=life_ref, genesis_ref=genesis_ref)
        lab.audit()
        return lab

    def _connect(self) -> sqlite3.Connection:
        if self.path.is_symlink() or not self.path.is_file():
            raise LabRefusal("absent or linked local lab owner")
        db = sqlite3.connect(self.path)
        db.execute("PRAGMA busy_timeout=5000")
        db.execute("PRAGMA synchronous=FULL")
        return db

    def _read(self) -> tuple[dict, tuple, tuple[dict, ...]]:
        with self._connect() as db:
            meta = db.execute("SELECT life_ref,genesis_ref,learning,deltas_json,"
                              "initial_energy,initial_resources FROM g1_lab_meta WHERE id=1").fetchone()
            state = db.execute("SELECT revision,energy,inventory,resources,terminal "
                               "FROM g1_lab_state WHERE id=1").fetchone()
            rows = db.execute("SELECT seq,capture_ref,capture_step,offered_json,action_ref,"
                              "control_status,observed_step,net,before_energy,energy,inventory,"
                              "resources,terminal,uc_remaining,cognition_head "
                              "FROM g1_lab_steps ORDER BY seq").fetchall()
            if meta is None or meta[:2] != (self.life_ref, self.genesis_ref) or state is None:
                raise LabRefusal("foreign or incomplete lab owner")
            raw = ("seq", "capture_ref", "capture_step", "offered_json", "action_ref",
                   "control_status", "observed_step", "net", "before_energy",
                   "energy", "inventory", "resources", "terminal", "uc_remaining",
                   "cognition_head")
            return ({"learning": bool(meta[2]), "deltas": tuple(json.loads(meta[3])),
                     "initial_energy": meta[4], "initial_resources": meta[5]},
                    state, tuple(dict(zip(raw, row)) for row in rows))

    def _fixture(self, valuation: object) -> CognitiveCycleFixture:
        return CognitiveCycleFixture.reopen(
            path=self.path, life_ref=self.life_ref,
            observation_source=self.observation_source,
            valuation_source=valuation, current_source=self.current_source,
            safety_source=self.safety_source,
            genesis_ref=self.genesis_ref, terminal_source=self.terminal_source,
        )

    def _verify_causal_history(
        self, *, meta: dict, records: tuple[dict, ...],
        cognitive_events: tuple[tuple, ...], capacity: int,
    ) -> None:
        """Replay every local body and past-only choice, not just the last row.

        An event-head reference is one-way: the v5 cognitive hash does NOT
        cryptographically commit the body rows. Replaying them detects
        inconsistent laboratory traces, NOT independently authenticated M11.
        """
        from i2.modules.chosen_outcome_study import observed_chosen_scores

        energy, inventory, resources = (
            meta["initial_energy"], 0, meta["initial_resources"],
        )
        uc_remaining = capacity
        seen_terminal = False
        past: list[ObservedChosenResult] = []
        for index, (record, saved) in enumerate(zip(records, cognitive_events)):
            seq = index + 1
            if seen_terminal or record["seq"] != seq or saved[0] != seq:
                raise LabRefusal("lab history crossed terminal or skipped a revision")
            if type(energy) is not int or type(inventory) is not int or type(resources) is not int:
                raise LabRefusal("invalid replayed body fields")
            offered = _visible(inventory, resources)
            capture_step = FIRST_STEP + STEP_GAP * index
            capture_ref = f"capture:lab:{index}"
            # Evidence must be issued only for PREVIOUS committed chosen actions.
            evidence = tuple(sorted(
                [f"evidence:lab:{index}"] +
                [r.evidence_ref for r in past]
            ))
            claim = ObservationClaim(
                self.life_ref,
                FirstPersonCapture(capture_step, capture_ref, "goal:food", offered),
                f"source:lab:past:{index}", evidence,
            )
            event = json.loads(saved[3])
            if (record["capture_ref"] != capture_ref or
                    record["capture_step"] != capture_step or
                    record["offered_json"] != _json(offered) or
                    record["observed_step"] != capture_step + 1 or
                    record["before_energy"] != energy or
                    saved[1] != capture_ref or
                    event["claim_digest"] != claim.digest() or
                    event["claim"]["source_event_ref"] != claim.source_event_ref or
                    tuple(event["claim"]["subjective_evidence_refs"]) != evidence or
                    event["claim"]["capture"]["accessible_semantics"] != list(offered)):
                raise LabRefusal("lab capture or subjective history contradicts body")
            frame, review = event["frame"], event["control_review"]
            status = None if review is None else review["status"]
            if status != record["control_status"]:
                raise LabRefusal("lab safety review status not replayable")
            chosen = None
            if status == "REVIEWED_NOT_ADMITTED":
                if frame is None or review is None:
                    raise LabRefusal("missing paid frame for lab action")
                ref = review["suggested_candidate_ref"]
                candidates = [c["semantic_ref"] for c in frame["candidates"]
                              if c["candidate_ref"] == ref]
                if len(candidates) != 1 or candidates[0] not in offered:
                    raise LabRefusal("lab action was not the reviewed candidate")
                chosen = candidates[0]
            elif review is not None and review["suggested_candidate_ref"] is not None:
                raise LabRefusal("veto or abstention applied action")
            if record["action_ref"] != chosen:
                raise LabRefusal("lab action differs from paid cognitive advice")
            if frame is not None:
                previous = tuple(past) if meta["learning"] else ()
                scores = observed_chosen_scores(
                    claim=claim, results=previous,
                    source=_StoredResultSource(tuple(past)), priors=PRIORS,
                )
                values = event["advice"]["values"]
                by_candidate = {c["candidate_ref"]: c["semantic_ref"]
                                for c in frame["candidates"]}
                if (len(values) != len(by_candidate) or
                        any(v["candidate_ref"] not in by_candidate or
                            v["value"] != scores[by_candidate[v["candidate_ref"]]]
                            for v in values)):
                    raise LabRefusal("lab score uses absent or altered chosen outcome")
            before = energy
            physical_net = -1  # passive metabolism on abstention
            if chosen == COLLECT:
                if resources <= 0:
                    raise LabRefusal("lab collected absent resource")
                resources -= 1
                inventory += 1
                physical_net = -2
            elif chosen == EAT:
                if inventory <= 0:
                    raise LabRefusal("lab ate absent inventory")
                inventory -= 1
                physical_net = meta["deltas"][index] - 2
            elif chosen == DRINK:
                physical_net = -2
            energy = min(100, max(0, energy + physical_net))
            seen_terminal = energy == 0
            uc_remaining -= (event["intake_uc"] +
                             event["competition_uc"] + event["control_uc"])
            if (record["net"] != energy - before or
                    record["energy"] != energy or
                    record["inventory"] != inventory or
                    record["resources"] != resources or
                    record["terminal"] != int(seen_terminal) or
                    record["uc_remaining"] != uc_remaining):
                raise LabRefusal("lab effect or paid UC history cannot replay")
            if chosen is not None:
                past.append(ObservedChosenResult(
                    self.life_ref, capture_ref, chosen, capture_step + 1,
                    f"evidence:lab:result:{seq}", record["net"],
                ))

    def audit(self) -> dict:
        """Cross-check local lab and cognitive journal. NOT remote attestation."""
        meta, state, records = self._read()
        fixture = self._fixture(_UnusedValuation())
        cognitive = fixture.audit()
        if (len(records) != state[0] or cognitive["committed"] != state[0] or
                len(records) > len(meta["deltas"]) or
                cognitive["synthetic_terminal"] or
                cognitive["motor_authority"] != "NONE"):
            raise LabRefusal("cognitive and body revisions diverge")
        with self._connect() as db:
            stored = tuple(db.execute(
                "SELECT seq,capture_ref,event_hash,event_json FROM events ORDER BY seq"
            ).fetchall())
        if (len(stored) != len(records) or
                any((row["seq"], row["capture_ref"], row["cognition_head"]) != stored[i][:3]
                    for i, row in enumerate(records))):
            raise LabRefusal("lab transition not bound to paid cognition")
        if records:
            final = records[-1]
            if (final["energy"], final["inventory"], final["resources"], final["terminal"]) != state[1:]:
                raise LabRefusal("body head diverges from transition")
            if final["uc_remaining"] != cognitive["remaining_synthetic_uc"]:
                raise LabRefusal("synthetic UC head diverges")
        else:
            if state != (0, meta["initial_energy"], 0, meta["initial_resources"], 0):
                raise LabRefusal("noncanonical lab genesis")
        with self._connect() as db:
            capacity = db.execute("SELECT capacity FROM identity WHERE id=1").fetchone()[0]
        self._verify_causal_history(
            meta=meta, records=records, cognitive_events=stored, capacity=capacity,
        )
        return {"cognition": cognitive, "revision": state[0], "energy": state[1],
                "inventory": state[2], "resources": state[3],
                "terminal": bool(state[4]), "learning": meta["learning"],
                "actual_synthetic_uc_spent": capacity - cognitive["remaining_synthetic_uc"],
                "motor_authority": "NONE", "m11_authenticated": False,
                "birth_authorized": False}

    def _inside_transaction(self, *, conn: sqlite3.Connection, seq: int,
                            claim: ObservationClaim, frame: dict | None,
                            control_review: dict | None, remaining_uc: int,
                            event_head: str) -> None:
        # Called by the existing v5 cognition owner just BEFORE its COMMIT.
        # No other executor, database, process or motor authority is involved.
        if not conn.in_transaction:
            raise LabRefusal("lab effect requires cognitive transaction")
        meta = conn.execute("SELECT deltas_json FROM g1_lab_meta WHERE id=1").fetchone()
        state = conn.execute("SELECT revision,energy,inventory,resources,terminal "
                             "FROM g1_lab_state WHERE id=1").fetchone()
        if meta is None or state is None or state[0] + 1 != seq or state[4]:
            raise LabRefusal("stale, terminal or uninitialized lab step")
        deltas = tuple(json.loads(meta[0]))
        if seq > len(deltas):
            raise LabRefusal("outside bounded lab protocol")
        expected = _visible(state[2], state[3])
        if (claim.capture.ref != f"capture:lab:{seq-1}" or
                claim.capture.step != FIRST_STEP + STEP_GAP * (seq-1) or
                claim.capture.accessible_semantics != expected):
            raise LabRefusal("subjective affordances do not match current body")
        chosen = None
        status = None if control_review is None else control_review["status"]
        if control_review is not None:
            if control_review["motor_authority"] != "NONE":
                raise LabRefusal("living motor capability forbidden")
            candidate = control_review["suggested_candidate_ref"]
            if status == "REVIEWED_NOT_ADMITTED":
                if frame is None or candidate is None:
                    raise LabRefusal("unbound local advisory candidate")
                matches = [x["semantic_ref"] for x in frame["candidates"]
                           if x["candidate_ref"] == candidate]
                if len(matches) != 1 or matches[0] not in expected:
                    raise LabRefusal("foreign or unavailable lab action")
                chosen = matches[0]
            elif candidate is not None:
                raise LabRefusal("veto/abstention cannot apply an action")
        energy, inventory, resources = state[1:4]
        raw_net = -1  # abstention still incurs a modeled metabolic tick
        if chosen == COLLECT:
            if resources <= 0:
                raise LabRefusal("collect without resource")
            resources -= 1
            inventory += 1
            raw_net = -2
        elif chosen == EAT:
            if inventory <= 0:
                raise LabRefusal("eat without inventory")
            inventory -= 1
            raw_net = deltas[seq-1] - 2
        elif chosen == DRINK:
            raw_net = -2
        energy_next = min(100, max(0, energy + raw_net))
        net = energy_next - energy
        terminal = int(energy_next == 0)
        conn.execute("UPDATE g1_lab_state SET revision=?,energy=?,inventory=?,"
                     "resources=?,terminal=? WHERE id=1",
                     (seq, energy_next, inventory, resources, terminal))
        conn.execute("INSERT INTO g1_lab_steps VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
            seq, claim.capture.ref, claim.capture.step, _json(expected), chosen, status,
            claim.capture.step+1, net, energy, energy_next, inventory, resources,
            terminal, remaining_uc, event_head))

    def step(self, *, veto: bool = False, fault: str | None = None) -> LabStep:
        if type(veto) is not bool:
            raise LabRefusal("invalid local safety decision")
        snapshot = self.audit()
        meta, state, rows = self._read()
        if state[4] or state[0] >= len(meta["deltas"]):
            raise LabRefusal("terminal or completed lab protocol")
        index = state[0]
        offered = _visible(state[2], state[3])
        at = FIRST_STEP + STEP_GAP * index
        claim = ObservationClaim(
            self.life_ref,
            FirstPersonCapture(at, f"capture:lab:{index}", "goal:food", offered),
            f"source:lab:past:{index}", tuple(sorted(
                [f"evidence:lab:{index}"] +
                [f"evidence:lab:result:{row['seq']}" for row in rows
                 if row["action_ref"] is not None])),
        )
        self.observation_source.expected_digest = claim.digest()
        self.current_source.capture_ref = claim.capture.ref
        self.safety_source.veto = veto
        # Read ONLY previously committed chosen results. No hidden regime,
        # unchosen counterfactual or consequence of the action about to occur.
        history = tuple(ObservedChosenResult(
            self.life_ref, row["capture_ref"], row["action_ref"],
            row["observed_step"], f"evidence:lab:result:{row['seq']}", row["net"])
            for row in rows if row["action_ref"] is not None)
        valuation = ChosenOutcomeValuationStudy(
            claim=claim, results=history if meta["learning"] else (),
            source=_StoredResultSource(history), priors=PRIORS,
        )
        fixture = self._fixture(valuation)
        if index == 0:
            receipt = fixture.open(
                claim=claim, semantic_ref=COLLECT,
                evidence_ref=f"evidence:lab:{index}", ttl_steps=64,
                _fault_at=fault, _g1_lab_hook=self._inside_transaction,
            )
        else:
            receipt = fixture.observe(
                claim=claim, _fault_at=fault,
                _g1_lab_hook=self._inside_transaction,
            )
        if receipt.motor_authority != "NONE":
            raise LabRefusal("model may never issue motor authority")
        post = self.audit()
        if post["revision"] != index + 1:
            raise LabRefusal("missing atomic lab transition")
        _, _, new_rows = self._read()
        record = new_rows[-1]
        return LabStep(
            index=index, capture_step=at, visible=offered,
            chosen=record["action_ref"], control_status=record["control_status"],
            result_net=record["net"], energy=record["energy"],
            inventory=record["inventory"], resources=record["resources"],
            terminal=bool(record["terminal"]),
            uc_spent=receipt.intake_uc+receipt.competition_uc+receipt.control_uc,
            uc_remaining=record["uc_remaining"],
        )


def run_pair(deltas: tuple[int, ...], *, initial_energy: int = 24,
             initial_uc: int = 60) -> dict:
    """Independently seeded, equal-initial-budget learning/ablated comparison."""
    outcomes = {}
    with tempfile.TemporaryDirectory(prefix="i2-g1lab-disposable-") as tmp:
        for learning in (False, True):
            label = "observational" if learning else "fixed"
            db = Path(tmp) / f"{label}.sqlite"
            lab = IntegratedLab.create(
                db, life_ref=f"lab-life:{label}",
                genesis_ref=f"lab-genesis:{label}", learning=learning,
                deltas=deltas, initial_energy=initial_energy,
                initial_uc=initial_uc,
            )
            steps = []
            for _ in deltas:
                try:
                    step = lab.step()
                except LabRefusal as error:
                    steps.append({"refusal": str(error)})
                    break
                steps.append(asdict(step))
                if step.terminal:
                    break
            outcomes[label] = {
                "steps": steps,
                "net_energy_change": sum(r.get("result_net", 0) for r in steps),
                "actions": [r.get("chosen") for r in steps if "chosen" in r],
                "spent_synthetic_uc": sum(r.get("uc_spent", 0) for r in steps),
                "terminal": lab.audit()["terminal"],
            }
    return {"status": "G1_LAB_ONLY_NOT_BORN", "motor_authority": "NONE",
            "m11_authenticated": False, "same_initial_uc": initial_uc,
            "same_initial_energy": initial_energy, "arms": outcomes}


def main() -> None:
    parser = argparse.ArgumentParser(description="Disposable, non-living I2 G1-LAB")
    parser.add_argument("--scenario", choices=tuple(REGIMES) + ("all",),
                        default="all")
    args = parser.parse_args()
    names = tuple(REGIMES) if args.scenario == "all" else (args.scenario,)
    results = {name: run_pair(REGIMES[name]) for name in names}
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()