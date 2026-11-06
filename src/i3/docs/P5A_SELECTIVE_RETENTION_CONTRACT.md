# I3 P5a: selective paid retention, development-only software contract

**Status: engineering development, NOT a preregistered held-out study.**
Source branch is a candidate under [#1026](https://github.com/josselin-orta-lab/individual-zero/issues/1026).
P3, P4a and P4b original evidence and scientific source SHAs remain immutable.
I1 remains active, I3 unregistered, all P4 reserve worlds locked.

## Falsifiable next question

P4b compared full retention of outcome updates with fully discarded updates
on a real, paid shadow computation. Its 84/288 vs 0/288 survival contrast
showed a major effect *of that combined retention intervention and its
economic/activity consequences*. The current implementation cannot say
whether learning action **effects**, TD **values** or sleep **replay** is
individually necessary. This slice adds **developer-only controls** to
examine them separately, without using P4b outcomes to tune behavior.

Four live modes are now available to development fixtures:

| Mode | Computation | Durable result |
| --- | --- | --- |
| `normal` | Original learning pipeline, fully paid | All retained |
| `discard_effects` | Original pipeline, genuinely executed and funded | Learned effect statistics restored to their prior state; TD values and replay can remain |
| `discard_values` | Original pipeline, genuinely executed and funded | TD coefficients restored to prior state; effects/buffer/replay may persist |
| `discard_replay` | Full paid base TD update plus genuinely executed replay on a detached copy | Base effects/value/buffer retained, replay's incremental changes discarded |

Legacy `shadow_discard` remains supported for reproducibility. In all
cases, prepaid sensorimotor orientation and first-person mapping remain
active; lives receive the same starting body, genome, world and nominal
per-unit energy/vigilance rates. The runtime never credits/refunds work
or invoices work it did not execute. Costs differ over time as resulting
memories, decisions and life durations diverge. **Equal realized cognition
is not claimed.**

The selective-retention counter denotes base learning pipeline executions
in all three single-component modes. It must **not** be interpreted as
proof every component was retained: that is determined by its declared
mode and separately checked before/after state invariants.

## Limits and next experimental design

Only developer/cohort `development` seeds are used in current tests, and
the original P4a/P4b full JSON bytes must match their immutable hashes.
No new validation life has been generated; no P4 reserve access is
authorized. This patch is not a claim that any of the three ablations
improves or harms survival.

Before a new scientific pilot: prospectively freeze the implementation
SHA, sample size, population-level design, new validation indices **at
least 48** within the existing 200-key validation partition, life seeds,
endpoint, expected costs and stopping logic. Keep every fixed G2 genome
from P3, not a P4a/P4b winner. State whether this is a three-arm
mechanism-screen or separate independently powered tests, and specify
corrections/interpretation for multiple comparisons. Preserve actual
per-phase receipts, idle fractions and lived time as secondary outcomes.

**Important conceptual caveat:** “discard replay” removes incremental
sleep replay retention while retaining ordinary one-step TD learning.
“Discard effects” removes the persistent effect model, not all perceived
consequences; future TD and current updates may still use momentary
effects. “Discard values” removes durable TD coefficients, not innate
projections, action-effect learning or first-person spatial beliefs.

Spatial belief learning requires its own targeted control because
those beliefs are updated during perception, separately from the
post-outcome phase. It must preserve the current observation and
sensorimotor position. It is deliberately **not** silently lumped into
these three controls.

For the stronger individuality question, create an entirely separate
**learned-history → common challenge** prospective protocol. Different
terminal memory digests in different worlds are not themselves a
behavioral demonstration. Any future such study must avoid transferring
information across births and observe individual decisions under an
identical post-history challenge, without opening P4 reserve worlds.

No scientific GO. More code is not a substitute for independent
replication.
