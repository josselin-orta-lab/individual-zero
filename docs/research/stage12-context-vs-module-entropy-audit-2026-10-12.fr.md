# Stage 12 : deux entropies a ne pas confondre (audit du 12 octobre 2026)

**Portee : instrumentation externe uniquement.** Aucun comportement, seuil ou cout UC du runtime I0 ne change.

La specification historique v1.2.1 §16.1 et §20.3 exige la surveillance de l'occupation de S_t par module. Le depot expose aussi une mesure complementaire d'entropie des signatures contextuelles temporelles.

- `low_context_entropy` dans `stage12_lived_diagnostics_published` mesure la repetition des signatures contextuelles entre pas physiques. Son journal est limite a une fenetre temporelle, avec `None` tant que les conditions de mesure ne sont pas remplies.
- `low_entropy` dans `stage12_st_module_occupancy_published` mesure la distribution des contributions **effectivement retenues dans S_t** entre les modules producteurs, a chaque cycle, apres debit UC. `unavailable_empty_st` n'est pas un diagnostic negatif.
- Ces deux variables ne sont pas interchangeables. Une suite de contextes varies n'implique pas une occupation S_t equitable entre producteurs. Une occupation variee dans un cycle n'implique pas une diversite de contextes entre les pas.

L'auditeur independant `src/lab/stage12_occupancy_audit.py` recalculait deja la vraie occupation des modules depuis les admissions bus et les versions publiees de S_t. Il publie maintenant egalement :

- `low_entropy_positive_cycles`
- `low_entropy_negative_cycles`
- `low_entropy_unavailable_cycles`

Ces trois categories somment exactement `evaluated_cycles + deferred_cycles`, et incluent explicitement les diagnostics reportes faute de budget comme non disponibles. La classification est auditee, pas inventee a partir de l'absence d'un evenement.

**Important :** cette modification ne valide pas encore les quatre detecteurs Stage 12 ni leur couverture contrastive; la calibration du biais d'attribution (issue #110), la progression de buts, la diversite des commandes et la persistance atomique M-11/Stage 12 restent ouvertes. Les 600 pas repetant `se_deplacer` ne suffisent pas pour la reception operateur.

Avant tout changement eventuel du MVP, proposer une clarification explicite distinguant (1) la surveillance normative de l'entropie d'occupation S_t par module et (2) la mesure complementaire de diversite des signatures de contexte; le critere normatif reste celui de §16.1, sans modifier v1.3.1 directement.
