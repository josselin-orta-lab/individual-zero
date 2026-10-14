# Stage12 issue #110 : préenregistrement A2.11, couverture exacte Equipment et crédits UC

**14 octobre 2026, AVANT instrumentation ou nouvelles expériences.** Base `main 57476d386d7a5b742c1abd0e078568395ebc3a47`. Stage12 PARTIAL, issue #110 ouverte, réception opérateur non réalisée. Spécification normative v1.3.1 inchangée.

## Défaillance et hypothèses

A2.10b : une baie était réellement observée dès t2 et ultérieurement dans sustained perturbé, mais `stage6_planning_result=incomplete_model` revient 35–36 pas/42; la vie libre ingère pourtant malgré 33 indisponibilités. La mémoire n'est **pas prouvée défaillante**. Le préentraînement dans `scripts/run_stage12_issue110_first_planning_state.py::build_prebirth_equipment` compte **seulement quatre transitions physiques** pour le monde alimentaire : deux mouvements, une collecte, une ingestion. `FrozenTableEquipment.input_digest` lie le **SimulationState complet** (position, corps, inventaire, voisins, jour/nuit) à la commande; `predict` rend `LookupError` pour tout couple absent. La prédiction d'une action jamais vue doit demeurer indisponible.

**H_exact** : les états physiques réellement rencontrés par les vies A2.10b présentent une faible couverture des quatre clés connues; un mouvement bloqué et le corps changeant déplacent les états hors du corpus. **H_coverage** : augmenter le nombre de transitions *externes réellement appliquées avant naissance* peut augmenter certaines correspondances exactes sans inférer les conséquences d'une commande non vécue. **H_other** : mémoire, UC, refus de sécurité et concurrence peuvent encore empêcher une ingestion, même si la couverture augmente.

## Intervention 1 : diagnostic indépendant, sans code cognitif

Ajouter un rapport en lecture seule opérant **sur les archives A2.10b déjà scellées** (même 16 vies ×42 pas), qui recense chaque `stage6_planning_result` et croise son statut avec `compute_charge` de Planning, `stage8_option_evaluation`, `stage12_action_motive_attested` et ingestion `effects.ate`. Les preuves de couverture exacte doivent être rapportées **séparément**, si l'état `SimulationState` complet et les clés d'Equipment peuvent être reproduits depuis des sources auditables. Ne jamais présenter un compteur `incomplete_model` comme taux exact de clés manquantes sans audit clé-par-clé.

## Intervention 2 : plus de données physiques observées (si réalisable)

Comparer le corpus d'origine de quatre transitions à un corpus **entièrement distinct**, construit avant naissance depuis `WorldBody.apply` sur états et commandes accessibles observables. Ne pas copier `WorldBody.ground_truth`, ni les résultats de futures vies, ni l'Oracle. Conserver un vrai bras OFF (fourni historiquement) et un ON élargi. Corps, obstacle et réouverture doivent rester identiques par paire à la naissance; seuls les exemples du modèle changent. L'exact-table ne doit jamais faire de wildcard sur nourriture, risque, inventaire, jour/nuit ou identité de ressources.

### Critères prospectifs

- **T1** : toute prédiction acceptée correspond exactement à un exemple attesté et au hash de corpus; aucune prédiction sur une clé jamais vue. Un modèle général qui invente `next_state` est FAIL.
- **T2** : chaque nouvelle donnée d'entraînement provient d'une transition physique indépendante, appliquée *avant* naissance et sans Oracle; aucun état d'une vie témoin n'est utilisé pour préentraîner son bras.
- **T3** : aucun changement de règle Stage9/Stage12, UC, veto, physique, mortalité ou contrat normatif; journaux et WAL audités sur toute nouvelle cohorte.
- **C4** : un gain alimentaire exige un `effects.ate` et une hausse réelle de `body.food`; une disponibilité de simulation accrue n'est qu'une métrique technique.
- **C3** : rapporter les visites distinctes et les effets sur l'exploration; ne pas déclarer une réduction massive des mouvements bénéfique sans amélioration vécue.
- **C1/C2/C5** : jugements `self/world/unknown` et P-48 sont mesurés séparément, sans transformer prédiction en cause subjective.
- **C6/C7** : premières comparaisons 42 pas sur profils `restored/sustained`, environnement libre et A2 perturbé; deux Python = répétition technique, pas plusieurs seeds scientifiques. Long horizon seulement avec justification.
- **Décision** : si la couverture s'améliore mais la consommation pas, ne pas bricoler de retour vers la baie. Identifier d'abord le véritable mécanisme résiduel. Un échec ou des données insuffisantes demeurent documentés.

**Toute modification de politique cognitive ou de contrat normatif nécessitera un protocole et une décision distincts. Stage12 ne sera pas déclaré terminé avant réception opérateur.**
