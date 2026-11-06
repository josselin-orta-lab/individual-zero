"""Independent read-only custody of original P5d *development-only* evidence.

Requires the first original JSON, not regenerated lives. Uses no I3 Mind,
World, generator or life runner. Negative and absent observations remain so.
"""
from __future__ import annotations

from collections import Counter, defaultdict, deque
from hashlib import sha256
import gzip
import json
from pathlib import Path
import sys

ORIGINAL_SHA256 = "3d9eff0469157cd1c9f41978720ddc61eb8b40da1c86366b3f1ed50f9823d5ec"
ORIGINAL_BYTES = 11131871
SCHEDULE_SHA256 = "710042156fb6ddb77a30b378dca1b0a51bd6ba0646a805190f83229c666d0ebd"
SCHEMA = "i3-p5d-resource-acquisition-development/v1"
MODES = ("normal", "discard_curiosity_bonus")
GENES = (901, 902)
FAMILIES = ("stable", "depletion", "pulse")
RESOURCE = ("boire", "collecter", "manger")


def _require(ok, msg):
    if not ok:
        raise ValueError("P5d custody: " + msg)


def _close(a, b):
    return abs(a - b) < 1e-7


def _digest(data):
    return sha256(json.dumps(data, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def read_raw(path):
    data = Path(path).read_bytes()
    return gzip.decompress(data) if str(path).endswith(".gz") else data


def verify_original(raw):
    _require(len(raw) == ORIGINAL_BYTES and sha256(raw).hexdigest() == ORIGINAL_SHA256,
             "original first-raw-byte digest does not match")
    return audit_payload(json.loads(raw))


def audit_payload(data):
    """Check experimental identities and receipts independently of I3 code.

    Public for adversarial synthetic mutation tests; does NOT replace the
    original-byte SHA check in verify_original.
    """
    d = data
    _require(d["schema"] == SCHEMA and
             d["status"] == "DEVELOPMENT_ONLY_NOT_HELDOUT_NOT_CAUSAL_MEDIATION",
             "schema or scientific status")
    _require(d["reserve"] == "LOCKED" and d["validation"] == "NOT_OPENED",
             "reserve/validation exposure")
    plan = dict(d["manifest"])
    original_digest = plan.pop("sha256")
    _require(original_digest == SCHEDULE_SHA256 and _digest(plan) == original_digest,
             "changed allocation or manifest digest")
    _require(plan["schema"] == SCHEMA and plan["cohort"] == "DEVELOPMENT_ONLY" and
             plan["modes"] == list(MODES) and plan["genome_seeds"] == list(GENES) and
             plan["horizon"] == 120 and plan["reserve"] == "LOCKED" and
             plan["validation"] == "NOT_OPENED", "changed plan")
    allocated = [(32 + 2 * i + j, f, 860032 + 2 * i + j)
                 for i, f in enumerate(FAMILIES) for j in (0, 1)]
    _require([(a["development_index"], a["family"], a["life_seed"])
              for a in plan["allocation"]] == allocated, "world cohort changed")
    expected = {(idx, g, m) for idx, _, _ in allocated
                for g in GENES for m in MODES}
    rows = d["receipts"]
    keys = [(r["development_index"], r["genome_seed"], r["mode"]) for r in rows]
    _require(len(rows) == len(expected) == 24 and set(keys) == expected and
             len(set(keys)) == len(keys), "incomplete/duplicate lives")
    _require(len(d["paired_chronology"]) == 12, "missing paired chronology")
    paired = defaultdict(dict)
    aggregate = {m: Counter() for m in MODES}
    life_rows = []
    for r in rows:
        idx, gene, mode = r["development_index"], r["genome_seed"], r["mode"]
        assignment = next(a for a in plan["allocation"] if a["development_index"] == idx)
        _require(r["family"] == assignment["family"] and
                 r["life_seed"] == assignment["life_seed"], "world assignment")
        paired[(idx, gene)][mode] = (r["world_sha256"], r["genome_sha256"], r["life_seed"])
        steps = r["steps"]
        _require(len(steps) == r["steps_lived"] and 1 <= len(steps) <= 120, "life length")
        _require(r["terminal"] in ("dead", "censored") and
                 ((r["terminal"] == "dead") == bool(r["death_causes"])), "terminal state")
        _require(steps[-1]["death_causes"] == r["death_causes"], "terminal cause")
        if r["terminal"] == "censored":
            _require(len(steps) == 120, "premature censored life")
        inventory = {}
        queue = defaultdict(deque)
        actions = Counter()
        paid = Counter()
        offered = scored = collect = eat = water_uptake = food_uptake = 0
        lags = []
        carrying_steps = 0
        first_collect = first_eat = first_offer = first_score = None
        for t, s in enumerate(steps, 1):
            _require(s["step"] == t and (not s["death_causes"] or t == len(steps)),
                     "discontinuous or postmortem life")
            before = dict(s["capture_inventory"])
            _require(before == inventory and all(type(n) is int and n > 0
                                                  for n in before.values()),
                     "first-person inventory balance")
            if before:
                carrying_steps += 1
            action, token = s["action"], s["param"]
            actions[action] += 1
            offered += s["resource_options_offered"]
            scored += s["resource_options_scored"]
            if first_offer is None and s["resource_options_offered"]:
                first_offer = t
            if first_score is None and s["resource_options_scored"]:
                first_score = t
            _require(s["resource_options_scored"] == len(s["paid_resource_scores"]) and
                     s["resource_options_scored"] <= s["resource_options_offered"],
                     "unpaid or fictitious resource score")
            _require(s["physical_resource_attempt"] == (action in RESOURCE) and
                     s["physical_resource_contact"] == (action in RESOURCE),
                     "resource contact mismatch")
            _require(s["collected_inventory"] == (action == "collecter") and
                     s["consumed_inventory"] == (action == "manger"),
                     "inventory flags inconsistent")
            if action in ("collecter", "manger"):
                delta = s["inventory_token_change"]
                _require(delta == (1 if action == "collecter" else -1),
                         "inventory transaction delta")
                current = inventory.get(token, 0) + delta
                _require(current >= 0, "eating missing inventory")
                if current:
                    inventory[token] = current
                else:
                    inventory.pop(token, None)
                if action == "collecter":
                    collect += 1
                    queue[token].append(t)
                    first_collect = first_collect or t
                else:
                    _require(bool(queue[token]), "eating uncollected token")
                    eat += 1
                    lags.append(t - queue[token].popleft())
                    first_eat = first_eat or t
            else:
                _require(s["inventory_token_change"] is None, "unexpected inventory transfer")
            if action == "boire":
                _require(s["positive_water_uptake"] ==
                         (s["water_uptake_above_decay"] > 1e-9), "water uptake truth")
            if action == "manger":
                _require(s["positive_food_uptake"] ==
                         (s["food_uptake_above_decay"] > 1e-9), "food uptake truth")
            water_uptake += bool(s["positive_water_uptake"])
            food_uptake += bool(s["positive_food_uptake"])
            for phase in ("decision", "learning"):
                bill = s["phase_payment"][phase]
                _require(bill["work"] == s["paid_" + phase + "_work"],
                         "work mismatch")
                if s["death_causes"] and phase == "learning":
                    _require(not any(bill["work"].values()), "postmortem learning")
                for channel in ("energy", "vigilance"):
                    charge = bill["accounting"][channel]
                    _require(charge["unpaid"] == 0 and charge["paid"] >= 0 and
                             _close(charge["requested"], charge["paid"]) and
                             _close(charge["paid"], s["paid_" + phase + "_" + channel]),
                             "unpaid or forged cognition")
                    paid[channel] += charge["paid"]
        _require(sum(inventory.values()) ==
                 sum(len(q) for q in queue.values()), "unaccounted terminal inventory")
        _require(_close(r["paid_energy"], paid["energy"]) and
                 _close(r["paid_vigilance"], paid["vigilance"]), "life cost totals")
        _require(r["summary"]["resource_options_offered"] == offered and
                 r["summary"]["resource_options_scored"] == scored and
                 r["summary"]["collected_inventory"] == collect and
                 r["summary"]["consumed_inventory"] == eat and
                 r["summary"]["positive_water_uptakes"] == water_uptake and
                 r["summary"]["positive_food_uptakes"] == food_uptake,
                 "post-life summary totals")
        aggregate[mode].update({
            "lives": 1, "alive_censored": int(r["terminal"] == "censored"),
            "deaths_water": int("zero_water" in r["death_causes"]),
            "lived_steps": len(steps),
            "voluntary_wait_steps": actions.get("attendre", 0),
            "sleep_steps": actions.get("dormir", 0),
            "movement_steps": actions.get("se_deplacer", 0),
            "motor_inactive_steps": actions.get(None, 0),
            "resource_options_offered": offered,
            "resource_options_scored": scored,
            "collections": collect, "ingestions": eat,
            "water_uptakes": water_uptake, "food_uptakes": food_uptake,
            "terminal_carried_tokens": sum(inventory.values()),
            "lives_with_terminal_inventory": int(bool(inventory)),
            "steps_carrying_inventory": carrying_steps,
            "collection_to_ingestion_transfers": len(lags),
            "collection_to_ingestion_total_lag": sum(lags),
        })
        life_rows.append({
            "development_index": idx, "genome_seed": gene, "mode": mode,
            "terminal": r["terminal"],
            "first_resource_offered": first_offer,
            "first_resource_scored": first_score,
            "first_collection": first_collect,
            "first_ingestion": first_eat,
            "collections": collect, "ingestions": eat,
            "terminal_inventory": sum(inventory.values()),
            "collection_to_ingestion_lags": lags,
        })
    for key, arm in paired.items():
        _require(set(arm) == set(MODES) and arm[MODES[0]] == arm[MODES[1]],
                 "genome/world/seed unmatched")
    for mode in MODES:
        observed = aggregate[mode]
        original = d["summary"][mode]
        _require(observed["lives"] == original["lives"] and
                 observed["alive_censored"] == original["censored_at_120"] and
                 observed["lived_steps"] == original["steps_lived"] and
                 observed["motor_inactive_steps"] == original["inactive_steps"] and
                 observed["collections"] == original["collected_inventory"] and
                 observed["water_uptakes"] == original["positive_water_uptakes"] and
                 observed["food_uptakes"] == original["positive_food_uptakes"] and
                 observed["resource_options_offered"] == original["resource_options_offered"] and
                 observed["resource_options_scored"] == original["resource_options_scored"],
                 "aggregate-vs-original summary mismatch")
    return {
        "schema": "i3-p5d-original-read-only-custody/v1",
        "status": "POSTHOC_DEVELOPMENT_ONLY_NO_NEW_LIVES",
        "original_sha256": ORIGINAL_SHA256,
        "schedule_sha256": SCHEDULE_SHA256,
        "aggregation": {m: dict(aggregate[m]) for m in MODES},
        "per_life": sorted(life_rows, key=lambda x:
                           (x["development_index"], x["genome_seed"], x["mode"])),
        "limitations": "Dependent G0 development lives; no independent evolution, no causally isolated resource choice."
    }


def main(argv):
    if len(argv) != 2:
        raise SystemExit("usage: python -m i3.lab.p5d_custody <original.json[.gz]>")
    print(json.dumps(verify_original(read_raw(argv[1])), sort_keys=True, indent=2))


if __name__ == "__main__":
    main(sys.argv)
