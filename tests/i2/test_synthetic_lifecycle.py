"""I2 v3 synthetic terminal custody: NOT a birth, physiology, or M11 death."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from dataclasses import fields
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from i2.modules.intention_continuity import FirstPersonCapture  # noqa: E402
from i2.modules.intention_ingress import ObservationClaim  # noqa: E402
from i2.modules.competition_preview import SubjectiveValuation  # noqa: E402
from i2.modules.action_control_boundary import SafetyFinding  # noqa: E402
from i2.modules.cognitive_cycle_fixture import (  # noqa: E402
    CognitiveCycleFixture, SCHEMA,
    SyntheticTerminalReceipt, FaultInjected, CommitAcknowledgmentLost,
    _json, _chain,
)

LIFE = "life:lifecycle-synthetic-1"
GENESIS = "genesis:synthetic-sealed-1"
COLLECT = "affordance:collect:berry_a"
EAT = "affordance:eat:berry_a"
DRINK = "affordance:drink:water"


def make_claim(step, *, life=LIFE):
    return ObservationClaim(
        life, FirstPersonCapture(step, f"capture:{step}", "goal:food",
                                 tuple(sorted((COLLECT, EAT, DRINK)))),
        f"source:{step}", (f"evidence:{step}",),
    )


class Source:
    def __init__(self):
        self.claims = set()
        self.calls = 0

    def add(self, value):
        self.claims.add(value.digest())
        return value

    def verify(self, *, life_ref, claim, digest):
        self.calls += 1
        return life_ref == LIFE and digest in self.claims and digest == claim.digest()


class Values:
    def __init__(self):
        self.calls = 0

    def evaluate_batch(self, *, frame, receipts):
        self.calls += 1
        return tuple(SubjectiveValuation(
            c.candidate_ref, r.ref, f"value:synthetic:{index}",
            5 if c.semantic_ref == EAT else 0,
        ) for index, (c, r) in enumerate(zip(frame.candidates, receipts)))


class Current:
    def __init__(self):
        self.calls = 0

    def verify_current(self, *, life_ref, frame, advice):
        self.calls += 1
        return life_ref == LIFE and frame.capture_ref == advice.capture_ref


class Safety:
    def __init__(self):
        self.calls = 0

    def check(self, *, life_ref, frame, candidate_ref, control_receipt_ref):
        self.calls += 1
        return SafetyFinding(life_ref, frame.frame_ref, frame.capture_ref,
                             candidate_ref, control_receipt_ref, False,
                             "safety:synthetic-veto-clear")


class TerminalSource:
    def __init__(self):
        self.calls = []
        self.answer = True
        self.fail = False

    def verify_terminal(self, *, life_ref, genesis_ref, physical_step,
                        terminal_ref, evidence_ref, previous_head):
        self.calls.append((life_ref, genesis_ref, physical_step, terminal_ref,
                           evidence_ref, previous_head))
        if self.fail:
            raise RuntimeError("mock terminal source unavailable")
        return self.answer


class SyntheticLifecycleTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / "synthetic-v3.sqlite"
        self.src, self.val, self.cur, self.safety, self.term = (
            Source(), Values(), Current(), Safety(), TerminalSource(),
        )

    def args(self, **overrides):
        params = dict(path=self.path, life_ref=LIFE,
                      observation_source=self.src, valuation_source=self.val,
                      current_source=self.cur, safety_source=self.safety,
                      genesis_ref=GENESIS, terminal_source=self.term)
        params.update(overrides)
        return params

    def create(self, capacity=20, **kwargs):
        return CognitiveCycleFixture.create(synthetic_uc=capacity, **self.args(**kwargs))

    def reopened(self, **kwargs):
        return CognitiveCycleFixture.reopen(**self.args(**kwargs))

    def open(self, f, step=3):
        return f.open(claim=self.src.add(make_claim(step)), semantic_ref=COLLECT,
                      evidence_ref=f"evidence:{step}", ttl_steps=12)

    def seal(self, f, *, step=4, ref=None, evidence=None, fault=None):
        return f.seal_terminal(
            physical_step=step, terminal_ref=ref or f"terminal:synthetic:{step}",
            evidence_ref=evidence or f"evidence:terminal:{step}", _fault_at=fault,
        )

    def inspect_table(self, query, params=()):
        with closing(sqlite3.connect(self.path)) as conn, conn:
            return conn.execute(query, params).fetchall()

    def test_genesis_pins_schema_before_any_cycle(self):
        f = self.create()
        a = f.audit()
        self.assertEqual((a["schema"], a["genesis_ref"], a["committed"]),
                         (SCHEMA, GENESIS, 0))
        self.assertIs(a["synthetic_terminal"], False)
        self.assertIs(a["physiological_death_attested"], False)
        self.assertEqual((a["terminal_ref"], a["terminal_step"]), (None, None))
        self.assertIsNone(f.terminal_lookup())
        self.assertEqual(a["motor_authority"], "NONE")

    def test_v3_has_no_birth_dead_recover_or_motor_execution(self):
        f = self.create()
        for forbidden in ("birth", "run_step", "dispatch", "command", "execute",
                          "admit", "admit_motor", "cold_recover", "revive", "resurrect"):
            self.assertFalse(hasattr(f, forbidden), forbidden)
        self.assertFalse({"command", "admission", "world_effect", "birth"} &
                         {item.name for item in fields(SyntheticTerminalReceipt)})

    def test_v3_requires_both_external_control_sources(self):
        for kwargs in ({"current_source": None, "safety_source": None},
                       {"current_source": None}, {"safety_source": None}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.create(**kwargs)
            self.assertFalse(self.path.exists())

    def test_v3_requires_genesis_and_terminal_port_together(self):
        for kwargs in ({"genesis_ref": None}, {"terminal_source": None},
                       {"genesis_ref": " "}, {"genesis_ref": "g" * 257}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.create(**kwargs)
            self.assertFalse(self.path.exists())

    def test_missing_terminal_method_rejected_before_file_creation(self):
        with self.assertRaises(ValueError):
            self.create(terminal_source=object())
        self.assertFalse(self.path.exists())

    def test_no_mode_or_identity_relaxation(self):
        f=self.create()
        for kwargs in (dict(genesis_ref=None,terminal_source=None),
                       dict(genesis_ref="genesis:other"),
                       dict(life_ref="life:other")):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.reopened(**kwargs)
        self.assertIsNone(f.terminal_lookup())

    def test_single_terminal_seal_preserves_uc_owner_and_chain(self):
        f=self.create(); c=self.open(f)
        before=f.audit()
        terminal=self.seal(f)
        after=f.audit()
        self.assertEqual(terminal.seq,2)
        self.assertEqual(terminal.life_ref,LIFE)
        self.assertEqual(terminal.genesis_ref,GENESIS)
        self.assertEqual(terminal.physical_step,4)
        self.assertEqual(terminal.terminal_ref,"terminal:synthetic:4")
        self.assertEqual(terminal.motor_authority,"NONE")
        self.assertEqual(after["remaining_synthetic_uc"],before["remaining_synthetic_uc"])
        self.assertEqual(after["intention"],before["intention"])
        self.assertEqual(after["committed"],2)
        self.assertEqual(after["last_step"],4)
        self.assertEqual(after["chain_head"],terminal.chain_head)
        self.assertTrue(after["synthetic_terminal"])
        self.assertEqual(after["terminal_ref"],terminal.terminal_ref)
        self.assertEqual(f.lookup(capture_ref=c.capture_ref),c)
        self.assertEqual(f.terminal_lookup(),terminal)
        self.assertFalse(after["physiological_death_attested"])

    def test_terminal_before_any_cognition_seals_empty_owner(self):
        f=self.create(capacity=0)
        t=self.seal(f,step=0)
        a=f.audit()
        self.assertEqual((a["committed"],a["remaining_synthetic_uc"]),(1,0))
        self.assertIsNone(a["intention"])
        self.assertEqual(f.terminal_lookup(),t)

    def test_reopened_terminal_only_for_readonly_inspection(self):
        f=self.create(); self.open(f); seal=self.seal(f)
        calls=(self.src.calls,self.val.calls,self.cur.calls,self.safety.calls,len(self.term.calls))
        g=self.reopened()
        self.assertEqual(g.terminal_lookup(),seal)
        self.assertEqual(g.audit(),f.audit())
        self.assertEqual(calls,(self.src.calls,self.val.calls,self.cur.calls,self.safety.calls,len(self.term.calls)))
        with self.assertRaises(ValueError): self.open(g,step=5)

    def test_after_terminal_no_cognitive_cycle_even_if_source_whitelists(self):
        f=self.create(); self.open(f); self.seal(f)
        prior=(self.src.calls,self.val.calls,self.cur.calls,self.safety.calls)
        with self.assertRaises(ValueError): self.open(f,step=5)
        with self.assertRaises(ValueError): f.observe(claim=self.src.add(make_claim(5)))
        self.assertEqual((self.src.calls,self.val.calls,self.cur.calls,self.safety.calls),prior)
        self.assertEqual(f.audit()["committed"],2)

    def test_after_terminal_no_reseal_or_external_port_called(self):
        f=self.create(); first=self.seal(f,step=2)
        calls=len(self.term.calls)
        with self.assertRaises(ValueError): self.seal(f,step=3)
        self.assertEqual(len(self.term.calls),calls)
        self.assertEqual(f.terminal_lookup(),first)

    def test_terminal_requires_later_step_than_last_cognitive(self):
        f=self.create(); self.open(f,step=6)
        for step in (0,3,6):
            with self.subTest(step=step), self.assertRaises(ValueError):
                self.seal(f,step=step)
        self.assertIsNone(f.terminal_lookup())
        self.assertEqual(len(self.term.calls),0)

    def test_invalid_terminal_ref_and_boolean_step_fail_pre_port(self):
        f=self.create()
        inputs=((True,"terminal:x"),(False,"terminal:x"),(-1,"terminal:x"),
                (0,"capture:incorrect"),(0,"terminal:has space"))
        for step,ref in inputs:
            with self.subTest(step=step,ref=ref),self.assertRaises(ValueError):
                self.seal(f,step=step,ref=ref)
        self.assertEqual(self.term.calls,[])
        self.assertFalse(f.audit()["synthetic_terminal"])

    def test_nonboolean_attester_denies_terminal_without_publish(self):
        f=self.create()
        for answer in (0,1,"true",None,False):
            self.term.answer=answer
            with self.subTest(answer=answer),self.assertRaises(ValueError):
                self.seal(f,step=1)
        self.assertEqual(f.audit()["committed"],0)
        self.assertIsNone(f.terminal_lookup())

    def test_attester_exception_cannot_publish_partial_state(self):
        f=self.create();self.term.fail=True
        with self.assertRaises(RuntimeError): self.seal(f,step=1)
        self.assertEqual(f.audit()["committed"],0)
        self.assertEqual(f.audit()["remaining_synthetic_uc"],20)

    def test_terminal_source_bound_to_genesis_and_exact_prior_head(self):
        f=self.create();r=self.open(f)
        self.seal(f)
        call=self.term.calls[-1]
        self.assertEqual(call[:2],(LIFE,GENESIS))
        self.assertEqual(call[5],r.chain_head)

    def test_crash_after_terminal_insert_is_fully_rolled_back(self):
        f=self.create()
        with self.assertRaises(FaultInjected): self.seal(f,step=1,fault="after_insert")
        self.assertEqual(f.audit()["committed"],0)
        self.assertIsNone(f.terminal_lookup())
        self.assertEqual(self.inspect_table("SELECT terminal_ref FROM lifecycle"),[(None,)])

    def test_crash_before_terminal_commit_is_fully_rolled_back(self):
        f=self.create()
        with self.assertRaises(FaultInjected): self.seal(f,step=1,fault="before_commit")
        self.assertEqual(f.audit()["committed"],0)
        self.assertFalse(f.audit()["synthetic_terminal"])

    def test_lost_terminal_ack_resolved_by_readonly_terminal_lookup(self):
        f=self.create();self.open(f)
        with self.assertRaises(CommitAcknowledgmentLost):
            self.seal(f,step=4,fault="after_commit")
        verified=f.terminal_lookup()
        self.assertEqual(verified.seq,2)
        self.assertEqual(f.audit()["committed"],2)
        calls=len(self.term.calls)
        with self.assertRaises(ValueError):self.seal(f,step=5)
        self.assertEqual(len(self.term.calls),calls)

    def test_two_concurrent_seals_only_one_can_commit(self):
        f=self.create()
        g=self.reopened()
        def attempt(instance):
            try: return ("OK",self.seal(instance,step=5))
            except ValueError: return ("DENIED",None)
        with ThreadPoolExecutor(max_workers=2) as executor:
            results=list(executor.map(attempt,(f,g)))
        self.assertCountEqual([x[0] for x in results],["OK","DENIED"])
        self.assertEqual(f.audit()["committed"],1)
        self.assertEqual(f.audit()["terminal_step"],5)

    def test_terminal_does_not_count_as_cognitive_receipt(self):
        f=self.create();self.seal(f,step=0)
        with self.assertRaises(ValueError):f.lookup(capture_ref="terminal:synthetic:0")

    def test_tampered_terminal_marker_rejected(self):
        f=self.create();self.seal(f,step=0)
        with closing(sqlite3.connect(self.path)) as conn, conn:
            conn.execute("UPDATE lifecycle SET terminal_step=10 WHERE id=1")
        with self.assertRaises(ValueError):f.audit()

    def test_tampered_genesis_ref_rejected_by_audit(self):
        f=self.create();self.seal(f,step=0)
        with closing(sqlite3.connect(self.path)) as conn, conn:
            conn.execute("UPDATE lifecycle SET genesis_ref='genesis:alien' WHERE id=1")
        with self.assertRaises(ValueError): f.audit()

    def test_tampered_terminal_event_with_recomputed_chain_but_old_marker_rejected(self):
        f=self.create();self.seal(f,step=0)
        with closing(sqlite3.connect(self.path)) as conn, conn:
            body,prev=conn.execute("SELECT event_json,previous_hash FROM events").fetchone()
            e=json.loads(body);e["evidence_ref"]="evidence:forged"
            altered=_json(e);head=_chain(prev,altered,schema=SCHEMA)
            conn.execute("UPDATE events SET event_json=?,event_hash=?",(altered,head))
            conn.execute("UPDATE account SET chain_head=?",(head,))
        with self.assertRaises(ValueError):f.audit()

    def test_tampered_terminal_source_ref_and_digest_rejected(self):
        f=self.create();self.seal(f,step=0)
        with closing(sqlite3.connect(self.path)) as conn, conn:
            conn.execute("UPDATE events SET capture_ref='terminal:altered'")
            conn.execute("UPDATE lifecycle SET terminal_ref='terminal:altered'")
        with self.assertRaises(ValueError):f.audit()

    def test_event_after_terminal_rejected_even_if_tail_chain_is_rebuilt(self):
        f=self.create();seal=self.seal(f,step=0)
        with closing(sqlite3.connect(self.path)) as conn, conn:
            data=json.loads(conn.execute("SELECT event_json FROM events").fetchone()[0])
            data["seq"]=2
            data["physical_step"]=3
            data["terminal_ref"]="terminal:again"
            body=_json(data); prev=seal.chain_head; head=_chain(prev,body,schema=SCHEMA)
            conn.execute("INSERT INTO events VALUES (?,?,?,?,?,?,?)",
                         (2,3,"terminal:again","a"*64,body,prev,head))
            conn.execute("UPDATE account SET committed=2,last_step=3,chain_head=?",(head,))
        with self.assertRaises(ValueError):f.audit()

    def test_terminal_ref_cannot_be_reused_as_cognitive_capture(self):
        f=self.create()
        from dataclasses import replace
        c=self.src.add(make_claim(3))
        modified=replace(c,capture=replace(c.capture,ref="terminal:synthetic:3"))
        self.src.add(modified)
        with self.assertRaises(ValueError):f.observe(claim=modified)
        self.assertEqual(f.audit()["committed"],0)

    def test_cannot_create_second_identity_on_existing_database(self):
        self.create()
        with self.assertRaises(FileExistsError):self.create()
        self.assertEqual(self.inspect_table("SELECT count(*) FROM identity"),[(1,)])

    def test_terminal_seal_rejects_bad_fault_before_opening_database(self):
        f=self.create()
        with self.assertRaises(ValueError):self.seal(f,step=0,fault="after_magic")
        self.assertEqual(self.term.calls,[])


if __name__ == "__main__":
    unittest.main()
