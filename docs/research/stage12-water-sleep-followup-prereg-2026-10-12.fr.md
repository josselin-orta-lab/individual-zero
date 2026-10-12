# EXP Stage12 | Diagnostic prospectif eau / sommeil | 12 octobre 2026

**Préenregistré avant les nouvelles exécutions. Exploratoire, aucune validation scientifique finale.**

Référence normative : `docs/architecture/reference/en/mvp-specification-v1.3.1.md`. Fondements : `docs/architecture/reference/fr/architecture-v2.md` §§25,27,39,40,43. Source figée avant ajout du runner : `167b274dd422caabb9d3ae03116232aa57c38f29`.

## Observation motivant l'expérience, non prévision du résultat

Archives du run 38298279330 : but `drink` créé dès le cycle 2 du premier pas, aucun `boire` ensuite, et `stage6_planning_result.proposal_ref=null` au pas suivant. Le simulateur Stage6 de référence utilise une table de transitions **exactes** entraînée sur un corps à 20 unités d'eau et une source à (2,2) ; les scénarios précédents combinent positions, baies et données corporelles différentes. Le modèle peut être hors support ; il ne faut pas conclure que l'exploration a « écrasé » une option de boire disponible.

Le sommeil de référence produit 47/50 `dormir`, avec pression de consolidation persistante après réveil de durée maximale 2 pas. Ne pas confondre consommation de temps physique, utilité réelle du sommeil, réveils et consolidation effectivement validée.

## Manipulations prévues

Nouvelle vie mortelle par condition, aucune modification de l'ancienne campagne ni des résultats historiques. 2 mondes × 2 politiques de sommeil, 50 pas physiques maximum/vie :
- `water_available` : source initiale et baies, comme la campagne précédente (même variable eau corporelle 20).
- `training_matched` : seulement source initiale en (2,2), sans baie supplémentaire ; état initial d'eau 20 et corpus Stage6 inchangé.
- `sleep_reference` : politique existante avec maximum 2 pas consécutifs.
- `sleep_reference_long` : identique sauf `max_consecutive_sleep_steps=18`, variation expérimentale **non normative**.

Ces deux facteurs sont fixes avant exécution. Aucune action, issue d'un test, sortie du simulateur ou jugement Oracle n'est injecté dans la cognition. La cognition et le simulateur restent inchangés.

## Hypothèses falsifiables

H-EAU-MODELE : présence de plans d'objectif `drink` non nuls et de commandes `boire` plus fréquente dans `training_matched` que dans `water_available` à politique de sommeil identique. Si aucune différence ou aucun `boire`, **NOT_SUPPORTED**, avec vérification indépendante des étapes et des préconditions. En 50 pas, un `boire` absent malgré préconditions valides pourrait rester INCONCLUSIVE si le plan est refusé pour un motif de sécurité.

H-SOMMEIL-DUREE : augmenter la durée maximale réduit le nombre de réentrées et peut diminuer la proportion de commandes `dormir`; aucune direction n'est garantie pour la proportion. Nombre d'entrées/réveils par vie, pas dormis, fatigue gelée et pression de consolidation ; mesurer également les événements de consolidation effectivement publiés. Si le nombre de pas dormis reste majoritaire, l'hypothèse de correction comportementale est non soutenue.

H-TRACE : aucun succès objectif ou attribution personnelle ne peut être affirmé sans préenregistrement et provenance. M11 Stage12 demeure non atomique.

Analyse : 4 vies différentes **par version Python** seulement ; le doublon 3.11/3.12 est une réplication technique, pas un doublement de N. Conserver les morts, blocages, pannes et artefacts. Rapporter effectifs et comparaisons descriptives, sans p-value. Un échec logiciel, scientifique ou comportemental ne modifie pas le protocole. Les nouveaux résultats doivent être classés `SUPPORTED`, `NOT_SUPPORTED` ou `INCONCLUSIVE` avec leurs limites.

**Aucune acceptation opérateur ou certification scientifique n'est autorisée par le seul succès CI.**
