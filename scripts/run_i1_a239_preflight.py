"""A2.39 prebirth physical and perception hard gate; no individual born."""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path

from i1_a239_lock import assigned, prebirth_hard_gate, PREREG_BLOB
from i1_a239_fixtures import world_case, factor_flags
from i1_a238_fixtures import references, TRAIN_SHA
from i1_a238_model import sealed_model


def preflight(output: Path, source_sha: str):
    from i1lab.world import WorldBody
    from i1lab.determinism import canonical_causal_bytes, sha256_hex

    if len(source_sha) != 40 or any(c not in "0123456789abcdef" for c in source_sha):
        raise ValueError("A2.39 requires immutable full source SHA")
    allocation = prebirth_hard_gate()
    model, model_seal = sealed_model(output)
    if model.corpus_sha256 != TRAIN_SHA or model.source_scope != "external_lab":
        raise RuntimeError("external source was not reconstructed")
    s11, c11, c10, policy = references()
    records = []
    for stratum, i, arm in allocation:
        world, layout, configured, events, east = world_case(s11,c11,stratum,i,arm)
        flags = factor_flags(arm)
        if events or bool(configured.geographic) != (arm == "H1_GEO"):
            raise RuntimeError("forbidden geospatial or scenario intervention")
        record = {
            "ordinal": len(records),
            "life_id": f"i1:a239:{stratum}:{i:02d}:{arm}",
            "stratum": stratum,
            "case_index": i,
            "arm": arm,
            "physics_sha256": sha256_hex(canonical_causal_bytes(world.as_dict())),
            "layout_sha256_operator_only": sha256_hex(canonical_causal_bytes(layout.as_dict())),
            "birth_flags": flags,
        }
        records.append(record)
    if len(records) != 160 or len({r["life_id"] for r in records}) != 160:
        raise RuntimeError("A2.39 incorrect lifetime population")
    for idx in range(0,160,5):
        case=records[idx:idx+5]
        if (len({r["physics_sha256"] for r in case}) != 1
                or len({r["layout_sha256_operator_only"] for r in case}) != 1):
            raise RuntimeError("paired life physics diverged")
    for i in range(8):
        for arm in ("BASE","H1_ONLY","H1_GEO","STRICT_UNKNOWN","FOOD_FIRST_RISK"):
            p1,l1,_,_,_ = world_case(s11,c11,"FOOD_FIRST_E_SAFE",i,arm)
            p2,l2,_,_,_ = world_case(s11,c11,"FOOD_FIRST_E_INVISIBLE_LETHAL",i,arm)
            if (p1.as_dict()!=p2.as_dict() or
                    WorldBody(config=p1,layout=l1).capture_local(t_monde=1).as_dict()!=
                    WorldBody(config=p2,layout=l2).capture_local(t_monde=1).as_dict()):
                raise RuntimeError("hidden hazard leaked into first-person inputs")
    manifest={"schema":"a239-prebirth-manifest-v1","source_sha":source_sha,
              "prereg_blob":PREREG_BLOB,"training":model_seal,
              "count":160,"births":records}
    (output/"birth-manifest.json").write_text(json.dumps(manifest,sort_keys=True,indent=2)+"\n")
    return manifest


def main():
    import argparse,sys
    from tempfile import TemporaryDirectory
    from build_i1_fork import generate
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--source-sha",required=True)
    args=p.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    with TemporaryDirectory(prefix="a239-code-") as tmp:
        built=Path(tmp)/"build"
        generate(built)
        sys.path.insert(0,str(built))
        manifest=preflight(args.output,args.source_sha)
    print(json.dumps({"births_planned":manifest["count"],"born":0,"prebirth":"PASS"}))


if __name__=="__main__":
    main()
