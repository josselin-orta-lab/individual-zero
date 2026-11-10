"""Read-only, independent Stage-2.1 64-triplet original-custody audit.

No imports from I3 simulation, no World/genome/Mind or admission construction,
no replay/rerun and no write to original evidence. Verify the *archived bytes*
against their first source-locked manifest and the original R report.
Run against a separate checkout of the immutable evidence commit, not a
runtime-generated replacement for any of the 192 original lives.
"""
from __future__ import annotations

from collections import Counter
import gzip
from hashlib import sha256
import json
from math import fsum, isclose, isfinite
from pathlib import Path
import sys

SCHEMA = "i3-three-arm-post-archive-original-audit/v1"
SOURCE = "11879c46a78697aa1d3f664f1a17f489a948667d"
SOURCE_FINGERPRINT = "37989805cadf6502e105e500e25a656e7898e4873a21f4d51b283c42c6754327"
PLAN_SHA256 = "585dd83dff80bcfc9b0014db929113f84f8c8d41938749fea39f4052a61e43ae"
MANIFEST_SHA256 = "f493a30598c3dd82f56ab84653537286487bea61414cfc2226785209c724a50f"
POLICIES = ("reference", "p13_replay_gate_v1",
            "p13_replay_gate_random_equal_mean_v1")
FAMILIES = ("stable", "depletion", "pulse")
SOURCE_ROOT = "three-dev-"
UNITS = 64
HORIZON = 400
FIELDS = ("pair_id", "index", "cohort", "family", "policy",
          "world_seed", "genome_seed", "life_seed")
RANDOM_KEYS = ("draws_funded", "nominal_replays_scheduled",
               "eligible_replays_scheduled", "actual_replays_paid",
               "lived_sleep_ordinals")


def _hash(raw: bytes) -> str:
    return sha256(raw).hexdigest()


def _canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def _read_json(path: Path):
    return json.loads(path.read_bytes())


def _require(ok, message):
    if not ok:
        raise ValueError(message)


def _float_eq(actual, expected):
    return (type(actual) in (int, float) and
            type(expected) in (int, float) and
            isfinite(actual) and isfinite(expected) and
            isclose(actual, expected, abs_tol=1e-8, rel_tol=1e-12))


def _original_row(identity, life, published, source_fingerprint):
    """Rebuild the historical reducer receipt independently, from raw life."""
    m = life["manifest"]
    c = life["cognitive_accounting"]
    r = life["admission_receipt"]
    policy = identity["policy"]
    _require(policy in POLICIES and identity["cohort"] == "development",
             "foreign cohort/policy")
    _require(m["source"]["sha256"] == published["source_sha256"],
             "source bytes mismatch in original")
    _require(r["cohort"] == "development" and
             r["family"] == identity["family"] and
             r["index"] == identity["index"] and
             r["world_seed"] == identity["world_seed"] and
             r["world_sha256"] == m["world_sha256"] and
             r["world_name"] == life["world"] and
             r["transport_fingerprint"] == source_fingerprint,
             "source/World/admission mismatch in original")
    _require(m["life_seed"] == identity["life_seed"],
             "life seed differs between original and allocation")
    _require(m.get("experimental_policy", {}).get("name", "reference") == policy,
             "wrong actual Mind policy")
    _require(("replay_gate" in life) == (policy != "reference"),
             "wrong gate receipt presence")
    _require(c["status"] == "SETTLED_FOR_DECLARED_WORK" and
             c["shortfall_steps"] == 0 and
             c["totals"]["energy"]["unpaid"] <= 1e-12 and
             c["totals"]["vigilance"]["unpaid"] <= 1e-12,
             "unfunded cognition")
    lived = life["steps_lived"]
    _require(type(lived) is int and 1 <= lived <= HORIZON and
             life["terminal"] in ("censored", "dead") and
             (life["terminal"] != "censored" or lived == HORIZON),
             "terminal boundary invalid")
    _require(type(c["replays_executed"]) is int and
             c["replays_executed"] >= 0, "invalid paid replay count")
    _require(type(c["inactive_steps"]) is int and
             0 <= c["inactive_steps"] <= lived, "invalid inactivity receipt")
    _require(type(life["actions"].get("dormir", 0)) is int, "sleep count invalid")
    random_schedule = None
    if policy == POLICIES[2]:
        rs = life["replay_gate"]["random_schedule"]
        _require(rs["mean_numerator"] == 5532 and
                 rs["mean_denominator"] == 867,
                 "historical nominal random mean changed")
        _require(all(type(rs[key]) is int and rs[key] >= 0
                     for key in RANDOM_KEYS), "invalid random schedule counts")
        draws, nominal, eligible, paid, ordinal = (rs[k] for k in RANDOM_KEYS)
        _require(6 * draws <= nominal <= 7 * draws and
                 0 <= paid <= eligible <= nominal and
                 paid == c["replays_executed"] and
                 draws <= ordinal <= life["actions"].get("dormir", 0),
                 "random nominal/eligible/actually paid chain violated")
        random_schedule = {key: rs[key] for key in RANDOM_KEYS}
    else:
        _require(policy == POLICIES[0] or
                 "random_schedule" not in life["replay_gate"],
                 "random receipts on nonrandom arm")
    expected = {
        **identity,
        "terminal": life["terminal"],
        "steps_lived": lived,
        "death_causes": life["death_causes"],
        "dead_at_400": life["terminal"] == "dead" and lived == HORIZON,
        "paid_energy": c["totals"]["energy"]["paid"],
        "paid_vigilance": c["totals"]["vigilance"]["paid"],
        "replays_paid": c["replays_executed"],
        "sleep_steps": life["actions"].get("dormir", 0),
        "inactive_steps": c["inactive_steps"],
        "random_schedule": random_schedule,
        "world_sha256": m["world_sha256"],
        "genome_sha256": _hash(_canonical(m["genome"])),
        "source_sha256": m["source"]["sha256"],
    }
    _require(set(published) == set(expected),
             "reduced row has missing or added fields")
    for key in expected:
        if key in ("paid_energy", "paid_vigilance"):
            _require(_float_eq(published[key], expected[key]),
                     "paid original-to-reduced mismatch: " + key)
        else:
            _require(published[key] == expected[key],
                     "original-to-reduced mismatch: " + key)
    return expected


def _summarize(rows):
    triples = [rows[3*i:3*i+3] for i in range(UNITS)]
    for i, trio in enumerate(triples):
        _require(tuple(row["policy"] for row in trio) == POLICIES,
                 "policy order differs from prospective plan")
        _require(all(row["index"] == 360000+i and
                     row["pair_id"] == f"{SOURCE_ROOT}{i:06d}" and
                     row["cohort"] == "development" and
                     row["family"] in FAMILIES for row in trio),
                 "index/identity outside reserved prospective triplets")
        for key in ("family", "pair_id", "index", "world_seed",
                    "genome_seed", "life_seed", "world_sha256",
                    "genome_sha256", "source_sha256"):
            _require(len({row[key] for row in trio}) == 1,
                     "not a matched three-arm original: " + key)
        _require(trio[0]["source_sha256"] == trio[1]["source_sha256"] ==
                 trio[2]["source_sha256"], "source changed between arms")
    _require(len({t[0]["world_seed"] for t in triples}) == UNITS and
             len({t[0]["genome_seed"] for t in triples}) == UNITS and
             len({t[0]["life_seed"] for t in triples}) == UNITS,
             "duplicate assigned world, genome or life seed")

    by_arm = {}
    for j, policy in enumerate(POLICIES):
        arm = [t[j] for t in triples]
        by_arm[policy] = {
            "units": UNITS,
            "horizon_survivors": sum(r["terminal"] == "censored" for r in arm),
            "deaths_at_horizon": sum(r["dead_at_400"] for r in arm),
            "mean_lived_steps": fsum(r["steps_lived"] for r in arm)/UNITS,
            "mean_energy_paid_per_assigned_life":
                fsum(r["paid_energy"] for r in arm)/UNITS,
            "mean_vigilance_paid_per_assigned_life":
                fsum(r["paid_vigilance"] for r in arm)/UNITS,
            "mean_replays_paid_per_assigned_life":
                fsum(r["replays_paid"] for r in arm)/UNITS,
            "mean_sleep_steps_per_assigned_life":
                fsum(r["sleep_steps"] for r in arm)/UNITS,
        }
        if j == 2:
            by_arm[policy]["random_schedule_per_assigned_life"] = {
                key: fsum(r["random_schedule"][key] for r in arm)/UNITS
                for key in RANDOM_KEYS}
    def paired(blocks, left, right):
        a=[t[left] for t in blocks]
        b=[t[right] for t in blocks]
        xs=[r["terminal"]=="censored" for r in a]
        ys=[r["terminal"]=="censored" for r in b]
        return {
            "units":len(blocks),
            "both_survive":sum(x and y for x,y in zip(xs,ys)),
            "target_only_survives":sum(x and not y for x,y in zip(xs,ys)),
            "comparator_only_survives":sum(y and not x for x,y in zip(xs,ys)),
            "neither_survives":sum(not x and not y for x,y in zip(xs,ys)),
            "paired_risk_difference":fsum(int(x)-int(y)
                                          for x,y in zip(xs,ys))/len(blocks),
            "mean_lived_step_difference":
                fsum(x["steps_lived"]-y["steps_lived"]
                     for x,y in zip(a,b))/len(blocks),
            "target_shorter_lived":sum(x["steps_lived"]<y["steps_lived"]
                                      for x,y in zip(a,b)),
            "target_longer_lived":sum(x["steps_lived"]>y["steps_lived"]
                                     for x,y in zip(a,b)),
        }
    pairs={label: paired(triples,a,b) for label,a,b in
           (("GATE_MINUS_RANDOM",1,2),("GATE_MINUS_FIXED",1,0),
            ("RANDOM_MINUS_FIXED",2,0))}
    family={}
    for name in FAMILIES:
        blocks=[t for t in triples if t[0]["family"]==name]
        _require(bool(blocks), "missing F0 family")
        family[name]={
            "contrasts":{label:paired(blocks,a,b) for label,a,b in
                         (("GATE_MINUS_RANDOM",1,2),("GATE_MINUS_FIXED",1,0),
                          ("RANDOM_MINUS_FIXED",2,0))}
        }
    return by_arm,pairs,family


def _same_tree(expected, actual, label):
    _require(isinstance(expected,dict) and isinstance(actual,dict) and
             set(expected)==set(actual), "aggregate keys mismatch: "+label)
    for key,value in expected.items():
        found=actual[key]
        if isinstance(value,dict):
            _same_tree(value,found,label+"."+key)
        elif type(value) in (int,float) and type(found) in (int,float):
            _require(_float_eq(value,found), "aggregate mismatch: "+label+"."+key)
        else:
            _require(value==found,"aggregate mismatch: "+label+"."+key)


def audit(root: Path) -> dict:
    """Verify exactly 192 original bytes and all 192 matching reduction rows."""
    root=Path(root).resolve()
    lock=_read_json(root/"SOURCE_LOCK.json")
    report=_read_json(root/"EXECUTION_REPORT.json")
    rows=_read_json(root/"REDUCED_ROWS.json")
    original_dir=root/"originals"
    raw_manifest=(original_dir/"MANIFEST.json").read_bytes()
    sha_file=(original_dir/"MANIFEST.sha256").read_text().strip()
    _require(_hash(raw_manifest)==sha_file==MANIFEST_SHA256,
             "source-pinned original manifest SHA-256 mismatch")
    manifest=json.loads(raw_manifest)
    _require(lock["source_sha"]==report["source_sha"]==SOURCE and
             lock["source_fingerprint"]==report["source_fingerprint"]==
             SOURCE_FINGERPRINT and
             lock["plan_sha256"]==report["plan_sha256"]==PLAN_SHA256 and
             lock["status"]=="CONSUMED_BEFORE_FIRST_BIRTH" and
             lock["units"]==UNITS and lock["lives"]==UNITS*3 and
             lock["no_retry"] is True and
             lock["scientific_inference_authorized"] is False,
             "original source lock/plan/one-shot claim mismatch")
    _require(manifest["status"]=="GENERATED" and
             manifest["planned"]==manifest["generated"]==UNITS*3 and
             len(manifest["files"])==UNITS*3 and manifest["failure"] is None,
             "missing original in generation manifest")
    _require(report["status"]=="COMPLETE_EXPLORATORY_DEVELOPMENT_ONLY" and
             report["phase_G"]=="GENERATED" and report["phase_R"]=="COMPLETE" and
             report["planned"]==report["generated"]==report["reduced"]==UNITS*3 and
             report["scientific_verdict"]=="NOT_ISSUED",
             "original execution incomplete or promoted")
    _require(isinstance(rows,list) and len(rows)==UNITS*3,
             "missing reduced source row")
    filenames={f"life-{i:03d}.json.gz" for i in range(UNITS*3)}
    _require({f["file"] for f in manifest["files"]}==filenames and
             len(set(f["file"] for f in manifest["files"]))==UNITS*3 and
             {p.name for p in original_dir.glob("life-*.json.gz")}==filenames,
             "missing, substituted or unexpected original gzip file")
    verified=[]
    for i,record in enumerate(manifest["files"]):
        _require(record["file"]==f"life-{i:03d}.json.gz",
                 "archive original order modified")
        packed=(original_dir/record["file"]).read_bytes()
        _require(_hash(packed)==record["sha256"],
                 "compressed original SHA mismatch: "+record["file"])
        raw=gzip.decompress(packed)
        _require(_hash(raw)==record["uncompressed_sha256"],
                 "uncompressed original SHA mismatch: "+record["file"])
        payload=json.loads(raw)
        identity=payload["identity"]
        _require(identity==record["identity"] and
                 all(identity.get(k)==rows[i].get(k) for k in FIELDS),
                 "original identity differs from reduced/manifest row")
        verified.append(_original_row(identity,payload["life"],rows[i],
                                      SOURCE_FINGERPRINT))
    arms,pairs,families=_summarize(verified)
    published=report["analysis"]
    _require(published["primary"]=="GATE_MINUS_RANDOM" and
             published["scientific_verdict"]=="NOT_ISSUED" and
             published["external_iid_or_ecological_sampling_attestation"] is False and
             published["scientific_noninferiority_margin_approved"] is False and
             published["selection_validation_reserve_executed"] is False,
             "unregistered inference or altered primary outcome")
    _same_tree(arms,published["by_arm"],"by_arm")
    _same_tree(pairs,published["overall_contrasts"],"overall_contrasts")
    for name in FAMILIES:
        _same_tree(families[name]["contrasts"],
                   published["by_family"][name]["contrasts"],
                   "by_family."+name+".contrasts")
    _require(pairs["GATE_MINUS_RANDOM"]["target_only_survives"]==4 and
             pairs["GATE_MINUS_RANDOM"]["comparator_only_survives"]==4 and
             pairs["GATE_MINUS_RANDOM"]["both_survive"]==23 and
             pairs["GATE_MINUS_RANDOM"]["neither_survives"]==33,
             "published 64-unit null result not recovered")
    _require(arms[POLICIES[0]]["horizon_survivors"]==26 and
             arms[POLICIES[1]]["horizon_survivors"]==27 and
             arms[POLICIES[2]]["horizon_survivors"]==27,
             "primary survivor count not independently reproduced")
    return {
        "schema":SCHEMA,
        "status":"READ_ONLY_ORIGINAL_REANALYSIS_PASS",
        "source_sha":SOURCE,
        "source_fingerprint":SOURCE_FINGERPRINT,
        "manifest_sha256":MANIFEST_SHA256,
        "originals_compressed_verified":len(verified),
        "originals_uncompressed_verified":len(verified),
        "matched_triplets":UNITS,
        "survivors":{k:v["horizon_survivors"] for k,v in arms.items()},
        "gate_minus_random":pairs["GATE_MINUS_RANDOM"],
        "family_primary_discordance":{
            name:families[name]["contrasts"]["GATE_MINUS_RANDOM"]
            for name in FAMILIES},
        "nominal_vs_paid_random_replay_total":{
            k:round(arms[POLICIES[2]]["random_schedule_per_assigned_life"][k]*UNITS)
            for k in RANDOM_KEYS},
        "scientific_go":False,
        "iid_or_mechanism_identification_claimed":False,
        "no_world_or_life_executed":True,
    }


def main(argv=None):
    argv=sys.argv if argv is None else argv
    if len(argv)!=2:
        raise SystemExit("usage: python -m i3.lab.stage2_three_arm_original_audit ARCHIVED_ORIGINALS_DIRECTORY")
    print(json.dumps(audit(Path(argv[1])),sort_keys=True,indent=2))


if __name__=="__main__":
    main()
