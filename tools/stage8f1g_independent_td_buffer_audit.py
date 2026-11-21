"""Separate F1G cold stdlib-only TD/episodic buffer causal audit runner.

Pure read-only native receipt re-reduction; never imports the World, Mind,
BodyLaws, F1F/F1G producers, or any life generation entrypoints.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from tools import stage8f1c_independent_postaction_audit as I
from tools import stage8f1f_independent_ecology_audit as X


def main():
    p=argparse.ArgumentParser(description="Independent F1G eight-context TD/buffer audit")
    p.add_argument("source_f1g")
    p.add_argument("original_f1c")
    p.add_argument("audit_output")
    args=p.parse_args()
    original_bytes=Path(args.original_f1c).read_bytes()
    X.check(sha256(original_bytes).hexdigest()==X.F1C_SHA,
            "missing exact original historical F1C evidence bytes")
    source_bytes=Path(args.source_f1g).read_bytes()
    report=X.audit_f1g(json.loads(source_bytes),json.loads(original_bytes))
    X.check(report["source_json_sha256"]==sha256(source_bytes).hexdigest(),
            "original F1G file non-canonical or altered")
    with Path(args.audit_output).open("xb") as out:
        out.write(I.c(report))
    print(json.dumps({
        "status":report["status"],
        "gate":report["overall_gate"],
        "td_verdict":report["td_primary_verdict"],
        "buffer_verdict":report["buffer_primary_verdict"],
        "valid_equal_cost_ecologies":report["matched_cost_ecologies"],
        "td_changed_ecologies":report["td_changed_ecologies"],
        "buffer_changed_ecologies":report["buffer_changed_ecologies"],
        "cold_native_second_steps":report["native_second_steps_checked"],
        "sha256":I.h(report),
    },sort_keys=True))


if __name__=="__main__":
    main()
