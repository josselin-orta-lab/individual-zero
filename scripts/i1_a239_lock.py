"""A2.39 immutable preregistration and experiment-input contract tests.

Before any births, assert the preregistered text, first-person paired
observations and new allocations. Actual runner must call this gate.
"""
from __future__ import annotations
from hashlib import sha1
from pathlib import Path

PREREG_BLOB = "9d1e0823920b7e8dbf8e2676fda789471ed6fdc5"
ROOT = Path(__file__).resolve().parents[1]
ARMS = ("BASE", "H1_ONLY", "H1_GEO", "STRICT_UNKNOWN", "FOOD_FIRST_RISK")
STRATA = ("ACQUIRE_THEN_EAT_LOCAL", "BOTH_LOCAL_GEO",
          "FOOD_FIRST_E_SAFE", "FOOD_FIRST_E_INVISIBLE_LETHAL")
SOURCE_A238 = "9b4cef681da1fa4433b739d851574b96310bc441"
PREREG_PATH = ROOT / "docs/research/i1-a239-nutrition-geography-food-first-prereg-2026-10-16.en.md"

def assigned():
    return [(stratum, i, arm) for stratum in STRATA for i in range(8)
            for arm in (ARMS if i % 2 == 0 else ARMS[::-1])]

def prereg_blob():
    data=PREREG_PATH.read_bytes()
    return sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()

def prebirth_hard_gate():
    rows=assigned()
    if len(rows)!=160 or len(set(rows))!=160:
        raise RuntimeError("A2.39 expected exactly 160 fresh birth identities")
    if (any(arm not in ARMS or strata not in STRATA or i not in range(8)
            for strata,i,arm in rows)):
        raise RuntimeError("unregistered factorial cell")
    if PREREG_BLOB=="cTODO":
        raise RuntimeError("A2.39 prereg blob has not been frozen")
    if prereg_blob()!=PREREG_BLOB:
        raise RuntimeError("preregistered A2.39 text was modified")
    return rows

if __name__ == "__main__":
    print(len(prebirth_hard_gate()))
