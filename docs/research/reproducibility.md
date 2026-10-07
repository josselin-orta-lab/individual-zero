# Reproducibility

Reproducibility is a project property, not just an experiment checkbox.

The goal is not to guarantee perfect bit-for-bit identity in every environment. The goal is to preserve enough information that another contributor can reconstruct the tested conditions and understand deviations.

## Minimum experiment record

A real EXP should capture, when relevant:

- repository commit;
- configuration;
- dependency versions;
- random seeds;
- environment or simulator version;
- input data or generation procedure;
- metrics;
- exact launch command;
- location and format of result artifacts.

## Seeds

If stochastic behavior matters, record seeds explicitly.

When using several seeds, document:

- the seed list or generation rule;
- aggregation method;
- exclusions, if any.

Do not silently rerun until a preferred outcome appears.

## Dependencies

Pin versions when a dependency can influence results.

For external research projects, also preserve:

- upstream repository or package;
- exact version or commit;
- relevant local adapter version;
- license.

## Configuration

Reference defaults should be explicit.

An EXP should not depend on an undocumented local configuration file that cannot be reconstructed.

## Data

Do not commit private, restricted, or non-redistributable data merely to make an EXP convenient.

Document provenance and access conditions.

If data can be generated deterministically, preserving the generator and seed may be preferable to storing a large dataset.

## Artifacts

Keep artifacts that are necessary to:

- verify the reported result;
- inspect important anomalies;
- reproduce derived metrics;
- understand a decision.

Avoid storing large disposable outputs that can be regenerated cheaply.

## Hardware and timing

If timing or hardware affects behavior, document it.

If hardware is irrelevant to the claim, do not add unnecessary hardware requirements to the protocol.

## Reproduction failures

A failed reproduction is useful information.

Document whether the failure appears to come from:

- environment drift;
- missing dependency information;
- nondeterminism;
- an actual contradiction of the original result.

Reproducibility problems can become research or infrastructure Issues in their own right.
