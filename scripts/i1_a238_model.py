"""Rebuild and authenticate A2.38 prebirth external-lab training."""
import json
import subprocess
import sys
from pathlib import Path

from i1_a238_fixtures import TRAIN_SHA, LOCK_SHA


def sealed_model(directory: Path):
    from i1.experimental.stage6_visible_delta_shadow import (
        ShadowVisibleDeltaModel, MODEL_VERSION, FIELDS,
    )
    script=Path(__file__).with_name("run_i1_a238_training_lock.py")
    target=directory/"sealed-prebirth-training"
    result=subprocess.run(
        [sys.executable,str(script),"--output",str(target)],
        capture_output=True,text=True,check=False,
    )
    if result.returncode:
        raise RuntimeError("A2.38 prebirth source failure: "+result.stderr[-900:])
    seal=json.loads((target/"seal.json").read_text())
    if (seal.get("input_lock_blob")!=LOCK_SHA
            or seal.get("corpus_sha256")!=TRAIN_SHA
            or seal.get("samples")!=16
            or seal.get("individual_births")!=0
            or seal.get("model_version")!=MODEL_VERSION):
        raise RuntimeError("A2.38 prospective source seal mismatch")
    rows=seal.get("rows")
    if not isinstance(rows,list) or len(rows)!=16:
        raise RuntimeError("wrong physical training population")
    ids=[row["id"] for row in rows]
    expected=[f"a238:{action}:{i}" for action in ("MOVE_E","COLLECT_B")
              for i in range(8)]
    if ids!=expected:
        raise RuntimeError("prebirth source identities not fixed")
    deltas=tuple((name,tuple((field,value) for field,value in vals))
                  for name,vals in seal["model_deltas"])
    if (set(dict(deltas))!={"MOVE_E","COLLECT_B"}
            or any(tuple(k for k,_ in vals)!=FIELDS for _,vals in deltas)):
        raise RuntimeError("model factors do not match frozen training")
    model=ShadowVisibleDeltaModel(MODEL_VERSION,TRAIN_SHA,deltas,
                                  (("MOVE_E",8),("COLLECT_B",8)))
    return model, {"training_sha256":TRAIN_SHA,"input_lock_blob":LOCK_SHA,
                   "samples":len(ids),"model_version":MODEL_VERSION}
