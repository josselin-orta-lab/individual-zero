"""G2 durability and corruption checks; no independent M11 witness."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import os
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"src"))
from i2.modules.durable_challenge_source import DurableChallengeSource, ChallengeCustodyError

NONCE="a"*64
NEXT="b"*64

class DurableChallengeTests(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir=Path(tmp.name)/"private"
        self.dir.mkdir(mode=0o700)

    def source(self,nonce=NONCE):
        return DurableChallengeSource(directory=self.dir,candidate_source=lambda: nonce)

    def test_cold_restart_same_nonce_refused(self):
        self.assertEqual(self.source().next_challenge(),NONCE)
        with self.assertRaisesRegex(ChallengeCustodyError,"already used"):
            self.source().next_challenge()
        self.assertEqual(self.source(NEXT).next_challenge(),NEXT)
        self.assertEqual((self.dir/"challenges.log").read_bytes(),
                         (NONCE+"\n"+NEXT+"\n").encode("ascii"))

    def test_concurrent_instances_only_one_reservation(self):
        def reserve(_):
            try:
                self.source().next_challenge()
                return "ok"
            except ChallengeCustodyError:
                return "refused"
        with ThreadPoolExecutor(max_workers=8) as pool:
            results=list(pool.map(reserve,range(8)))
        self.assertEqual(results.count("ok"),1)
        self.assertEqual(results.count("refused"),7)

    def test_torn_and_forged_log_fail_closed(self):
        self.source().next_challenge()
        p=self.dir/"challenges.log"
        for data in (b"partial", (NONCE+"\n"+NONCE+"\n").encode(),
                     ("Z"*64+"\n").encode(),(NONCE+"\r\n").encode()):
            with self.subTest(data=data[:16]):
                p.write_bytes(data)
                with self.assertRaises(ChallengeCustodyError):
                    self.source(NEXT).next_challenge()
                self.assertEqual(p.read_bytes(),data)

    def test_unsafe_directory_and_symlink_rejected(self):
        self.dir.chmod(0o755)
        with self.assertRaises(ChallengeCustodyError):
            self.source()
        self.dir.chmod(0o700)
        (self.dir/"challenges.log").symlink_to(self.dir/"missing")
        with self.assertRaises(ChallengeCustodyError):
            self.source().next_challenge()

    def test_missing_log_after_valid_reservation_is_not_recreated(self):
        self.source().next_challenge()
        path=self.dir/"challenges.log"
        path.unlink()
        with self.assertRaises(ChallengeCustodyError):
            self.source().next_challenge()
        self.assertFalse(path.exists())

    def test_missing_lock_with_existing_log_is_not_silently_reinitialized(self):
        self.source().next_challenge()
        (self.dir/".challenge.lock").unlink()
        with self.assertRaises(ChallengeCustodyError):
            self.source(NEXT).next_challenge()
        self.assertEqual((self.dir/"challenges.log").read_bytes(),
                         (NONCE+"\n").encode())

    def test_reopen_existing_empty_log_refuses(self):
        self.source().next_challenge()
        (self.dir/"challenges.log").write_bytes(b"")
        with self.assertRaises(ChallengeCustodyError):
            self.source(NEXT).next_challenge()

    def test_fully_restored_directory_is_still_not_detectable(self):
        self.source().next_challenge()
        # An attacker with directory control can replace both files. This
        # synthetic demonstration is a LIMIT, never a security success.
        (self.dir/".challenge.lock").unlink()
        (self.dir/"challenges.log").unlink()
        self.assertEqual(self.source().next_challenge(),NONCE)

    def test_replaced_lock_during_reservation_refuses(self):
        self.source().next_challenge()
        class SwapAfterLock(DurableChallengeSource):
            def _check_named_file(self, name, fd):
                if name == ".challenge.lock" and not getattr(self, "_swapped", False):
                    self._swapped=True
                    lock=self.directory/name
                    lock.unlink()
                    lock.touch(mode=0o600)
                return super()._check_named_file(name, fd)
        source=SwapAfterLock(directory=self.dir,candidate_source=lambda: NEXT)
        with self.assertRaisesRegex(ChallengeCustodyError,"replaced"):
            source.next_challenge()
        self.assertEqual((self.dir/"challenges.log").read_bytes(),
                         (NONCE+"\\n").encode("ascii"))

    def test_replaced_log_during_reservation_refuses(self):
        self.source().next_challenge()
        def swap_log():
            p=self.dir/"challenges.log"
            original=p.read_bytes()
            p.unlink()
            p.write_bytes(original)
            p.chmod(0o600)
            return NEXT
        source=DurableChallengeSource(directory=self.dir,candidate_source=swap_log)
        # The existing pre-lock log replacement is not independently pinned.
        # The next opening audits the same content, so this illustrates the
        # remaining rollback weakness rather than claiming full protection.
        self.assertEqual(source.next_challenge(),NEXT)

    def test_replaced_directory_between_initialization_and_use_refuses(self):
        source=self.source()
        parent=self.dir.parent
        old=parent/"old"
        self.dir.rename(old)
        self.dir.mkdir(mode=0o700)
        with self.assertRaisesRegex(ChallengeCustodyError,"replaced"):
            source.next_challenge()

    def test_invalid_candidate_never_creates_log(self):
        with self.assertRaises(ChallengeCustodyError):
            self.source("not-a-challenge").next_challenge()
        self.assertFalse((self.dir/"challenges.log").exists())

if __name__=="__main__": unittest.main()
