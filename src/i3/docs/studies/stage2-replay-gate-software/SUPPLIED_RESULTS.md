# Supplied Stage 2.1 software falsifier result

**SUPPLIED RESULT, PRESERVED FOR CUSTODY. NOT THE CANONICAL FROZEN-PROTOCOL
VERDICT.**

The uploaded development package reports `REPLAY_GATE_CAPACITY_SHOWN` from a
single execution at 08:20:33 UTC on 9 November 2026, from supplied commit
`0442ea9fb723cbf6895a9fd3de5339739b2c2d55`.

Reported rules:

| Rule | Supplied observation |
| --- | --- |
| R0 | 40 decision states identical to P1.3; paid audit; token renaming invariant |
| R1 | forced-open equals FIXED in all 32 sleep fixtures |
| R2 | S0: 0 replays in all 16 bodies; S1: 16 replays in high-E/V bodies |
| R3 | 84/84 ordered pairs non-increasing, but 16 replays in every S1 body |
| R4 | gate overhead 1 cycle + 2 simulations; audit <= 1 cycle |

The package itself notes that R3 is vacuous: replay cost never binds in the S1
software fixtures. It also reports no World, life or runtime registration for
this software execution.

Repository audit additionally found that this run used
`(relevant+1)/(audited+2)` instead of the frozen
`(relevant+1)/(decisions+2)`. Therefore the result is retained as supplied
evidence but is superseded for decision-making by [RESULTS.md](RESULTS.md).
