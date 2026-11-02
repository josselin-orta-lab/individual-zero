"""Bounded I2-native first-person -> paid choice -> committed body loop.

Uses the EXISTING v5 CognitiveCycleFixture transaction and SQLite file.
No second cognition, WorldBody, UC or motor owner. Distinct research genesis
does not migrate, run or relabel the earlier energy-only I2 experiment.
Neither this model nor its local cold audit is independent M11 custody.
"""
from __future__ import annotations

from dataclasses import replace
from math import isclose
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
from uuid import uuid4

from i2.modules.cognitive_cycle_fixture import (
    CognitiveCycleFixture, CommitAcknowledgmentLost,
)
from i2.modules.action_control_boundary import SafetyFinding
from i2.modules.chosen_outcome_study import (
    ChosenOutcomeValuationStudy, ObservedChosenResult, observed_chosen_scores,
)
from i2.modules.intention_continuity import FirstPersonCapture
from i2.modules.intention_ingress import ObservationClaim
from i2.modules.native_body_contract import Body
from i2.modules.native_birth_temperament import BirthTemperament
from i2.modules.native_consequence_bridge import admitted_consequence
from i2.modules.native_owner_support import (
    NativeCaptureReflex, _json, current_evidence, native_scores,
    saved_body, saved_traits,
)
from i2.modules.native_physiological_needs import assess_needs
from i2.runtime.native_physiology_journal import (
    initialize_native_body, native_snapshot, commit_admitted_physics,
    audit_native_body, commit_unadmitted_tick, passive_body_tick, NO_ACTION,
)

PRIORS = {"boire": 1, "manger": 4, "dormir": 2, "attendre": 1}
HORIZON = 8
GENESIS_SCHEMA = "i2-native-paid-local-life-v1"


class NativeRefusal(ValueError):
    pass


class _Observation:
    def __init__(self, life):
        self.life = life
        self.expected = None

    def verify(self, *, life_ref, claim, digest):
        return (life_ref == self.life and
                self.expected == digest == claim.digest())


class _Current:
    def __init__(self):
        self.ref = None

    def verify_current(self, *, life_ref, frame, advice):
        return frame.life_ref == life_ref and frame.capture_ref == self.ref


class _Safety:
    def __init__(self):
        self.reflex = None
        self.veto = False

    def check(self, *, life_ref, frame, candidate_ref, control_receipt_ref):
        reflex = self.reflex
        if (reflex is None or life_ref != reflex.claim.life_ref or
                frame.claim_digest != reflex.claim.digest() or
                frame.capture_ref != reflex.claim.capture.ref or
                not any(c.candidate_ref == candidate_ref
                        for c in frame.candidates)):
            raise NativeRefusal("native safety lacks fresh body-bound reflex")
        return SafetyFinding(
            life_ref, frame.frame_ref, frame.capture_ref,
            candidate_ref, control_receipt_ref, self.veto,
            reflex.evidence_ref)


class _Terminal:
    def verify_terminal(self, **kwargs):
        return False


class _NoEvaluation:
    def evaluate_batch(self, **kwargs):
        raise NativeRefusal("cold native audit may not evaluate an action")


class _HistorySource:
    def __init__(self, results):
        self.known = frozenset(results)

    def verify_chosen_result(self, *, result):
        return result in self.known


def innate_adjustment(values, body, traits):
    scores = native_scores(
        values, body, traits, collect="collecter",
        eat="manger", drink="boire")
    needs = assess_needs(body, traits)
    scores["dormir"] += round(8 * needs.pressures["energy"] +
                            4 * needs.pressures["integrity"])
    return scores


class _Valuation(ChosenOutcomeValuationStudy):
    def __init__(self, *, body, traits, **kwargs):
        super().__init__(**kwargs)
        self.body, self.traits = body, traits

    def evaluate_batch(self, *, frame, receipts):
        evaluated = super().evaluate_batch(frame=frame, receipts=receipts)
        named = {c.candidate_ref: c.semantic_ref for c in frame.candidates}
        original = {named[v.candidate_ref]: v.value for v in evaluated}
        updated = innate_adjustment(original, self.body, self.traits)
        return tuple(replace(
            v, value=updated[named[v.candidate_ref]],
            evidence_ref=v.evidence_ref + ":native-body") for v in evaluated)


def genesis_digest(meta):
    return sha256(_json([GENESIS_SCHEMA, meta["life_ref"],
        meta["genesis_ref"], meta["body_json"], meta["traits_json"],
        meta["food_stock"], meta["water_stock"], meta["learning"],
        meta["berry_food_gain"], meta["berry_integrity_delta"],
        meta["drink_water_gain"]]).encode("ascii")).hexdigest()


class NativePaidI2:
    """One local SQLite file per research individual, no independent M11."""

    def __init__(self, path, life, genesis, *, inspection_only=False):
        self.path = Path(path)
        self.life_ref, self.genesis_ref = life, genesis
        self.inspection_only = inspection_only
        self.halted = False
        self.observation = _Observation(life)
        self.current = _Current()
        self.safety = _Safety()

    def _connect(self):
        if self.path.is_symlink() or not self.path.is_file():
            raise NativeRefusal("no native research identity file")
        return sqlite3.connect(self.path.resolve().as_uri() + "?mode=rw",
                               uri=True, timeout=5)

    def _fixture(self, evaluator):
        return CognitiveCycleFixture.reopen(
            path=self.path, life_ref=self.life_ref,
            observation_source=self.observation,
            valuation_source=evaluator, current_source=self.current,
            safety_source=self.safety, genesis_ref=self.genesis_ref,
            terminal_source=_Terminal())

    @classmethod
    def create(cls, path, *, body: Body, temperament: BirthTemperament,
               learning=True, food_stock=4, water_stock=4, uc=80,
               berry_food_gain=20.0, berry_integrity_delta=-8.0,
               drink_water_gain=25.0):
        if (type(body) is not Body or
                type(temperament) is not BirthTemperament or
                min(body.food, body.water, body.integrity) <= 0 or
                type(learning) is not bool or
                type(food_stock) is not int or not 0 <= food_stock <= 8 or
                type(water_stock) is not int or not 0 <= water_stock <= 8 or
                type(uc) is not int or not 0 <= uc <= 1000):
            raise NativeRefusal("invalid independent bounded native birth")
        from i2.modules.native_body_contract import transition
        transition(body, "manger", berry_food_gain=berry_food_gain,
                   berry_integrity_delta=berry_integrity_delta)
        transition(body, "boire", drink_water_gain=drink_water_gain)
        key = uuid4().hex
        obj = cls(path, "i2:prototype:native:" + key,
                  "genesis:i2:native:" + key)
        CognitiveCycleFixture.create(
            path=obj.path, life_ref=obj.life_ref, synthetic_uc=uc,
            observation_source=obj.observation,
            valuation_source=_NoEvaluation(), current_source=obj.current,
            safety_source=obj.safety, genesis_ref=obj.genesis_ref,
            terminal_source=_Terminal())
        with obj._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            initialize_native_body(db, body=body, traits=temperament)
            db.execute("""CREATE TABLE native_genesis (
                id INTEGER PRIMARY KEY CHECK(id=1),
                life_ref TEXT NOT NULL, genesis_ref TEXT NOT NULL,
                body_json TEXT NOT NULL, traits_json TEXT NOT NULL,
                food_stock INTEGER NOT NULL, water_stock INTEGER NOT NULL,
                learning INTEGER NOT NULL, berry_food_gain REAL NOT NULL,
                berry_integrity_delta REAL NOT NULL,
                drink_water_gain REAL NOT NULL, digest TEXT NOT NULL)""")
            meta = dict(life_ref=obj.life_ref, genesis_ref=obj.genesis_ref,
                        body_json=_json(body.as_dict()),
                        traits_json=_json(temperament.as_dict()),
                        food_stock=food_stock, water_stock=water_stock,
                        learning=int(learning), berry_food_gain=berry_food_gain,
                        berry_integrity_delta=berry_integrity_delta,
                        drink_water_gain=drink_water_gain)
            db.execute("INSERT INTO native_genesis VALUES(1,?,?,?,?,?,?,?,?,?,?,?)",
                       (*meta.values(), genesis_digest(meta)))
            db.commit()
        obj.audit()
        return obj

    @classmethod
    def inspect(cls, path):
        """Cold audit only; never reopens native action authority."""
        path = Path(path)
        if path.is_symlink() or not path.is_file():
            raise NativeRefusal("native identity missing or symlinked")
        with sqlite3.connect(path.resolve().as_uri() + "?mode=ro",
                             uri=True) as db:
            row = db.execute(
                "SELECT life_ref,genesis_ref FROM native_genesis "
                "WHERE id=1").fetchone()
        if row is None:
            raise NativeRefusal("incomplete native birth")
        obj = cls(path, row[0], row[1], inspection_only=True)
        obj.audit()
        return obj

    def _meta(self, conn):
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM native_genesis WHERE id=1").fetchone()
        if row is None:
            raise NativeRefusal("missing native genesis")
        meta = dict(row)
        if ((meta["life_ref"], meta["genesis_ref"]) !=
                (self.life_ref, self.genesis_ref) or
                meta["digest"] != genesis_digest(meta)):
            raise NativeRefusal("foreign or mutated native genesis")
        return meta

    def _rows(self, conn):
        return tuple(conn.execute(
            "SELECT e.seq, e.capture_ref, p.admitted_action, "
            "p.net_physiological_relief FROM native_physical_events p "
            "JOIN events e ON e.seq=p.seq ORDER BY p.seq"))

    def _claim(self, snapshot, meta, rows):
        seq = len(rows)
        if seq != snapshot["revision"]:
            raise NativeRefusal("native observation crossed revisions")
        chosen = [r[2] for r in rows]
        offered = ["dormir", "attendre"]
        if chosen.count("manger") < meta["food_stock"]:
            offered.append("manger")
        if chosen.count("boire") < meta["water_stock"]:
            offered.append("boire")
        evidence = list(snapshot["current_evidence"])
        evidence.extend("evidence:i2:native:outcome:" + str(r[0])
                        for r in rows if r[2] != NO_ACTION)
        return ObservationClaim(
            self.life_ref, FirstPersonCapture(
                10 + 8 * seq, "capture:i2:native:" + str(seq),
                "goal:physical-needs", tuple(sorted(offered))),
            "source:i2:native:committed:" + str(seq),
            tuple(sorted(evidence)))

    def _history(self, rows):
        return tuple(ObservedChosenResult(
            self.life_ref, capture, action,
            11 + 8 * (seq - 1),
            "evidence:i2:native:outcome:" + str(seq),
            int(round(20 * relief)))
            for seq, capture, action, relief in rows if action != NO_ACTION)

    def _apply(self, *, conn, seq, claim, frame, control_review,
               remaining_uc, event_head):
        """The sole physical action hook within v5's existing COMMIT."""
        meta = self._meta(conn)
        snapshot = native_snapshot(conn)
        rows = self._rows(conn)
        if claim != self._claim(snapshot, meta, rows):
            raise NativeRefusal("stale native body capture")
        if seq != len(rows) + 1:
            raise NativeRefusal("nonsequential native cognition")
        record = conn.execute(
            "SELECT event_json FROM events WHERE seq=?", (seq,)).fetchone()
        if record is None:
            raise NativeRefusal("no paid cognitive event")
        event = json.loads(record[0])
        if (event["frame"] != frame or
                event["control_review"] != control_review or
                event["claim_digest"] != claim.digest()):
            raise NativeRefusal("unbound native candidate or observation")
        review = event["control_review"]
        if review is None or review["status"] != "REVIEWED_NOT_ADMITTED":
            return commit_unadmitted_tick(conn, cognition_hash=event_head)
        selected = [c["semantic_ref"] for c in event["frame"]["candidates"]
                    if c["candidate_ref"] == review["suggested_candidate_ref"]]
        if len(selected) != 1:
            raise NativeRefusal("ambiguous chosen action")
        action = selected[0]
        admission = "internal:i2:native-admission:" + sha256(
            _json([seq, event_head, action]).encode()).hexdigest()
        if (action not in claim.capture.accessible_semantics or
                (action == "boire" and
                 sum(r[2] == action for r in rows) >= meta["water_stock"]) or
                (action == "manger" and
                 sum(r[2] == action for r in rows) >= meta["food_stock"])):
            raise NativeRefusal("unavailable or depleted native resource")
        effect = {}
        if action == "boire":
            effect["drink_water_gain"] = meta["drink_water_gain"]
        elif action == "manger":
            effect["berry_food_gain"] = meta["berry_food_gain"]
            effect["berry_integrity_delta"] = meta["berry_integrity_delta"]
        result = commit_admitted_physics(
            conn, action=action, admission_ref=admission,
            cognition_hash=event_head, **effect)
        if conn.execute("SELECT remaining_uc FROM account WHERE id=1").fetchone()[0] != remaining_uc:
            raise NativeRefusal("native physiological step lacks paid UC")
        return result

    def audit(self):
        """Replay every native effect from the immutable local genesis.

        The generic journal audit checks its physical hash chain; this
        additional local audit recalculates the actual body and subjective
        values from birth, with only preceding chosen observations. This is
        NOT an independently witnessed M11 or a proof of general learning.
        """
        with self._connect() as db:
            meta = self._meta(db)
            physical = audit_native_body(db)
            snapshot = native_snapshot(db)
            recorded = tuple(db.execute(
                "SELECT seq,capture_ref,event_json,event_hash "
                "FROM events ORDER BY seq"))
            effects = tuple(db.execute(
                "SELECT seq,admitted_action,admission_ref,cognition_hash,"
                "before_json,after_json,net_physiological_relief,terminal "
                "FROM native_physical_events ORDER BY seq"))
            capacity, remaining = db.execute(
                "SELECT capacity,remaining_uc FROM identity JOIN account ON "
                "identity.id=account.id WHERE identity.id=1").fetchone()
        cognition = self._fixture(_NoEvaluation()).audit()
        if (len(recorded) != len(effects) or len(effects) > HORIZON or
                physical["revision"] != len(effects) or
                cognition["committed"] != len(effects) or
                cognition["motor_authority"] != "NONE" or
                cognition["synthetic_terminal"]):
            raise NativeRefusal("native world and paid cognition diverge")

        body = saved_body(meta["body_json"])
        traits = saved_traits(meta["traits_json"])
        if (snapshot["traits"] != traits or
                physical["traits"] != traits.as_dict() or
                min(body.food, body.water, body.integrity) <= 0):
            raise NativeRefusal("mutated native birth traits or terminal genesis")
        previous = []
        total_uc, terminal = 0, False
        for index, (source, effect) in enumerate(zip(recorded, effects)):
            seq, capture, event_json, cognition_hash = source
            (phy_seq, action, admission_ref, linked_head,
             before_json, after_json, saved_relief, saved_terminal) = effect
            if (terminal or seq != index + 1 or phy_seq != seq or
                    linked_head != cognition_hash):
                raise NativeRefusal("post-terminal or unbound native transition")
            claim = self._claim(
                {"revision": index,
                 "current_evidence": current_evidence(body, traits)},
                meta, previous)
            event = json.loads(event_json)
            expected_capture = {
                "step": claim.capture.step, "ref": claim.capture.ref,
                "goal_ref": claim.capture.goal_ref,
                "accessible_semantics": list(
                    claim.capture.accessible_semantics),
                "contradicted_semantics": list(
                    claim.capture.contradicted_semantics)}
            expected_claim = {
                "life_ref": claim.life_ref,
                "source_event_ref": claim.source_event_ref,
                "subjective_evidence_refs": list(
                    claim.subjective_evidence_refs),
                "capture": expected_capture}
            if (capture != claim.capture.ref or
                    event["claim_digest"] != claim.digest() or
                    event["claim"] != expected_claim):
                raise NativeRefusal("first-person body or past evidence forged")

            frame, advice = event["frame"], event["advice"]
            if frame is not None:
                if (advice is None or
                        frame["claim_digest"] != claim.digest() or
                        frame["capture_ref"] != claim.capture.ref):
                    raise NativeRefusal("missing bound paid native frame")
                past = self._history(previous) if meta["learning"] else ()
                priors = observed_chosen_scores(
                    claim=claim, results=past,
                    source=_HistorySource(past), priors=PRIORS)
                scores = innate_adjustment(priors, body, traits)
                candidates = {item["candidate_ref"]: item["semantic_ref"]
                              for item in frame["candidates"]}
                values = advice["values"]
                if (len(candidates) != len(frame["candidates"]) or
                        len(values) != len(candidates) or
                        any(c not in candidates or
                            candidates[c] not in claim.capture.accessible_semantics or
                            value["value"] != scores[candidates[c]] or
                            not value["evidence_ref"].endswith(":native-body")
                            for value in values
                            for c in (value["candidate_ref"],))):
                    raise NativeRefusal("paid score not grounded in born needs or experience")
            elif advice is not None:
                raise NativeRefusal("unpaid native advice")

            review = event["control_review"]
            if review is not None and review["status"] == "REVIEWED_NOT_ADMITTED":
                if frame is None:
                    raise NativeRefusal("native action lacks paid candidates")
                chosen = [item["semantic_ref"] for item in frame["candidates"]
                          if item["candidate_ref"] ==
                          review["suggested_candidate_ref"]]
                safety = event["safety_finding"]
                control = event["control_receipt"]
                if (len(chosen) != 1 or action != chosen[0] or
                        action not in claim.capture.accessible_semantics or
                        safety is None or safety["veto"] is not False or
                        control is None or
                        control["ref"] != review["control_receipt_ref"]):
                    raise NativeRefusal("native physical action lacks fresh admission")
                expected_ref = ("internal:i2:native-admission:" + sha256(
                    _json([seq, cognition_hash, action]).encode()).hexdigest())
                if action == "boire" and sum(
                        prior[2] == action for prior in previous) >= meta["water_stock"]:
                    raise NativeRefusal("native drank unavailable water")
                if action == "manger" and sum(
                        prior[2] == action for prior in previous) >= meta["food_stock"]:
                    raise NativeRefusal("native ate unavailable food")
                changes = {}
                if action == "boire":
                    changes["drink_water_gain"] = meta["drink_water_gain"]
                elif action == "manger":
                    changes["berry_food_gain"] = meta["berry_food_gain"]
                    changes["berry_integrity_delta"] = meta["berry_integrity_delta"]
                outcome = admitted_consequence(
                    before=body, temperament=traits,
                    action=action, admitted=True, applied=True, **changes)
                next_body = outcome.after
                terminal = outcome.terminal
            else:
                if (action != NO_ACTION or
                        (review is not None and (
                            review["status"] == "REVIEWED_NOT_ADMITTED" or
                            review["suggested_candidate_ref"] is not None))):
                    raise NativeRefusal("unadmitted physical time became a motor action")
                expected_ref = "no-motor:i2:physical-time:" + sha256(
                    _json([seq, cognition_hash]).encode()).hexdigest()
                next_body = passive_body_tick(body)
                terminal = min(next_body.food, next_body.water,
                               next_body.integrity) <= 0
            if admission_ref != expected_ref:
                raise NativeRefusal("native motor or no-motor receipt forged")
            before_pressure = assess_needs(body, traits)
            after_pressure = assess_needs(next_body, traits)
            relief = (sum(before_pressure.pressures.values()) -
                      sum(after_pressure.pressures.values()))
            if (before_json != _json(body.as_dict()) or
                    after_json != _json(next_body.as_dict()) or
                    not isclose(saved_relief, relief, rel_tol=0, abs_tol=1e-12) or
                    saved_terminal != int(terminal)):
                raise NativeRefusal("native physiology disagrees with birth replay")
            total_uc += (event["intake_uc"] + event["competition_uc"] +
                         event["control_uc"])
            previous.append((seq, capture, action, relief))
            body = next_body
        if (body != snapshot["body"] or
                body.as_dict() != physical["body"] or
                total_uc != capacity - remaining or
                remaining != cognition["remaining_synthetic_uc"]):
            raise NativeRefusal("native final body or paid UC disagrees with replay")
        return {
            "revision": len(effects), "body": body.as_dict(),
            "temperament": traits.as_dict(), "remaining_uc": remaining,
            "terminal": terminal, "m11_authenticated": False,
            "engine_registered": False, "scientific_verdict": "NOT_ESTABLISHED",
            "native_loop": "PAID_SINGLE_SQLITE_INTERNAL_ONLY",
        }

    def step(self, *, veto=False, fault=None):
        if self.inspection_only or self.halted:
            raise NativeRefusal("halted or cold inspection-only life")
        if type(veto) is not bool:
            raise NativeRefusal("native safety veto must be a boolean")
        before = self.audit()
        if before["terminal"] or before["revision"] >= HORIZON:
            raise NativeRefusal("terminal or bounded native life")
        with self._connect() as db:
            meta = self._meta(db)
            snap = native_snapshot(db)
            rows = self._rows(db)
        claim = self._claim(snap, meta, rows)
        body, traits = snap["body"], snap["traits"]
        self.observation.expected = claim.digest()
        self.current.ref = claim.capture.ref
        self.safety.veto = veto
        self.safety.reflex = NativeCaptureReflex(claim, body, traits)
        # Only previously committed personal results, never a hidden counterfactual.
        outcomes = self._history(rows) if meta["learning"] else ()
        valuation = _Valuation(
            claim=claim, results=outcomes, source=_HistorySource(outcomes),
            priors=PRIORS, body=body, traits=traits)
        fixture = self._fixture(valuation)
        try:
            if not rows:
                choice = ("boire" if "boire" in claim.capture.accessible_semantics
                          else claim.capture.accessible_semantics[0])
                fixture.open(
                    claim=claim, semantic_ref=choice,
                    evidence_ref=current_evidence(body, traits)[0],
                    ttl_steps=64, _fault_at=fault, _g1_lab_hook=self._apply)
            else:
                fixture.observe(
                    claim=claim, _fault_at=fault, _g1_lab_hook=self._apply)
        except CommitAcknowledgmentLost:
            self.halted = True
            raise
        except sqlite3.Error:
            self.halted = True
            raise
        final = self.audit()
        if final["revision"] != before["revision"] + 1:
            self.halted = True
            raise NativeRefusal("native ambiguous physical COMMIT")
        return final
