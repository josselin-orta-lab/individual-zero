# I1 architecture and ownership

I1 is the active embodied individual. It is not an incremental patch to a
shared mutable I0 Lab.

| Layer | Owned source | Execution surface |
| --- | --- | --- |
| Cognitive contracts and mechanisms | `src/i1/modules/`, `src/i1/config/` | `i1.modules.*` |
| I1 Lab and technical orchestration | `src/i1/lab/` | currently `i1lab.*` |
| Natural birth, body and journals | `src/i1/runtime/` | currently `i1lab.*` |
| Generation interface obligations | `src/i1/engine.json` | verified at CI, not injected into cognition |
| Historical I0 and Lab | `src/i0/`, `archive/i0/lab/` | immutable; independent legacy tests |

The transitional builder copies the I1 Lab and native I1 runtime into a
disposable `i1lab` namespace; its output is not an independent living
individual, nor a source of scientific truth. I1 natural birth uses explicit
physical and cognitive configuration. M11 owns an authenticated current
generation and rejects any uncertain transaction. Do not detach an already
living individual into a previous generation.

**Data boundary:** perception and causal learning use lived observations,
not privileged environment truth. The Lab may audit privately but must never
inject results into the individual's subjective state. Scientific evaluators,
test fixtures and H1/H2 historical cohorts do not determine current I1 policy.

**Change boundary:** modify only the affected generation, its contract,
its per-generation Lab and tests. Preserve I0 and archived blob/tree SHA.
Read the registry to resolve ownership before editing. Future I2 must never
import I1's Lab as its mutable runtime.
