# Stage 3 technical decisions

Status: non-normative implementation note.

Normative authority remains `docs/architecture/reference/en/mvp-specification-v1.2.1.md`.

## TD-S3-01 · Avoidance-reflex tie-breaking

The normative Stage 3 requires an innate reflex that moves away from an adjacent creature, but does not fully specify how to choose among several equally valid escape directions.

The reference implementation therefore uses the following reversible deterministic rule:

1. consider only locally observed passable adjacent cells;
2. maximize the minimum **squared Euclidean distance** to all adjacent observed creatures; using the squared distance avoids any floating-point square-root operation while preserving the same ordering;
3. break remaining ties in the canonical primitive direction order already used by the MVP vocabulary: north, south, east, west.

This rule adds no learning, no value estimate, no oracle access and no hidden state. It exists only to make the mandated avoidance reflex deterministic and independently testable.

If a future normative revision specifies another exact reflex geometry or tie-break, this rule must be replaced without changing the Action Control interface.
