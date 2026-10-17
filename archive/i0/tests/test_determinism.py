from __future__ import annotations

import math
import unittest

from lab.determinism import (
    DETERMINISTIC_RUNTIME_CONTRACT,
    RandomStreamRegistry,
    RunManifest,
    StructuralContractRef,
    canonical_causal_bytes,
    derive_stream_seed,
    deterministic_id,
)


def contract(name: str, digit: str) -> StructuralContractRef:
    return StructuralContractRef(
        name=name,
        version="1",
        sha256=digit * 64,
    )


class CanonicalCausalEncodingTests(unittest.TestCase):
    def test_mapping_order_does_not_change_bytes(self) -> None:
        left = {"b": 2, "a": 1}
        right = {"a": 1, "b": 2}

        self.assertEqual(canonical_causal_bytes(left), canonical_causal_bytes(right))
        self.assertEqual(canonical_causal_bytes(left), b'{"a":1,"b":2}')

    def test_strings_are_normalized_to_nfc(self) -> None:
        composed = "é"
        decomposed = "e\u0301"

        self.assertEqual(
            canonical_causal_bytes({"value": composed}),
            canonical_causal_bytes({"value": decomposed}),
        )

    def test_float_uses_tagged_binary64_hex(self) -> None:
        self.assertEqual(
            canonical_causal_bytes({"value": 1.5}),
            b'{"value":{"$f64":"0x1.8000000000000p+0"}}',
        )
        self.assertEqual(
            canonical_causal_bytes({"value": -0.0}),
            canonical_causal_bytes({"value": 0.0}),
        )

    def test_non_finite_floats_are_rejected(self) -> None:
        for value in (math.nan, math.inf, -math.inf):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    canonical_causal_bytes({"value": value})

    def test_unordered_collections_are_rejected(self) -> None:
        with self.assertRaises(TypeError):
            canonical_causal_bytes({"values": {1, 2, 3}})

    def test_keys_colliding_after_nfc_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            canonical_causal_bytes({"é": 1, "e\u0301": 2})


class DeterministicIdentifierTests(unittest.TestCase):
    def test_same_context_produces_same_full_sha256_identifier(self) -> None:
        first = deterministic_id("journal-event-v1", "emitter", 4, 2)
        second = deterministic_id("journal-event-v1", "emitter", 4, 2)

        self.assertEqual(first, second)
        self.assertEqual(len(first), 64)

    def test_context_change_changes_identifier(self) -> None:
        self.assertNotEqual(
            deterministic_id("journal-event-v1", "emitter", 4, 2),
            deterministic_id("journal-event-v1", "emitter", 4, 3),
        )


class RandomStreamRegistryTests(unittest.TestCase):
    def test_seed_derivation_is_stable_and_stream_specific(self) -> None:
        self.assertEqual(
            derive_stream_seed(7, "world"),
            derive_stream_seed(7, "world"),
        )
        self.assertNotEqual(
            derive_stream_seed(7, "world"),
            derive_stream_seed(7, "perception"),
        )

    def test_extra_draw_in_one_stream_does_not_shift_another(self) -> None:
        baseline = RandomStreamRegistry(campaign_seed=7)
        expected = [baseline.stream("perception").random() for _ in range(4)]

        with_extra_world_draws = RandomStreamRegistry(campaign_seed=7)
        world = with_extra_world_draws.stream("world")
        for _ in range(20):
            world.random()
        actual = [
            with_extra_world_draws.stream("perception").random()
            for _ in range(4)
        ]

        self.assertEqual(actual, expected)

    def test_snapshot_restore_reproduces_exact_continuation(self) -> None:
        registry = RandomStreamRegistry(campaign_seed=11)
        stream = registry.stream("world")
        stream.random()
        states = registry.snapshot()

        expected = [stream.random() for _ in range(5)]

        restored = RandomStreamRegistry(campaign_seed=999)
        restored.restore(states)
        actual = [restored.stream("world").random() for _ in range(5)]

        self.assertEqual(actual, expected)


class RunManifestTests(unittest.TestCase):
    def make_manifest(self, contracts: tuple[StructuralContractRef, ...]) -> RunManifest:
        return RunManifest(
            specification_version="1.2.1",
            deterministic_runtime_contract=DETERMINISTIC_RUNTIME_CONTRACT,
            python_version="3.11.14",
            code_commit="abc123",
            campaign_seed=42,
            contracts=contracts,
        )

    def required_contracts(self) -> tuple[StructuralContractRef, ...]:
        return (
            contract("ontology_registry", "1"),
            contract("similarity_schema", "2"),
            contract("signal_family_registry", "3"),
            contract("safety_policy", "4"),
            contract("parameter_registry", "5"),
            contract("schema_registry", "6"),
            contract("equipment", "7"),
        )

    def test_manifest_digest_is_independent_of_contract_input_order(self) -> None:
        contracts = self.required_contracts()
        manifest_a = self.make_manifest(contracts)
        manifest_b = self.make_manifest(tuple(reversed(contracts)))

        self.assertEqual(manifest_a.canonical_bytes(), manifest_b.canonical_bytes())
        self.assertEqual(manifest_a.digest(), manifest_b.digest())

    def test_missing_required_contract_is_rejected(self) -> None:
        manifest = self.make_manifest(self.required_contracts()[:-1])

        with self.assertRaises(ValueError):
            manifest.validate()

    def test_duplicate_contract_name_is_rejected(self) -> None:
        contracts = self.required_contracts()
        duplicate = contracts + (contract("ontology_registry", "8"),)
        manifest = self.make_manifest(duplicate)

        with self.assertRaises(ValueError):
            manifest.validate()

    def test_reference_runtime_family_is_python_311(self) -> None:
        manifest = RunManifest(
            specification_version="1.2.1",
            deterministic_runtime_contract=DETERMINISTIC_RUNTIME_CONTRACT,
            python_version="3.12.0",
            code_commit="abc123",
            campaign_seed=42,
            contracts=self.required_contracts(),
        )

        with self.assertRaises(ValueError):
            manifest.validate()


if __name__ == "__main__":
    unittest.main()
