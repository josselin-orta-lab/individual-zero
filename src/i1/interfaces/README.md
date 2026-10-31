# I1 interfaces: source ownership and historical context

This directory contains minimal interfaces under core.py (Observation, Action, PrimitiveCommand, StepResult and Individual) with historical bootstrap-oriented descriptions. Their presence **does not mean** that the natural I1 runtime follows the old I0 bootstrap protocol as its canonical motor contract.

For the actual active I1 execution, use [engine.json](../engine.json), [cognitive flow](../docs/COGNITIVE_FLOW.md), [Stage handoffs](../docs/STAGES_AND_INTERFACES.md), and the source defining the affected interface and owner. Check the method's actual runtime caller, the first-person observation boundary, Action Control and M11 before changing a shared type.

An interface should clarify ownership, provenance and replaceability, not silently add cognitive policy, inherited runtime state, legacy fallback or unearned world knowledge. See [ADR-0001](../../../docs/decisions/ADR-0001-strict-generation-autonomy.md) and [adapter example](../../../examples/adapter-example.md).
