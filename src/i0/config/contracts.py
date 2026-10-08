"""Normative structural-contract contents for I0 MVP v1.2.1.

These are structural identifiers and schemas, not cognitive behavior and not
calibrated P-xx values.

Spec: 4.1-4.4, 5.2, 9.3, 17.2, 22, DC-06, INV-35, INV-51.
"""

from __future__ import annotations

from lab.contracts import (
    OntologyRegistry,
    OntologyTerm,
    ProhibitionCategory,
    SafetyPolicy,
    SchemaDefinition,
    SchemaRegistry,
    SignalFamilyRegistry,
    SimilaritySchema,
    StructuralContractBundle,
)


SPECIFICATION_VERSION = "1.2.1"
STRUCTURAL_CONTRACT_VERSION = "mvp-v1.2.1"

REQUIRED_PARAMETER_IDS = tuple(f"P-{index:02d}" for index in range(1, 59))

MVP_ENTITY_TYPES = (
    "individual",
    "water_source",
    "berry",
    "stone",
    "wood",
    "creature",
    "shelter",
    "zone",
    "crafted_object",
    "tool",
)

MVP_ABSTRACT_GROUPS = ("resource", "structure", "external_agent")
MVP_BODY_VARIABLES = ("energy", "food", "water", "integrity")
MVP_UNITS = ("pas", "cycle", "jour", "UC")
MVP_PRIMITIVE_ACTIONS = (
    "se_deplacer",
    "collecter",
    "manger",
    "boire",
    "poser_une_pierre",
    "fabriquer_outil",
    "dormir",
    "attendre",
)
MVP_MOVE_DIRECTIONS = ("north", "south", "east", "west")

MVP_SIGNAL_FAMILIES = (
    "world_symbolic",
    "body_telemetry",
    "equipment_predictor",
    "agency_comparator",
    "memory_recall",
    "value_needs",
    "goal_management",
    "causal_model",
    "exploration",
    "planning",
    "metacognition",
)

MVP_PROHIBITION_CATEGORIES = (
    "lethal_zone_movement",
    "toxic_item_consumption",
    "protected_invariant_violation",
)

SIMILARITY_FAMILIES = ("entity", "situation", "episode")

MVP_PHASE1_PRODUCER_ORDER = (
    "perception",
    "value_needs",
    "memory",
    "goal_manager",
    "causal_model",
    "exploration",
    "planning",
    "metacognition_health",
)

MVP_CYCLE_PHASE_COMPONENT_ORDER = {
    0: ("global_modulation",),
    1: MVP_PHASE1_PRODUCER_ORDER + ("bus",),
    2: ("gatekeeper",),
    3: ("competition",),
    4: ("competition", "action_control"),
    5: (
        "metacognition_health",
        "causal_model",
        "perception",
        "journal",
    ),
}


def build_ontology_registry() -> OntologyRegistry:
    terms: list[OntologyTerm] = []

    for identifier in MVP_ENTITY_TYPES:
        terms.append(
            OntologyTerm(
                identifier=identifier,
                category="entity_type",
                semantic_type="entity_type",
                semantics=f"MVP entity type: {identifier}",
                visibility="observable",
                introduced_in=SPECIFICATION_VERSION,
            )
        )

    for identifier in MVP_ABSTRACT_GROUPS:
        terms.append(
            OntologyTerm(
                identifier=identifier,
                category="abstract_group",
                semantic_type="entity_group",
                semantics=f"MVP abstract ontology grouping: {identifier}",
                visibility="derived",
                introduced_in=SPECIFICATION_VERSION,
            )
        )

    for identifier in MVP_BODY_VARIABLES:
        terms.append(
            OntologyTerm(
                identifier=identifier,
                category="body_variable",
                semantic_type="measurable_variable",
                semantics=f"MVP body variable: {identifier}",
                visibility="observable",
                introduced_in=SPECIFICATION_VERSION,
                numeric_range=(0.0, 100.0),
            )
        )

    for identifier in MVP_UNITS:
        terms.append(
            OntologyTerm(
                identifier=identifier,
                category="unit",
                semantic_type="unit",
                semantics=f"Normative MVP unit: {identifier}",
                visibility="derived",
                introduced_in=SPECIFICATION_VERSION,
            )
        )

    for identifier in MVP_PRIMITIVE_ACTIONS:
        enumeration = MVP_MOVE_DIRECTIONS if identifier == "se_deplacer" else ()
        terms.append(
            OntologyTerm(
                identifier=identifier,
                category="primitive_action",
                semantic_type="action",
                semantics=f"MVP primitive action: {identifier}",
                visibility="derived",
                introduced_in=SPECIFICATION_VERSION,
                enumeration=enumeration,
            )
        )

    return OntologyRegistry(
        version=STRUCTURAL_CONTRACT_VERSION,
        terms=tuple(terms),
    )


def build_similarity_schema(ontology: OntologyRegistry) -> SimilaritySchema:
    return SimilaritySchema(
        version=STRUCTURAL_CONTRACT_VERSION,
        ontology_sha256=ontology.digest(),
        families=SIMILARITY_FAMILIES,
        metric="1-mean-absolute-distance",
        categorical_encoding="one-hot/canonical-enumeration-order",
        boolean_encoding="0-or-1",
        numeric_encoding="affine-[0,1]-declared-finite-range",
        optional_encoding="presence-bit-then-value",
        collection_encoding="per-category-count/canonical-order/declared-max",
    )


def build_signal_family_registry() -> SignalFamilyRegistry:
    return SignalFamilyRegistry(
        version=STRUCTURAL_CONTRACT_VERSION,
        families=MVP_SIGNAL_FAMILIES,
    )


def build_safety_policy() -> SafetyPolicy:
    return SafetyPolicy(
        version=STRUCTURAL_CONTRACT_VERSION,
        categories=(
            ProhibitionCategory(
                identifier="lethal_zone_movement",
                semantics="movement into a zone established as lethal",
            ),
            ProhibitionCategory(
                identifier="toxic_item_consumption",
                semantics="consumption of an item established as toxic",
            ),
            ProhibitionCategory(
                identifier="protected_invariant_violation",
                semantics=(
                    "command with a sufficiently established consequence that "
                    "violates a protected invariant"
                ),
            ),
        ),
        protected_integrity_parameter="P-37",
    )


def build_parameter_registry(values: dict[str, object]):
    """Build a complete campaign parameter registry without inventing values.

    The caller must supply all P-01 through P-58. Missing or additional ids are
    rejected by the generic registry validator.
    """

    from lab.contracts import ParameterRegistry, ParameterValue

    registry = ParameterRegistry(
        version=STRUCTURAL_CONTRACT_VERSION,
        values=tuple(
            ParameterValue(identifier=identifier, value=value)
            for identifier, value in sorted(values.items())
        ),
    )
    registry.validate(required_ids=REQUIRED_PARAMETER_IDS)
    return registry


def build_structural_contract_bundle(values: dict[str, object]) -> StructuralContractBundle:
    """Build and validate the frozen I0 structural-contract bundle."""

    ontology = build_ontology_registry()
    bundle = StructuralContractBundle(
        ontology=ontology,
        similarity=build_similarity_schema(ontology),
        signal_families=build_signal_family_registry(),
        safety_policy=build_safety_policy(),
        parameters=build_parameter_registry(values),
        schemas=build_schema_registry(),
        required_parameter_ids=REQUIRED_PARAMETER_IDS,
    )
    bundle.validate()
    return bundle


def build_schema_registry() -> SchemaRegistry:
    """Return Stage-1 schemas whose field sets are fixed by sections 4 and 5.

    Nested payload semantics are validated by later component-specific
    validators. This registry closes top-level compatibility behavior now.
    """

    return SchemaRegistry(
        version=STRUCTURAL_CONTRACT_VERSION,
        schemas=(
            SchemaDefinition(
                name="Contribution",
                major_version=1,
                required_fields=(
                    "id",
                    "version_schema",
                    "type",
                    "resume",
                    "charge",
                    "subject_ref",
                    "references_secondaires",
                    "confiance",
                    "urgence",
                    "risque",
                    "valeur",
                    "cout",
                    "provenance",
                    "horodatage",
                    "validite",
                    "liens",
                    "degrade",
                    "empreinte",
                ),
            ),
            SchemaDefinition(
                name="Requete",
                major_version=1,
                required_fields=(
                    "id",
                    "individu",
                    "emetteur",
                    "destinataire",
                    "question",
                    "contexte",
                    "budget",
                    "echeance",
                    "format_attendu",
                    "profondeur",
                    "racine_ref",
                ),
                optional_causal_fields=("parent_ref",),
            ),
            SchemaDefinition(
                name="Reponse",
                major_version=1,
                required_fields=(
                    "request_ref",
                    "statut",
                    "partageable",
                    "t_monde_production",
                ),
                optional_causal_fields=(
                    "contenu",
                    "motif_refus",
                    "validite",
                ),
            ),
            SchemaDefinition(
                name="JournalEvent",
                major_version=1,
                required_fields=(
                    "n",
                    "type",
                    "charge",
                    "provenance",
                    "emp_prec",
                    "emp",
                ),
                optional_causal_fields=(
                    "t_monde",
                    "cycle",
                    "attempt_ref",
                    "individu",
                ),
            ),
            SchemaDefinition(
                name="Snapshot",
                major_version=1,
                required_fields=(
                    "id",
                    "type",
                    "individu",
                    "t_monde",
                    "cycle",
                    "etat_causal_complet",
                    "versions",
                    "empreinte",
                ),
                optional_causal_fields=(
                    "attempt_ref",
                    "etat_scenario_causal",
                ),
            ),
        ),
    )
