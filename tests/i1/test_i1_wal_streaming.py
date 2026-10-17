"""Differential WAL auditor tests, including truncation and chain corruption."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


class WALStreamingTests(unittest.TestCase):
    def test_audit_equivalence_and_stream_only_read(self):
        with TemporaryDirectory() as directory:
            out = Path(directory) / "generated"
            built = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_i1_fork.py"),
                 "--output", str(out)], capture_output=True, text=True)
            self.assertEqual(built.returncode, 0, built.stderr)
            script = r"""
import io
import os
import tempfile
from unittest.mock import patch
from i1lab.journal import HashChainedJournal
from i1lab.determinism import canonical_causal_bytes

with tempfile.TemporaryDirectory() as directory:
    path = os.path.abspath(os.path.join(directory, "events.wal"))
    journal = HashChainedJournal()
    for i in range(256):
        journal.append(event_id=f"event:{i}", causal_event={
            "kind":"test_event", "t_monde":i, "data":{"number":i}})
    valid = b"".join(canonical_causal_bytes(x.as_dict()) + b"\n"
                     for x in journal.entries)
    real_open = open
    class StreamingOnly(io.BytesIO):
        def read(self, *args, **kwargs):
            raise AssertionError("whole-file WAL read is forbidden")
    def streaming_open(target, mode="r", *args, **kwargs):
        if target == path and mode == "rb":
            return StreamingOnly(real_open(target, "rb").read())
        return real_open(target, mode, *args, **kwargs)
    trials = [
        (b"",True),
        (valid,True),
        (valid.replace(b"\n", b"\r\n"), False),
        (valid[:-1],False),
        (valid + b"\n",False),
        (valid.replace(b'"event:42"', b'"event:99"', 1),False),
        (valid + b"garbage\n",False),
    ]
    for content, ok in trials:
        with real_open(path,"wb") as stream:
            stream.write(content)
        with patch("builtins.open", streaming_open):
            try:
                observed=HashChainedJournal.audit_durable_wal(path)
            except (ValueError, RuntimeError):
                if ok: raise
            else:
                assert ok, content[-45:]
                assert observed["verified_entries"] == (256 if content else 0)
                assert observed["head_hash"] == (
                    journal.head_hash if content else "00" * 32)
print("I1_WAL_STREAMING_AUDIT_OK")
"""
            checked = subprocess.run(
                [sys.executable, "-c", script], capture_output=True,
                text=True, env={"PYTHONPATH":str(out)})
            self.assertEqual(checked.returncode, 0, checked.stderr)
            self.assertIn("I1_WAL_STREAMING_AUDIT_OK", checked.stdout)


if __name__ == "__main__":
    unittest.main()
