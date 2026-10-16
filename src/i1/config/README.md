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

## Current normative structural contracts

The first MVP v1.2.1 implementation layer now defines structural contracts in `contracts.py`.

It currently provides:

- the closed MVP ontology registry;
- the deterministic similarity-schema contract;
- the closed κ signal-family registry;
- the three-category MVP safety policy;
- the schema compatibility registry for Stage 1 message types;
- the normative set of parameter identifiers P-01 through P-58;
- builders that require campaign parameter values to be supplied explicitly.

No P-xx numerical value is invented here. A complete parameter registry can only be built when all 58 values have been explicitly supplied by preregistration/calibration.

These artifacts are versioned and hashable. Their hashes are intended to enter the causal run manifest before execution.

## Placement rule

Generic loading, hashing, compatibility validation, and deterministic rejection belong in `lab`.

The concrete normative I0 vocabulary, schema set, signal families, safety categories, and parameter identifiers belong here because they define the reference I0 contract.

Do not move cognitive state or cognitive policy into this directory merely because it is configurable.
