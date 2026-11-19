"""Stage8-E2 independent shape gate for *decoded* parental native life records.

No synthetic score may pass as a real sealed archive: this reducer accepts
only records after a future independent gzip SHA+source+World+body verifier.
The caller is responsible for that prior audit. Here we enforce six
opportunities per genome and preserve deaths, including death at horizon.
"""
from __future__ import annotations

SCHEMA = "i3-stage8e2-parent-fitness-from-audited-lives/v0"
FAMILIES = ("stable", "depletion", "pulse")


def summarize_authenticated_lives(rows: list[dict], generation: int) -> dict:
    """Aggregate exactly six first-person native lives per parental genotype.

    This is NOT an original-gzip auditor or source/receipt validation.
    Future runner MUST supply verified originals only, never aggregates.
    """
    if type(generation) is not int or generation not in (0, 1):
        raise ValueError("parents can only be in G0 or G1")
    arms = ("shared",) if generation == 0 else ("S", "M")
    expected = {(p, arm, slot, family, repeat)
                for p in range(64) for arm in arms for slot in range(24)
                for family in FAMILIES for repeat in range(2)}
    if type(rows) is not list or len(rows) != len(expected):
        raise ValueError("incorrect original parental life count")
    seen, sums = set(), {}
    for r in rows:
        if type(r) is not dict or set(r) != {
                "population", "generation", "arm", "slot", "family",
                "repeat", "steps_lived", "terminal"}:
            raise ValueError("decoded original identity/terminal row invalid")
        key = (r["population"], r["arm"], r["slot"], r["family"], r["repeat"])
        if (r["generation"] != generation or key not in expected or key in seen
                or type(r["steps_lived"]) is not int
                or not 1 <= r["steps_lived"] <= 400
                or r["terminal"] not in ("dead", "censored")):
            raise ValueError("duplicate, impossible or foreign native life")
        if r["terminal"] == "censored" and r["steps_lived"] != 400:
            raise ValueError("premature censoring cannot be scored as survival")
        seen.add(key)
        parent = key[:3]
        cell = sums.setdefault(parent, [0, 0, 0])
        cell[0] += int(r["terminal"] == "censored")
        cell[1] += r["steps_lived"]
        cell[2] += 1
    if seen != expected or any(v[2] != 6 for v in sums.values()):
        raise ValueError("not all six F0 opportunities present")
    return {key: (v[0], v[1]) for key, v in sums.items()}
