# Native I2: committed source discovery after uncertain exploration

This experiment extends ADR-0009 / issue #888 and builds on PR #899.

A bounded native individual may consider `collecter` only after revising a
failed vital strategy from its own committed experiences. The existing paid
Competition and fresh safety review may admit the physical collection,
which has its ordinary energy and metabolic costs. The born environment has
a locked `discovered_water_gain` parameter. Until a collection has actually
been admitted and committed, that hidden parameter is **never exposed to
the individual's observation or valuation**.

After an admitted collection, the same existing SQLite transaction records
one source-discovery event with the committed physical hash, recording either
found=1 or found=0. At the next capture only, a found source yields the
`boire_decouverte` affordance, with a strictly single-use resource count,
and an evidence reference bound to its discovery sequence. A discovered
drink still requires its own paid Competition and fresh action admission.
Its water gain is physically applied only after that subsequent action.
The previous failed drinking source and the newly discovered water have
different semantic labels, so the older aversive history is not silently
transferred to the new resource. No independent world or memory owner was
created.

The native cold audit recalculates source discovery from the original
birth-locked physical condition, verifies its exact same-COMMIT physical
event hash, checks that a future source was not offered prematurely,
enforces resource exhaustion, and rejects a forged or missing discovery.
Tests cover positive discovery, genuinely empty exploration, next-capture
availability and fabricated positive discovery.

The initial implementation has one hidden source with a static result
parameter and one possible discovery. It does not establish adaptive
survival, geographical search, a generalized learning algorithm,
autonomous living actuation, independent M11 custody or I1 physical parity.
Do not claim scientific superiority from a successful bounded software
example. Keep explicit no-learning and nonrestoring controls.
