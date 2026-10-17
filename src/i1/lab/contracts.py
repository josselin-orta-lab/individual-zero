"""Versioned structural-contract primitives for the normative MVP.

This module contains generic validation and hashing infrastructure. I0-specific
contract contents live under i0.config.

Spec: 4.1-4.4, 5.1-5.2, 17.2, 22, INV-35, INV-51.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from .determinism import StructuralContractRef, canonical_causal_bytes, sha256_hex


class ContractViolation(ValueError):
    """Deterministic validation failure suitable for later journal logging."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message}


def _artifact_digest(payload: Mapping[str, object]) -> str:
    return sha256_hex(canonical_causal_bytes(payload))


@dataclass(frozen=True, slots=True)
class OntologyTerm:
    identifier: str
    category: str
    semantic_type: str
    semantics: str
    visibility: str
    introduced_in: str
    canonical_unit: str | None = None
    numeric_range: tuple[float, float] | None = None
    enumeration: tuple[str, ...] = ()

    def validate(self) -> None:
        if not self.identifier or not self.category or not self.semantic_type:
            raise ValueError("ontology term identifiers and types must not be empty")
        if not self.semantics or not self.introduced_in:
            raise ValueError("ontology term semantics and introduction version are required")
        if self.visibility not in {"world_only", "observable", "derived"}:
            raise ValueError("invalid ontology visibility class")
        if self.numeric_range is not None:
            lower, upper = self.numeric_range
            if lower > upper:
                raise ValueError("ontology numeric range must be ordered")
        if len(self.enumeration) != len(set(self.enumeration)):
            raise ValueError("ontology enumeration values must be unique")

    def as_dict(self) -> dict[str, object]:
        return {
            "identifier": self.identifier,
            "category": self.category,
            "semantic_type": self.semantic_type,
            "semantics": self.semantics,
            "visibility": self.visibility,
            "introduced_in": self.introduced_in,
            "canonical_unit": self.canonical_unit,
            "numeric_range": self.numeric_range,
            "enumeration": list(self.enumeration),
        }


@dataclass(frozen=True, slots=True)
class OntologyRegistry:
    version: str
    terms: tuple[OntologyTerm, ...]

    def validate(self) -> None:
        if not self.version:
            raise ValueError("ontology version must not be empty")
        identifiers: list[str] = []
        for term in self.terms:
            term.validate()
            identifiers.append(term.identifier)
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("ontology term identifiers must be unique")

    def as_dict(self) -> dict[str, object]:
        self.validate()
        return {
            "version": self.version,
            "terms": [
                term.as_dict()
                for term in sorted(self.terms, key=lambda item: item.identifier)
            ],
        }

    def digest(self) -> str:
        return _artifact_digest(self.as_dict())

    def require(self, identifier: str) -> OntologyTerm:
        for term in self.terms:
            if term.identifier == identifier:
                return term
        raise ContractViolation(
            "unknown_semantic_term",
            f"semantic term is absent from active ontology: {identifier}",
        )

    def require_all(self, identifiers: Sequence[str]) -> None:
        for identifier in identifiers:
            self.require(identifier)


@dataclass(frozen=True, slots=True)
class SimilaritySchema:
    version: str
    ontology_sha256: str
    families: tuple[str, ...]
    metric: str
    categorical_encoding: str
    boolean_encoding: str
    numeric_encoding: str
    optional_encoding: str
    collection_encoding: str

    def validate(self, ontology: OntologyRegistry) -> None:
        if not self.version:
            raise ValueError("similarity schema version must not be empty")
        if self.ontology_sha256 != ontology.digest():
            raise ValueError("similarity schema ontology hash mismatch")
        if len(self.families) != len(set(self.families)):
            raise ValueError("similarity families must be unique")

    def as_dict(self) -> dict[str, object]:
        return {
            "version": self.version,
            "ontology_sha256": self.ontology_sha256,
            "families": list(self.families),
            "metric": self.metric,
            "categorical_encoding": self.categorical_encoding,
            "boolean_encoding": self.boolean_encoding,
            "numeric_encoding": self.numeric_encoding,
            "optional_encoding": self.optional_encoding,
            "collection_encoding": self.collection_encoding,
        }

    def digest(self) -> str:
        return _artifact_digest(self.as_dict())

    def similarity(
        self,
        *,
        left_family: str,
        left: Sequence[float],
        right_family: str,
        right: Sequence[float],
    ) -> float:
        if left_family != right_family:
            raise ContractViolation(
                "cross_family_similarity",
                "similarity comparison across families is forbidden",
            )
        if left_family not in self.families:
            raise ContractViolation(
                "unknown_similarity_family",
                f"unknown similarity family: {left_family}",
            )
        if len(left) != len(right):
            raise ContractViolation(
                "similarity_dimension_mismatch",
                "vectors must have identical dimension counts",
            )
        if not left:
            raise ContractViolation(
                "empty_similarity_vector",
                "similarity vectors must not be empty",
            )

        total = 0.0
        for left_value, right_value in zip(left, right):
            if not 0.0 <= left_value <= 1.0 or not 0.0 <= right_value <= 1.0:
                raise ContractViolation(
                    "similarity_value_out_of_range",
                    "normalized similarity dimensions must be in [0,1]",
                )
            total += abs(left_value - right_value)

        return max(0.0, min(1.0, 1.0 - total / len(left)))


@dataclass(frozen=True, slots=True)
class SignalFamilyRegistry:
    version: str
    families: tuple[str, ...]

    def validate(self) -> None:
        if not self.version:
            raise ValueError("signal-family registry version must not be empty")
        if not self.families or len(self.families) != len(set(self.families)):
            raise ValueError("signal-family registry must contain unique families")

    def as_dict(self) -> dict[str, object]:
        self.validate()
        return {"version": self.version, "families": sorted(self.families)}

    def digest(self) -> str:
        return _artifact_digest(self.as_dict())

    def require(self, family: str) -> None:
        if family not in self.families:
            raise ContractViolation(
                "unknown_signal_family",
                f"signal family is absent from active registry: {family}",
            )


@dataclass(frozen=True, slots=True)
class ProhibitionCategory:
    identifier: str
    semantics: str

    def validate(self) -> None:
        if not self.identifier or not self.semantics:
            raise ValueError("prohibition category id and semantics are required")

    def as_dict(self) -> dict[str, str]:
        return {"identifier": self.identifier, "semantics": self.semantics}


@dataclass(frozen=True, slots=True)
class SafetyPolicy:
    version: str
    categories: tuple[ProhibitionCategory, ...]
    protected_integrity_parameter: str = "P-37"

    def validate(self) -> None:
        if not self.version:
            raise ValueError("safety policy version must not be empty")
        identifiers: list[str] = []
        for category in self.categories:
            category.validate()
            identifiers.append(category.identifier)
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("safety prohibition categories must be unique")
        if self.protected_integrity_parameter != "P-37":
            raise ValueError("MVP protected integrity threshold is parameter P-37")

    def as_dict(self) -> dict[str, object]:
        self.validate()
        return {
            "version": self.version,
            "categories": [
                category.as_dict()
                for category in sorted(self.categories, key=lambda item: item.identifier)
            ],
            "protected_integrity_parameter": self.protected_integrity_parameter,
        }

    def digest(self) -> str:
        return _artifact_digest(self.as_dict())


@dataclass(frozen=True, slots=True)
class ParameterValue:
    identifier: str
    value: object

    def validate(self) -> None:
        if not self.identifier:
            raise ValueError("parameter identifier must not be empty")
        canonical_causal_bytes(self.value)

    def as_dict(self) -> dict[str, object]:
        return {"identifier": self.identifier, "value": self.value}


@dataclass(frozen=True, slots=True)
class ParameterRegistry:
    version: str
    values: tuple[ParameterValue, ...]

    def validate(self, *, required_ids: Sequence[str]) -> None:
        if not self.version:
            raise ValueError("parameter registry version must not be empty")
        identifiers: list[str] = []
        for parameter in self.values:
            parameter.validate()
            identifiers.append(parameter.identifier)
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("parameter identifiers must be unique")

        actual = set(identifiers)
        required = set(required_ids)
        missing = sorted(required - actual)
        extra = sorted(actual - required)
        if missing:
            raise ContractViolation(
                "missing_parameter",
                "missing required parameters: " + ", ".join(missing),
            )
        if extra:
            raise ContractViolation(
                "unknown_parameter",
                "parameters absent from normative registry: " + ", ".join(extra),
            )

    def as_dict(self) -> dict[str, object]:
        return {
            "version": self.version,
            "values": [
                parameter.as_dict()
                for parameter in sorted(self.values, key=lambda item: item.identifier)
            ],
        }

    def digest(self) -> str:
        return _artifact_digest(self.as_dict())


@dataclass(frozen=True, slots=True)
class SchemaDefinition:
    name: str
    major_version: int
    required_fields: tuple[str, ...]
    optional_causal_fields: tuple[str, ...] = ()
    ignorable_noncausal_fields: tuple[str, ...] = ()

    def validate(self) -> None:
        if not self.name:
            raise ValueError("schema name must not be empty")
        if self.major_version < 0:
            raise ValueError("schema major version must be non-negative")
        required = set(self.required_fields)
        optional = set(self.optional_causal_fields)
        noncausal = set(self.ignorable_noncausal_fields)
        if len(required) != len(self.required_fields):
            raise ValueError("required schema fields must be unique")
        if len(optional) != len(self.optional_causal_fields):
            raise ValueError("optional causal schema fields must be unique")
        if len(noncausal) != len(self.ignorable_noncausal_fields):
            raise ValueError("ignorable non-causal schema fields must be unique")
        if required & optional or required & noncausal or optional & noncausal:
            raise ValueError("schema field classes must be disjoint")

    def as_dict(self) -> dict[str, object]:
        self.validate()
        return {
            "name": self.name,
            "major_version": self.major_version,
            "required_fields": sorted(self.required_fields),
            "optional_causal_fields": sorted(self.optional_causal_fields),
            "ignorable_noncausal_fields": sorted(self.ignorable_noncausal_fields),
        }


@dataclass(frozen=True, slots=True)
class SchemaRegistry:
    version: str
    schemas: tuple[SchemaDefinition, ...]

    def validate(self) -> None:
        if not self.version:
            raise ValueError("schema registry version must not be empty")
        names: list[str] = []
        for schema in self.schemas:
            schema.validate()
            names.append(schema.name)
        if len(names) != len(set(names)):
            raise ValueError("schema names must be unique")

    def as_dict(self) -> dict[str, object]:
        self.validate()
        return {
            "version": self.version,
            "schemas": [
                schema.as_dict()
                for schema in sorted(self.schemas, key=lambda item: item.name)
            ],
        }

    def digest(self) -> str:
        return _artifact_digest(self.as_dict())

    def definition(self, name: str) -> SchemaDefinition:
        for schema in self.schemas:
            if schema.name == name:
                return schema
        raise ContractViolation("unknown_schema", f"unknown schema: {name}")

    def validate_message(
        self,
        *,
        schema_name: str,
        schema_version: str,
        payload: Mapping[str, object],
    ) -> dict[str, object]:
        schema = self.definition(schema_name)
        try:
            major_text = schema_version.split(".", 1)[0]
            major = int(major_text)
        except (AttributeError, ValueError) as exc:
            raise ContractViolation(
                "invalid_schema_version",
                f"invalid schema version: {schema_version!r}",
            ) from exc

        if major != schema.major_version:
            raise ContractViolation(
                "unknown_major_version",
                f"schema {schema_name} does not support major version {major}",
            )

        fields = set(payload)
        required = set(schema.required_fields)
        optional = set(schema.optional_causal_fields)
        noncausal = set(schema.ignorable_noncausal_fields)
        missing = sorted(required - fields)
        if missing:
            raise ContractViolation(
                "missing_required_field",
                "missing required fields: " + ", ".join(missing),
            )

        unknown = sorted(fields - required - optional - noncausal)
        if unknown:
            raise ContractViolation(
                "unknown_causal_field",
                "unknown causal fields: " + ", ".join(unknown),
            )

        return {
            key: payload[key]
            for key in sorted(fields - noncausal)
        }


@dataclass(frozen=True, slots=True)
class StructuralContractBundle:
    ontology: OntologyRegistry
    similarity: SimilaritySchema
    signal_families: SignalFamilyRegistry
    safety_policy: SafetyPolicy
    parameters: ParameterRegistry
    schemas: SchemaRegistry
    required_parameter_ids: tuple[str, ...]

    def validate(self) -> None:
        self.ontology.validate()
        self.similarity.validate(self.ontology)
        self.signal_families.validate()
        self.safety_policy.validate()
        self.parameters.validate(required_ids=self.required_parameter_ids)
        self.schemas.validate()

    def contract_refs(
        self,
        *,
        equipment: StructuralContractRef,
    ) -> tuple[StructuralContractRef, ...]:
        self.validate()
        equipment.validate()
        if equipment.name != "equipment":
            raise ValueError("equipment contract ref must use name 'equipment'")
        return (
            StructuralContractRef(
                name="ontology_registry",
                version=self.ontology.version,
                sha256=self.ontology.digest(),
            ),
            StructuralContractRef(
                name="similarity_schema",
                version=self.similarity.version,
                sha256=self.similarity.digest(),
            ),
            StructuralContractRef(
                name="signal_family_registry",
                version=self.signal_families.version,
                sha256=self.signal_families.digest(),
            ),
            StructuralContractRef(
                name="safety_policy",
                version=self.safety_policy.version,
                sha256=self.safety_policy.digest(),
            ),
            StructuralContractRef(
                name="parameter_registry",
                version=self.parameters.version,
                sha256=self.parameters.digest(),
            ),
            StructuralContractRef(
                name="schema_registry",
                version=self.schemas.version,
                sha256=self.schemas.digest(),
            ),
            equipment,
        )
