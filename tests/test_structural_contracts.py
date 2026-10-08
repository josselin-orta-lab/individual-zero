from __future__ import annotations

import unittest

from i0.config import (
    MVP_ABSTRACT_GROUPS,
    MVP_BODY_VARIABLES,
    MVP_ENTITY_TYPES,
    MVP_PRIMITIVE_ACTIONS,
    MVP_PROHIBITION_CATEGORIES,
    MVP_SIGNAL_FAMILIES,
    MVP_UNITS,
    REQUIRED_PARAMETER_IDS,
    SIMILARITY_FAMILIES,
    build_ontology_registry,
    build_parameter_registry,
    build_safety_policy,
    build_schema_registry,
    build_signal_family_registry,
    build_similarity_schema,
    build_structural_contract_bundle,
)
from lab.contracts import (
    ContractViolation,
    SchemaDefinition,
    SchemaRegistry,
)


class OntologyRegistryTests(unittest.TestCase):
    def test_normative_mvp_terms_are_present(self) -> None:
        registry = build_ontology_registry()
        identifiers = {term.identifier for term in registry.terms}

        expected = (
            set(MVP_ENTITY_TYPES)
            | set(MVP_ABSTRACT_GROUPS)
            | set(MVP_BODY_VARIABLES)
            | set(MVP_PRIMITIVE_ACTIONS)
            | set(MVP_UNITS)
        )
        self.assertTrue(expected <= identifiers)

    def test_unknown_semantic_term_is_rejected(self) -> None:
        registry = build_ontology_registry()

        with self.assertRaises(ContractViolation) as caught:
            registry.require("not_in_mvp")

        self.assertEqual(caught.exception.code, "unknown_semantic_term")

    def test_body_variables_have_normative_range(self) -> None:
        registry = build_ontology_registry()

        for identifier in MVP_BODY_VARIABLES:
            with self.subTest(identifier=identifier):
                self.assertEqual(
                    registry.require(identifier).numeric_range,
                    (0.0, 100.0),
                )


class SimilaritySchemaTests(unittest.TestCase):
    def test_schema_is_bound_to_active_ontology(self) -> None:
        ontology = build_ontology_registry()
        schema = build_similarity_schema(ontology)

        schema.validate(ontology)
        self.assertEqual(schema.families, SIMILARITY_FAMILIES)

    def test_cross_family_comparison_is_rejected(self) -> None:
        ontology = build_ontology_registry()
        schema = build_similarity_schema(ontology)

        with self.assertRaises(ContractViolation) as caught:
            schema.similarity(
                left_family="entity",
                left=(0.0, 1.0),
                right_family="episode",
                right=(0.0, 1.0),
            )

        self.assertEqual(caught.exception.code, "cross_family_similarity")

    def test_normative_metric_is_deterministic(self) -> None:
        ontology = build_ontology_registry()
        schema = build_similarity_schema(ontology)

        self.assertAlmostEqual(
            schema.similarity(
                left_family="entity",
                left=(0.0, 0.5, 1.0),
                right_family="entity",
                right=(1.0, 0.5, 0.0),
            ),
            1.0 / 3.0,
            places=15,
        )


class SignalFamilyRegistryTests(unittest.TestCase):
    def test_registry_matches_closed_normative_family_set(self) -> None:
        registry = build_signal_family_registry()

        self.assertEqual(set(registry.families), set(MVP_SIGNAL_FAMILIES))

    def test_unknown_signal_family_is_rejected(self) -> None:
        registry = build_signal_family_registry()

        with self.assertRaises(ContractViolation) as caught:
            registry.require("hidden_extra_channel")

        self.assertEqual(caught.exception.code, "unknown_signal_family")


class SafetyPolicyTests(unittest.TestCase):
    def test_policy_contains_exactly_three_normative_categories(self) -> None:
        policy = build_safety_policy()

        self.assertEqual(
            {category.identifier for category in policy.categories},
            set(MVP_PROHIBITION_CATEGORIES),
        )
        self.assertEqual(len(policy.categories), 3)
        self.assertEqual(policy.protected_integrity_parameter, "P-37")


class ParameterRegistryTests(unittest.TestCase):
    def complete_values(self) -> dict[str, object]:
        return {identifier: index for index, identifier in enumerate(REQUIRED_PARAMETER_IDS)}

    def test_all_58_parameters_are_required(self) -> None:
        values = self.complete_values()

        registry = build_parameter_registry(values)

        self.assertEqual(len(registry.values), 58)

    def test_missing_parameter_is_rejected_without_defaulting(self) -> None:
        values = self.complete_values()
        del values["P-37"]

        with self.assertRaises(ContractViolation) as caught:
            build_parameter_registry(values)

        self.assertEqual(caught.exception.code, "missing_parameter")

    def test_unknown_parameter_is_rejected(self) -> None:
        values = self.complete_values()
        values["P-59"] = 1

        with self.assertRaises(ContractViolation) as caught:
            build_parameter_registry(values)

        self.assertEqual(caught.exception.code, "unknown_parameter")


class SchemaRegistryTests(unittest.TestCase):
    def test_unknown_major_version_is_rejected(self) -> None:
        registry = build_schema_registry()
        payload = {
            field: None
            for field in registry.definition("JournalEvent").required_fields
        }

        with self.assertRaises(ContractViolation) as caught:
            registry.validate_message(
                schema_name="JournalEvent",
                schema_version="2.0",
                payload=payload,
            )

        self.assertEqual(caught.exception.code, "unknown_major_version")

    def test_unknown_causal_field_is_rejected(self) -> None:
        registry = build_schema_registry()
        schema = registry.definition("JournalEvent")
        payload = {field: None for field in schema.required_fields}
        payload["hidden_causal_input"] = 1

        with self.assertRaises(ContractViolation) as caught:
            registry.validate_message(
                schema_name="JournalEvent",
                schema_version="1.0",
                payload=payload,
            )

        self.assertEqual(caught.exception.code, "unknown_causal_field")

    def test_declared_noncausal_optional_field_may_be_ignored(self) -> None:
        registry = SchemaRegistry(
            version="fixture-v1",
            schemas=(
                SchemaDefinition(
                    name="Fixture",
                    major_version=1,
                    required_fields=("causal",),
                    ignorable_noncausal_fields=("diagnostic",),
                ),
            ),
        )

        validated = registry.validate_message(
            schema_name="Fixture",
            schema_version="1.4",
            payload={"causal": 7, "diagnostic": "wall-clock-only"},
        )

        self.assertEqual(validated, {"causal": 7})


class StructuralContractBundleTests(unittest.TestCase):
    def test_bundle_hashes_are_stable_for_same_values(self) -> None:
        values = {
            identifier: index
            for index, identifier in enumerate(REQUIRED_PARAMETER_IDS)
        }

        first = build_structural_contract_bundle(values)
        second = build_structural_contract_bundle(dict(reversed(tuple(values.items()))))

        self.assertEqual(first.ontology.digest(), second.ontology.digest())
        self.assertEqual(first.similarity.digest(), second.similarity.digest())
        self.assertEqual(first.parameters.digest(), second.parameters.digest())
        self.assertEqual(first.schemas.digest(), second.schemas.digest())


if __name__ == "__main__":
    unittest.main()
