"""Inert challenge witness integration and terminal minimum propagation."""
from dataclasses import replace
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"src"))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from test_unified_control_cycle import LIFE, ObservationPort, Values, Current, Safety, Terminal
from i2.modules.cognitive_cycle_fixture import CognitiveCycleFixture, ZERO_HASH
from i2.modules.challenge_witness_contract import SignedClaim, TrustPolicy, SCHEMA
from i2.modules.challenge_witness_adapter import ChallengeBoundWitness
from i2.modules.lifecycle_external_witness import LatestWitness, WITNESS_SCHEMA, WitnessRefusal, verify_fixture
from i2.modules.uncertain_witness_inspection import inspect_uncertain_terminal_with_witness

NONCE="a"*64
POLICY=TrustPolicy("authority:lab","key:lab",10,1000)

class Nonces:
    def __init__(self): self.calls=0
    def next_challenge(self):
        self.calls+=1
        return NONCE if self.calls==1 else "b"*64
class Clock:
    def now(self): return 110
class Crypto:
    def __init__(self,valid=True): self.valid=valid
    def verify(self,**kwargs): return self.valid
class Transport:
    def __init__(self,record): self.record=record;self.calls=[]
    def request_latest(self,*,life_ref,genesis_ref,challenge):
        self.calls.append(challenge)
        return SignedClaim(SCHEMA,POLICY.authority_ref,POLICY.key_ref,challenge,100,150,
                           self.record,b"synthetic-verifier-only")

class AdapterTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        self.source=ObservationPort()
        self.ports=dict(path=Path(temp.name)/"v5.sqlite",life_ref=LIFE,
                        genesis_ref="genesis:adapter-v5",
                        observation_source=self.source,valuation_source=Values(),
                        current_source=Current(),safety_source=Safety(),
                        terminal_source=Terminal())
        self.fixture=CognitiveCycleFixture.create(synthetic_uc=20,**self.ports)

    def record(self, report=None):
        report=self.fixture.audit() if report is None else report
        return LatestWitness(WITNESS_SCHEMA,report["life_ref"],report["genesis_ref"],
                             report["schema"],report["committed"],report["last_step"],
                             report["chain_head"],report["terminal_ref"],
                             report["terminal_step"],"proof:mock")

    def adapter(self,record=None,valid=True):
        transport=Transport(self.record() if record is None else record)
        adapter=ChallengeBoundWitness(challenge_source=Nonces(),clock=Clock(),
                                     transport=transport,verifier=Crypto(valid),
                                     policy=POLICY)
        return adapter,transport

    def test_witness_inspection_matches_but_never_authorizes(self):
        adapter,transport=self.adapter()
        inspection=verify_fixture(fixture=self.fixture,witness=adapter)
        self.assertEqual(inspection.status,"MATCHED_OPEN_INSPECTION")
        self.assertEqual(transport.calls,[NONCE])
        self.assertFalse(inspection.resumption_authorized)
        self.assertEqual(inspection.motor_authority,"NONE")

    def test_new_request_uses_new_challenge(self):
        adapter,transport=self.adapter()
        adapter.read_verified_latest(life_ref=LIFE,genesis_ref=self.ports["genesis_ref"])
        adapter.read_verified_latest(life_ref=LIFE,genesis_ref=self.ports["genesis_ref"])
        self.assertEqual(transport.calls,[NONCE,"b"*64])

    def test_unverified_signature_is_unknown_in_audit(self):
        adapter,_=self.adapter(valid=False)
        with self.assertRaises(WitnessRefusal) as failure:
            verify_fixture(fixture=self.fixture,witness=adapter)
        self.assertEqual(failure.exception.reason,"UNKNOWN")

    def test_verified_foreign_life_rejected(self):
        adapter,_=self.adapter(record=replace(self.record(),life_ref="life:other"))
        with self.assertRaises(WitnessRefusal) as failure:
            verify_fixture(fixture=self.fixture,witness=adapter)
        self.assertEqual(failure.exception.reason,"UNKNOWN")

    def test_terminal_minimum_is_not_silently_ignored(self):
        self.fixture.seal_terminal(physical_step=3,terminal_ref="terminal:done",
                                   evidence_ref="evidence:done")
        pinned=self.record()
        adapter,_=self.adapter(record=replace(pinned,committed=0,last_step=-1,
                                               chain_head=ZERO_HASH,
                                               terminal_ref=None,terminal_step=None))
        with self.assertRaises(WitnessRefusal) as failure:
            inspect_uncertain_terminal_with_witness(
                fixture=self.fixture,witness=adapter,
                previous_count=0,previous_head=ZERO_HASH,physical_step=3,
                terminal_ref="terminal:done",evidence_ref="evidence:done",
                minimum_witness=pinned,
            )
        self.assertEqual(failure.exception.reason,"STALE")

    def test_no_nonce_or_replay_protection_claimed(self):
        # A repeated nonce remains a responsibility of the external provider.
        class Reused:
            def next_challenge(self): return NONCE
        transport=Transport(self.record())
        adapter=ChallengeBoundWitness(challenge_source=Reused(),clock=Clock(),
                                      transport=transport,verifier=Crypto(),policy=POLICY)
        adapter.read_verified_latest(life_ref=LIFE,genesis_ref=self.ports["genesis_ref"])
        with self.assertRaisesRegex(ValueError,"duplicate witness challenge"):
            adapter.read_verified_latest(life_ref=LIFE,genesis_ref=self.ports["genesis_ref"])
        self.assertEqual(transport.calls,[NONCE])

    def test_bad_nonce_refused_before_transport(self):
        for nonce in ("bad", "G"*64, True, None, "a"*63):
            class Invalid:
                def next_challenge(self): return nonce
            transport=Transport(self.record())
            adapter=ChallengeBoundWitness(challenge_source=Invalid(),clock=Clock(),
                                          transport=transport,verifier=Crypto(),policy=POLICY)
            with self.subTest(nonce=nonce),self.assertRaises(ValueError):
                adapter.read_verified_latest(life_ref=LIFE,genesis_ref=self.ports["genesis_ref"])
            self.assertEqual(transport.calls,[])

    def test_uncertain_transport_failure_burns_nonce_in_session(self):
        class Same:
            def next_challenge(self): return NONCE
        class Lost(Transport):
            def request_latest(self,**kwargs):
                self.calls.append(kwargs["challenge"])
                raise TimeoutError("lost response")
        transport=Lost(self.record())
        adapter=ChallengeBoundWitness(challenge_source=Same(),clock=Clock(),
                                      transport=transport,verifier=Crypto(),policy=POLICY)
        with self.assertRaises(TimeoutError):
            adapter.read_verified_latest(life_ref=LIFE,genesis_ref=self.ports["genesis_ref"])
        with self.assertRaisesRegex(ValueError,"duplicate witness challenge"):
            adapter.read_verified_latest(life_ref=LIFE,genesis_ref=self.ports["genesis_ref"])
        self.assertEqual(transport.calls,[NONCE])

    def test_concurrent_duplicate_nonce_one_transport_call(self):
        from concurrent.futures import ThreadPoolExecutor
        from threading import Barrier
        class Same:
            def next_challenge(self): return NONCE
        transport=Transport(self.record())
        adapter=ChallengeBoundWitness(challenge_source=Same(),clock=Clock(),
                                      transport=transport,verifier=Crypto(),policy=POLICY)
        barrier=Barrier(3)
        def attempt():
            barrier.wait()
            try:
                adapter.read_verified_latest(life_ref=LIFE,genesis_ref=self.ports["genesis_ref"])
                return "accepted"
            except ValueError:
                return "refused"
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures=[pool.submit(attempt) for _ in range(2)]
            barrier.wait()
            self.assertEqual(sorted(f.result(timeout=5) for f in futures),
                             ["accepted","refused"])
        self.assertEqual(transport.calls,[NONCE])

if __name__=="__main__": unittest.main()
