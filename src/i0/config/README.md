# I0 reference configuration

This directory contains configuration defining the current I0 baseline.

## Purpose

Reference configuration should make it possible to answer:

- which components are enabled;
- which implementations are selected;
- which parameters define the baseline;
- which dependency versions or modes are expected;
- which settings are scientifically meaningful.

## Behavioral parameters

A parameter change expected to alter cognitive behavior should be evaluated through an EXP before becoming part of the reference configuration.

Example:

Changing a memory-capacity parameter from 100 to 200 may alter learning and recall. If that parameter is part of reference cognition, the effect should be measured.

## Technical parameters

Purely technical changes may not require an EXP.

Example:

Changing a local log-directory path without changing execution semantics can use ordinary tests.

## Reproducibility

Experiments should record the exact reference configuration or commit used.

Avoid hidden defaults that cannot be reconstructed later.

## Future structure

Once implementation begins, prefer explicit versioned configuration files over undocumented runtime defaults.
