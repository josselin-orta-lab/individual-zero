# I2 native comparability baseline, 2 November 2026

**Engineering stage 1 only, not full physiological parity.** I1 reference: `src/i1/runtime/world.py`, `src/i1/runtime/i1_natural_sleep.py`, `src/i1/temperament.py`, `src/i1/runtime/i1_birth_temperament.py`. I2 implementation is original and cannot import any I1 runtime or life state.

- Four channels `energy/food/water/integrity`, each bounded [0,100].
- Existing I1 v4 default per-step `food -0.20`, `water -0.40`, action energy costs `move 2, collect 1, eat 0.5, drink 0.5, place stone 1.5, craft 1.5, sleep 0.25 nominal but sleep uses +3 instead, wait 0.35`.
- Energy restored by sleep at most 3, only with water after decay >=0.05 and with `0.05` food consumed per restored energy unit. Rest/wait integrity repair at most 0.20 and `0.10` food per integrity point, only when hydrated. Water has **no direct calorie energy bonus**.
- Normal I1 v4 terminal when `food==0`, `water==0`, or `integrity==0` after the actual effect. No stand-alone zero-energy death in I1's v4 WorldBody contract.
- Five temperament raw coordinates: `reward_sensitivity`, `threat_sensitivity`, `exploration`, `goal_protection`, `affiliation`, bounded [-1,1]. I1 derives them at birth and projects them into Value/Needs, Competition, Gatekeeper, Stage8. I2's first tranche freezes values but **does not yet use them in cognition**, thus is NOT behaviorally comparable.
- I1's actual world has 32x32 movement, location-dependent drink/collect, different berry species, hazards and Stage10 fatigue/sleep; the pure I2 first tranche **does not** claim positional/resource or fatigue parity and must never be used as an alternative motor owner.
- Effective I1 configuration can preserve world-specific overrides; for parity fix exact effective configuration rather than assuming these fallback constants apply to every world.
- An independent same-action physical tape with truly matched configuration is a prerequisite for a valid head-to-head cognition study, never evidence that two free policies learn equally.

**Current source:** `src/i2/modules/native_body_contract.py` and `src/i2/modules/native_birth_temperament.py`. Targeted test: `python -m unittest discover -s tests/i2 -p test_native_body_temperament_contract_888.py -v`. These are deliberately unconnected to the historical I2 SQLite experimental owner. Do not silently reinterpret prior water-energy smokes as I1 parity. See [ADR-0009](../../../docs/decisions/ADR-0009-i2-physiology-temperament-parity.md).
