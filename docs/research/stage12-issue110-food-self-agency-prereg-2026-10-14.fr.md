# Issue #110 — Préenregistrement : jugement `self` sur ingestion vécue et résultat de nourriture

**Date : 14 octobre 2026.** Préenregistrement **avant toute implémentation ou exécution de cette nouvelle campagne**. Branche née du commit technique PR #147 `f0f4b72ab9cfacff8843dd26d75ef5734cf69c43`. Cible normative GA-01..GA-07 de la PR #148, non fusionnée. Ne pas réinterpréter la spécification v1.3.1 ni la conclusion Stage 9 NO-GO.

## Justification et hypothèses

La campagne indépendante #151 a démontré, sur 100 vrais pas et deux vies, une réussite corporelle, un non-gain et deux jugements cognitifs légitimes `unknown` au coût UC effectivement payé, mais zéro couple de biais. Le producteur GA existant peut formuler `self` **uniquement** après une commande `manger` rattachée à un but `food`, lorsque le nouvel inventaire perçu baisse exactement d'une unité et que la position n'a pas changé. Cette preuve est **différente** du critère de réussite sur `body.food`. Elle n'est ni un label causal physique, ni une conformité P-47. Le producteur ne dispose pas de mécanisme `world` défendable pour la nourriture.

- **H1 :** une trajectoire de recherche physiquement exécutable amène I0, sans commande imposée, à proposer et éventuellement accomplir `collecter` puis `manger` afin d'atténuer une faim réelle.
- **H2 :** sous commande `manger` réellement admise/appliquée, Action Control préenregistre le mécanisme `ingested_from_inventory` **avant** la transition puis constate au cycle suivant une décrémentation d'inventaire perçue ; dans ce cas uniquement, un jugement subjectif `self` payé est produit. Changer le gain de nourriture à indice d'inventaire égal ne doit pas fabriquer/changer ce jugement (contrôle logiciel adversarial séparé).
- **H3 :** le résultat du critère strict sur `body.food` est mesuré indépendamment. Un couple `(outcome, self)` ne peut être admis qu'avec deux propriétaires/receipts, des références uniques, le débit UC d'évaluation d'agence et un débit UC de jointure séparé. `unknown` n'est jamais promu en `world`.
- **H4 :** un seul couple authentique ne suffit pas à détecter un biais. Sans `self/world` et deux succès/deux échecs distincts, `attribution_bias=None` reste le verdict correct.
- **H5 :** le refus par le modèle Equipment exact d'entrées non vues, l'absence de commande ou les refus UC doivent demeurer explicitement non conclusifs plutôt que maquiller les effets.

## Conditions préfixées

**Factoriel 2×2, quatre vies distinctes par version Python, 50 transitions physiques appliquées au maximum par vie**. Facteur équipement : `reference_exact` (table Stage 6 de développement, étroite et inchangée) ou `physical_food_corpus` (table exacte figée avant naissance). Facteur horizon de valorisation Stage6 : `h_eff=2` ou `h_eff=3`; toutes les versions du même candidat utilisent `simulator.h_max=3`, `planning.max_depth=3` et une `version` nouvelle fixée à la naissance, afin que le changement de l'horizon effectif reste traçable. Les 4 vies partagent le même monde (sans scénario caché injecté) et le même échantillon initial.

Monde défini avant exécution : grille physique normative 32×32 ; départ (2,2), `resources=((Position(2,2), "berry_a", 2),)`, eau sur la case (2,2) conservée mais initialisation `water=70` pour **ne pas** inventer une soif, `food=35` pour atteindre la pression de faim, `energy=50`, `integrity=100`. Effet physique versionné et injecté avant naissance : `berry_a.food_gain=30`, intégrité delta zéro ; `berry_b` normative inchangée. Aucune commande forcée et aucune commande issue d'un scénario laboratoire. Pas de température/danger opportuniste rajouté.

Corpus optionnel constitué **hors d'I0 avant sa naissance** par des transitions effectivement appliquées à un WorldBody d'entraînement, sur la même config/layout : `north`, `south`, `collecter berry_a`, `manger berry_a` aux pas successifs, avec capture accessible ; Equipment exact généré par la routine de référence. Ne jamais fournir un résultat d'entraînement au système cognitif après sa naissance ni déduire une attribution à partir des données d'entraînement. Ce corpus externe ne démontre pas d'apprentissage autonome de l'équipement, et l'état de développement n'est pas un monde tenu à l'écart de l'entraînement.

Même profil de sommeil que l'expérience #132 : `consolidation_weight=0` autorisé temporairement, sans supprimer le calcul de `p_cons`, six phases conservées et aucune suspension a posteriori. Réutiliser `Stage12GoalProgressLedger`, `GoalAgencyService`, `Stage12AttributionPairs`. Config pré-naissance obligatoire : `subjective_goal_agency=True`, `goal_agency_cost_uc=1`, `attribution_join=True`, `attribution_join_cost_uc=1`, `diagnostic_sample_cost_uc=1`, `module_occupancy_cost_uc=1`. Détecteur figé : `window=12`, `bias_min_outcomes_each=2`, `attribution_bias_threshold=0.75`, `stagnation_steps=4`, `stagnation_tolerance=0.05`, `loop_repetitions=3`, `loop_max_period=2`, `entropy_min_samples=4`, `entropy_warning_fraction=0.25`.

## Mesures et preuve

Pour chaque vie, conserver WAL durable, export JSONL canonique, SHA256, head/count, version/empreinte Equipment, scénario préfixé, pas appliqués, état de mortalité, options de buts proposées, commandes effectivement appliquées par primitive, plan engagé/motif, intention préenregistrée, score d'objectif `success/failure/unknown`, préengagement/jugement GA `self/world/unknown/unavailable`, jointures admises/utilisées, débits UC acceptés/refusés et diagnostics. Échec/absence de preuves et arrêt technique ne doivent pas disparaître du dénominateur.

Auditer les mêmes ancres immuables avec `audit_export_bytes`, `audit_stage12_goal_progress`, `audit_stage12_first_person_agency`, `audit_stage12_attribution_pairs` et `audit_stage12_diagnostics`, sans importer I0 dans les auditeurs. Tests adversariaux distincts : aucun `self` sans décrément d'inventaire perçu, aucun `world` déduit de l'absence de gain corporel, aucun label postmortem, aucune jointure sans débit UC, pas de succès fabriqué en changeant la prédiction P-47.

Deux interpréteurs CPython 3.11 et 3.12 servent **uniquement de contrôle de reproductibilité déterministe** ; les 8 exécutions techniques ne sont pas 8 vies scientifiques indépendantes. Aucun relèvement arbitraire des seuils ni allongement opportuniste des vies.

## Verdicts préenregistrés

- **Preuve exploratoire partielle positive :** au moins un `self` et un couple authentiquement admis après consommation librement choisie, avec audits et UC exacts. Cela ne valide pas encore les diagnostics statistiques.
- **Inconclusif :** pas de commande alimentant la chaîne, pas de `self`, ou uniquement `unknown`, mais événements vérifiés sans incohérence.
- **NO-GO logiciel :** journal incohérent ou preuve forgée acceptée, calcul UC gratuit, causalité cachée injectée, jugement postmortem ou résultat de but rétroactif.
- **Aucune validation scientifique finale**, Stage 12 non réceptionné, issue #110 ouverte quelle que soit la conclusion de cette exploration.

Une politique `world` nécessite un indice extérieur **spécifique, perceptible et pertinent pour le but**. Aucune classe `world` n'est créée par l'étude de nourriture, ni par un label de faute de prédiction P-47.
