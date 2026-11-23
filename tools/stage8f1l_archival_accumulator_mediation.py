"""F1L archival-only accumulator transport audit; stdlib, NO i3/Mind/World imports.

Exploratory POSTHOC structural witness analysis, NOT a new scientific outcome.
Reads only GitHub immutable RAW/COLD release bytes and original 128 gzip receipts.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from math import isclose
from pathlib import Path
import sys
import tarfile

ARCHIVE_DIGEST = "fc47a04fa7aa65c1726fc4e5896f85bda9ca0a4dbeba18ebecb5f105f1b7a64f"
MANIFEST_DIGEST = "fca85816a870d7c0c124cdd23dc1aefdd5efcbe04fc5d475c019649a0bb20b44"
COLD_DIGEST = "dbb35567b3d199a7f3f988d7d0b5b79c0e9698d580c90195e980d8f6f56f97d0"
LEAK, GAIN, THRESHOLD, RESIDUAL = 0.2, 1.0, 1.5, 0.5
EXPECTED_ARMS = ("source", "full", "full_sham", "stale_owned_t1_means")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def check(condition, explanation):
    if not condition:
        raise AssertionError("ARCHIVAL_F1L: " + explanation)


def same_float(left, right):
    return isclose(left, right, rel_tol=0, abs_tol=1e-10)


def private(mind):
    check(mind["data"]["class"] == "F1JFixedRoundMind", "changed controller")
    pairs = mind["data"]["private"]["__dict__"]
    result = {key: value for key, value in pairs}
    check(len(result) == len(pairs), "duplicated brain private field")
    return result


def accumulated(mind):
    raw = private(mind)["acc"]["__dict__"]
    vals = dict(raw)
    check(len(vals) == len(raw), "duplicate accumulator key")
    return vals


def witness(step):
    return step["decision_info"]["observer"]["competition_witness"]


def competition_algebra(w, incoming, verify_actual=False):
    """Recalculate archived F1J witness arithmetic, WITHOUT calling Mind.decide.

    A substituted incoming state is a single-equation sensitivity probe,
    NOT a native decision, bodily action, or paid counterfactual life.
    """
    opts = w["scored_order"]
    evid = w["normalized_evidence"]
    thresholds = w["thresholds"]
    rounds = w["paid_competition_cycles"]
    check(0 < rounds <= w["round_capacity_from_actual_body"], "unpaid fixed round")
    check(set(opts) == set(evid) == set(thresholds), "inconsistent scored set")
    check(len(opts) == len(set(opts)), "duplicate scored option")
    acc = {o: incoming.get(o, 0.0) for o in opts}
    for i in range(rounds):
        for o in opts:
            acc[o] = max(0.0, (1.0 - LEAK) * acc[o] + GAIN * evid[o])
        if verify_actual:
            snapshot = w["actual_substantive_round_snapshots"][i]
            check(all(same_float(acc[o], snapshot[o]) for o in opts),
                  "fixed-round private update does not match original")
    if verify_actual:
        check(all(same_float(acc[o], w["accumulators_before_residual"][o])
                  for o in opts), "original before-residual witness differs")

    crossed = [((acc[o] - thresholds[o]) / thresholds[o], o)
               for o in opts if acc[o] >= thresholds[o]]
    if crossed:
        highest = max(m for m, o in crossed)
        ties = sorted(o for m, o in crossed if m == highest)
        mechanism = "final_round_threshold"
    else:
        best = max(acc.values())
        ties = sorted(o for o, x in acc.items() if x >= best - 1e-12)
        if len(ties) == len(opts) and max(acc.values()) - min(acc.values()) <= 1e-12:
            mechanism = "all_activations_equal_raw_score_fallback"
            # Raw scored-options fallback cannot be reconstructed solely from
            # normalized evidence without the original score + sorting tie rule.
            ties = None
        else:
            mechanism = "final_round_activation"
    if ties is None:
        selection = None
    elif len(ties) == 1:
        selection = ties[0]
    elif w["prior_intention"] in ties:
        selection = w["prior_intention"]
    else:
        selection = None  # RNG tie-breaking is intentionally NOT reconstructed.
    if verify_actual:
        check(mechanism == w["selection_mechanism"], "selection mechanism changed")
        if ties is not None:
            check(ties == w["tie_candidates"], "native tie candidates mismatch")
        if selection is not None:
            check(selection == w["winner_before_control"], "native winner mismatch")
        last = {o: 0.0 if o == w["winner_before_control"] else acc[o] * RESIDUAL
                for o in opts}
        check(all(same_float(last[o], w["accumulators_after_residual"][o])
                  for o in opts), "native RESIDUAL algebra mismatch")
    return {"unique_or_intention_winner": selection, "ties": ties,
            "selection_mechanism": mechanism}


def read(base):
    names = ["F1L_ORIGINALS_128_GZIP.tar.gz", "F1L_CUSTODY_MANIFEST.json",
             "F1L_INDEPENDENT_COLD_T60.json"]
    digests = [ARCHIVE_DIGEST, MANIFEST_DIGEST, COLD_DIGEST]
    for name, expected in zip(names, digests):
        check(sha((base/name).read_bytes()) == expected, name + " checksum")
    manifest = json.loads((base/names[1]).read_bytes())
    cold = json.loads((base/names[2]).read_bytes())
    check(manifest["native_part_count"] == 128 and
          len(manifest["roots"]) == 32 and
          manifest["heldout_native_passes"] == 1 and
          manifest["phase"] == "F1L_HELDOUT_RELEASE", "source custody")
    check(cold["cold_verdict"] ==
          "NO_REPRODUCIBLE_LOCAL_T60_CONTENT_BODY_ADVANTAGE" and
          cold["roots"] == cold["personal_paid_sources_verified"] == 32 and
          cold["T5_equal_real_decision_cost_pairs"] == 32 and
          cold["whole_trajectory_shams_verified"] == 32 and
          manifest["native_original_sha256"] == cold["original_sha256"],
          "primary science not preserved")
    entries = {r["path"]: r for r in manifest["entries"]}
    check(len(entries) == 128 and set(entries) ==
          {f"{i}/{a}.json.gz" for i in manifest["roots"] for a in EXPECTED_ARMS},
          "source/arms not exactly 128")
    return manifest, cold, entries


def audit(base):
    import gzip
    manifest, cold, entries = read(base)
    per_root = []
    verified = 0
    with tarfile.open(base/"F1L_ORIGINALS_128_GZIP.tar.gz", "r:gz") as archive:
        members = {m.name: m for m in archive.getmembers()}
        check(len(members) == 160 and all(m.isfile() for m in members.values()),
              "missing source/checkpoint")
        check(set(entries).issubset(members), "missing required original parts")

        def original(root, part):
            nonlocal verified
            name = f"{root}/{part}.json.gz"
            raw_gz = archive.extractfile(members[name]).read()
            body = gzip.decompress(raw_gz)
            entry = entries[name]
            check(sha(raw_gz) == entry["gzip_sha256"] and
                  sha(body) == entry["original_sha256"] and
                  len(raw_gz) == entry["gzip_bytes"] and
                  len(body) == entry["original_bytes"], "changed gzip " + name)
            wrapped = json.loads(body)
            check(wrapped["schema"] == "i3-stage8f1l-native-origin-part/v0" and
                  wrapped["id"] == root and wrapped["part"] == part,
                  "incorrect original wrapper " + name)
            verified += 1
            return wrapped["native"]

        for detail in cold["per_root"]:
            root = detail["root"]
            src = original(root, "source")
            full = original(root, "full")
            sham = original(root, "full_sham")
            stale = original(root, "stale_owned_t1_means")
            check(len(src["source_steps"]) == 4 and
                  src["valid_paid_personal_source"], "invalid paid source " + root)
            check(full["last_world"] == sham["last_world"] and
                  full["last_mind"] == sham["last_mind"] and
                  full["metrics"] == sham["metrics"], "invalid sham " + root)
            steps_f, steps_s = full["steps"], stale["steps"]
            check(len(steps_f) == len(steps_s) == 56 and
                  steps_f[0]["t"] == steps_s[0]["t"] == 5 and
                  steps_f[1]["t"] == steps_s[1]["t"] == 6,
                  "incomplete original T5-T60 " + root)
            f5,s5 = steps_f[0],steps_s[0]
            f6,s6 = steps_f[1],steps_s[1]
            wf5,ws5,wf6,ws6 = [witness(x) for x in (f5,s5,f6,s6)]
            check(f5["before_world"] == s5["before_world"] and
                  f5["before_mind"] == s5["before_mind"] and
                  f5["capture"] == s5["capture"] and
                  f5["cognitive_work"] == s5["cognitive_work"] and
                  f5["requested_native_cost"] == s5["requested_native_cost"] and
                  f5["native_motor"]["cognitive_accounting"] ==
                  s5["native_motor"]["cognitive_accounting"],
                  "T5 controls differ " + root)
            check(wf5["accumulators_before"] == ws5["accumulators_before"],
                  "different baseline residual at T5 " + root)

            t5_same_motor = (f5["action"],f5["param"]) == (s5["action"],s5["param"])
            t6_same_motor = (f6["action"],f6["param"]) == (s6["action"],s6["param"])
            t5_same_world = f5["after_paid_learning_world"] == s5["after_paid_learning_world"]
            afterf,afters = private(f5["after_paid_learning_mind"]), private(s5["after_paid_learning_mind"])
            check(set(afterf) == set(afters), "different sealed mind field keys " + root)
            differences = sorted(k for k in afterf if afterf[k] != afters[k])
            non_diag_diff = [k for k in differences if k != "acc" and "observer" not in k]
            check(f5["after_paid_learning_mind"] == f6["before_mind"] and
                  s5["after_paid_learning_mind"] == s6["before_mind"],
                  "T5 mind was not carried into T6 " + root)
            check(accumulated(f5["after_paid_learning_mind"]) ==
                  wf5["accumulators_after_residual"] and
                  accumulated(s5["after_paid_learning_mind"]) ==
                  ws5["accumulators_after_residual"],
                  "T5 residual not retained in mind " + root)
            check(all(same_float(wf6["accumulators_before"][o],
                                 wf5["accumulators_after_residual"].get(o, 0.0))
                      for o in wf6["scored_order"]) and
                  all(same_float(ws6["accumulators_before"][o],
                                 ws5["accumulators_after_residual"].get(o, 0.0))
                      for o in ws6["scored_order"]),
                  "residual T5->T6 carry across paid learning " + root)

            actual_f = competition_algebra(wf6, wf6["accumulators_before"], True)
            actual_s = competition_algebra(ws6, ws6["accumulators_before"], True)
            same_t6_evidence = wf6["normalized_evidence"] == ws6["normalized_evidence"]
            same_t6_thresholds = wf6["thresholds"] == ws6["thresholds"]
            same_t6_order = wf6["scored_order"] == ws6["scored_order"]
            same_t6_scores = f6["decision_info"]["observer"]["score_witness"] == s6["decision_info"]["observer"]["score_witness"]
            same_t6_comp_cost = f6["cognitive_work"] == s6["cognitive_work"]
            swap_f = swap_s = None
            if same_t6_order:
                swap_f = competition_algebra(wf6, ws6["accumulators_before"])
                swap_s = competition_algebra(ws6, wf6["accumulators_before"])
            reset_f=competition_algebra(wf6, {})
            reset_s=competition_algebra(ws6, {})
            first_different_motor = next((a["t"] for a,b in zip(steps_f,steps_s)
                if (a["action"],a["param"]) != (b["action"],b["param"])), None)
            first_different_body = next((a["t"] for a,b in zip(steps_f,steps_s)
                if any(abs(x-y) > 1e-9 for x,y in zip(
                    a["postaction"]["body_after_any_learning"],
                    b["postaction"]["body_after_any_learning"]))),None)
            flagged = (root in ("L06","L14"))
            if flagged:
                check(t5_same_motor and t5_same_world and
                      first_different_motor == 6 and first_different_body == 7,
                      "L06/L14 prior observation not conserved")
            row = {
                "root":root, "ecology":detail["ecology"],
                "t5_motor_equal":t5_same_motor,
                "t5_world_equal_after_learning":t5_same_world,
                "t5_full": [f5["action"],f5["param"]],
                "t5_stale": [s5["action"],s5["param"]],
                "t6_full": [f6["action"],f6["param"]],
                "t6_stale": [s6["action"],s6["param"]],
                "t6_motor_equal":t6_same_motor,
                "first_motor_divergence":first_different_motor,
                "first_body_divergence":first_different_body,
                "post_t5_private_changed_fields":differences,
                "post_t5_non_observer_non_acc_changed_fields":non_diag_diff,
                "t6_same_scores":same_t6_scores,
                "t6_same_normalized_evidence":same_t6_evidence,
                "t6_same_thresholds":same_t6_thresholds,
                "t6_same_scored_order":same_t6_order,
                "t6_equal_actual_work":same_t6_comp_cost,
                "t6_original_winner_full":wf6["winner_before_control"],
                "t6_original_winner_stale":ws6["winner_before_control"],
                "t6_original_ties_full":wf6["tie_candidates"],
                "t6_original_ties_stale":ws6["tie_candidates"],
                "t6_same_actual_competition_cost":wf6["paid_competition_cycles"] == ws6["paid_competition_cycles"],
                "t6_swapped_residual_algebraic_winner_full_evidence":None if swap_f is None else swap_f["unique_or_intention_winner"],
                "t6_swapped_residual_algebraic_winner_stale_evidence":None if swap_s is None else swap_s["unique_or_intention_winner"],
                "t6_zero_residual_algebraic_winner_full_evidence":reset_f["unique_or_intention_winner"],
                "t6_zero_residual_algebraic_winner_stale_evidence":reset_s["unique_or_intention_winner"],
                "t6_prior_intention_equal":wf6["prior_intention"] == ws6["prior_intention"],
                "t6_initial_accumulators_full":wf6["accumulators_before"],
                "t6_initial_accumulators_stale":ws6["accumulators_before"],
                "t6_normalized_evidence_full":wf6["normalized_evidence"] if flagged else None,
                "t6_normalized_evidence_stale":ws6["normalized_evidence"] if flagged else None,
                "t6_witness_mechanism_full":actual_f["selection_mechanism"],
                "t6_witness_mechanism_stale":actual_s["selection_mechanism"],
                "terminal_body_delta": [
                    round(x-y, 8) for x,y in zip(
                        full["metrics"]["terminal_body"],stale["metrics"]["terminal_body"])],
            }
            per_root.append(row)

    check(verified == 128 and len(per_root) == 32, "entire originals not inspected")
    summary = {
        "roots":32,"verified_original_gzips":verified,
        "t5_same_motor":sum(x["t5_motor_equal"] for x in per_root),
        "t5_motor_changed":sum(not x["t5_motor_equal"] for x in per_root),
        "t5_same_motor_t6_different":sum(x["t5_motor_equal"] and not x["t6_motor_equal"] for x in per_root),
        "t5_same_motor_t6_same_scores_evidence":sum(x["t5_motor_equal"] and x["t6_same_scores"] and x["t6_same_normalized_evidence"] for x in per_root),
        "t5_same_motor_non_acc_behavioral_field_changed":sum(x["t5_motor_equal"] and bool(x["post_t5_non_observer_non_acc_changed_fields"]) for x in per_root),
        "t5_same_motor_t6_different_and_no_other_behavioral_private_change":sum(x["t5_motor_equal"] and not x["t6_motor_equal"] and not x["post_t5_non_observer_non_acc_changed_fields"] for x in per_root),
        "survival_gain_count":cold["survival_gain_count"],
        "survival_loss_count":cold["survival_loss_count"],
        "f1l_cold_verdict":cold["cold_verdict"],
    }
    return {
        "schema":"i3-stage8f1l-archival-accumulator-mediation-exploratory/v0",
        "interpretation":"Archival structural and single-equation arithmetic probes, not native mediator interventions or new lives.",
        "f1l_historical_verdict_unmodified":True,
        "engine_imports":0,"new_world_steps":0,
        "source_release_tag":"i3-stage8f1l-t60-raw-heldout-once",
        "independent_cold_release_tag":"i3-stage8f1l-t60-cold-heldout-once",
        "summary":summary,"per_root":per_root,
    }


def main():
    path=Path(sys.argv[1])
    report=audit(path)
    (path/"F1L_ARCHIVAL_ACCUMULATOR_MEDIATION.json").write_text(
        json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("SUMMARY",json.dumps(report["summary"],sort_keys=True))
    for x in report["per_root"]:
        if x["root"] in ("L06","L14","L20","L22","L24","L29","L31"):
            keys=("root","t5_motor_equal","t6_motor_equal",
                  "post_t5_private_changed_fields",
                  "post_t5_non_observer_non_acc_changed_fields",
                  "t6_same_scores","t6_same_normalized_evidence",
                  "t6_original_winner_full","t6_original_winner_stale",
                  "t6_swapped_residual_algebraic_winner_full_evidence",
                  "t6_swapped_residual_algebraic_winner_stale_evidence",
                  "t6_zero_residual_algebraic_winner_full_evidence",
                  "t6_zero_residual_algebraic_winner_stale_evidence")
            print("ROOT",json.dumps({k:x[k] for k in keys},sort_keys=True))
    print("F1L_ARCHIVE_ONLY_RESIDUAL_AUDIT_PASS; 128 original parts verified; World.step=0")


if __name__=="__main__":
    main()
