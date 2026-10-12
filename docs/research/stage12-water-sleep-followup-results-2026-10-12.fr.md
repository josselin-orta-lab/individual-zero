# Résultats du suivi Stage 12 eau / sommeil (12 octobre 2026)

**Nature : exploration prospective technique et comportementale, non une validation scientifique confirmatoire.**
Préenregistrement : `docs/research/stage12-water-sleep-followup-prereg-2026-10-12.fr.md` commit `6e1c3783e6c9efda38e15dcd59a1da73a666d50d`, écrit avant les exécutions. Ancienne campagne et attentes historiques non modifiées.

## Sources et vérification

- Code exécuté : `21006df1cfdacc6126b21104f82df2bd78573ade`.
- [GitHub Actions](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38303705014) : jobs follow-up Python 3.11 et 3.12 SUCCESS.
- [Preuves Python 3.11](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38303705014/artifacts/11771193436).
- [Preuves Python 3.12](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38303705014/artifacts/11770929203).
- Archives ZIP vérifiées de manière extérieure à la vie exécutée : `summary.json` + quatre `life-result.json` par version, avec WAL et export causal propre à chaque individu.
- 4/4 vies auditées par version, 50 vrais pas physiques par vie, 0 échec de vie, 0 échec d'audit. **200 pas/version = 400 pas au total**, mais quatre conditions et une réplication technique inter-Python, pas huit réalisations indépendantes de même traitement.

## Résultats par version Python

| Condition | Déplacements | Sommeils | Boire | Plans de but non nuls | Entrées / réveils | Consolidations activées |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| training_matched, sleep_reference | 3 | 47 | 0 | 0 | 16 / 15 | 0 |
| training_matched, sleep_reference_long | 3 | 47 | 0 | 0 | 3 / 2 | 0 |
| water_available, sleep_reference | 3 | 47 | 0 | 0 | 16 / 15 | 0 |
| water_available, sleep_reference_long | 3 | 47 | 0 | 0 | 3 / 2 | 0 |

**Toutes les mesures sont identiques sous Python 3.11 et 3.12.**

## Délibération des hypothèses préenregistrées

**H-EAU-MODELE : NOT_SUPPORTED.** Ajouter uniquement une source d'eau sous les pieds d'I0, comme dans le petit corpus exact de référence Stage 6, n'a produit aucun plan d'objectif ni commande boire. Le simple ajout de baies n'est donc pas l'explication unique. Même dans `training_matched`, le premier déplacement vers le nord produit ensuite un état (2,1) hors de l'équipement minimal ; cette étude n'établit pas que tous les états vécus sont couverts par le modèle. Des expériences avec prédictions effectives, provenance et budget de planification sont nécessaires.

**H-SOMMEIL-DUREE : EFFET SUR LE FRAGMENTATION, ABSENCE D'EFFET SUR LA PROPORTION.** Augmenter `max_consecutive_sleep_steps` de 2 à 18 réduit les entrées de 16 à 3 et les réveils de 15 à 2 par vie ; il ne réduit pas les 47 commandes dormir/50. L'hypothèse selon laquelle un seuil de durée suffit à sortir de la domination du sommeil n'est **pas soutenue**. Aucune consolidation n'a été activée dans ce banc, ce qui est cohérent avec le fait que la configuration de référence ne garantit pas la présence d'un `semantic_policy` de six passes. **Ne pas affirmer que sommeil répété = consolidation efficace.**

**H-TRACE : PASS logiciel ciblé, couverture scientifique INCONCLUSIVE.** Les quatre vies/versions disposent de WAL, journal causal et audits ; zéro plan d'objectif, zéro boisson. Aucune attribution personnelle vérifiée ; l'issue #110 reste ouverte. La traçabilité technique ne démontre ni une hiérarchie de motivations adéquate, ni une sécurité de récupération atomique M-11/Stage12.

## Diagnostic mécanistique disponible

Sur la campagne antérieure, `active_goal_changed` enregistre un but `drink` au pas 1, cycle 2 ; `stage6_planning_result` pour ce but revient `proposal_ref=None` au pas suivant. Des options exploratoires sont pourtant proposées, notées, puis admises avec leur motivation intrinsèque. L'absence de boire ne se réduit donc pas à une simple absence de soif ni au défaut d'audit corrigé dans la PR #128.

Les options Stage 6 dépendent d'un simulateur dont la table de référence n'a que quelques transitions exactes. Le contrat Stage 6 interdit d'inventer un résultat pour une entrée non vue. La **source de non-plannabilité** doit encore être départagée entre absence de transitions, fenêtre de planification, inadmissibilité, budget ou état cognitif.

Pour le sommeil, la pression persiste après le réveil `maximum_duration`, comme le montre la nouvelle absence de changement de la proportion de pas dormis malgré la durée plus longue. Il faut examiner la fatigue réellement réduite, la composante de consolidation, le suivi d'épisodes non consolidés et le mécanisme de comparaison en Competition, **sans injecter de correction de seuil après coup**.

## Décision sur la campagne

- **La nouvelle campagne exploratoire est techniquement complète.**
- **Le comportement boire n'est toujours pas démontré**, y compris dans le monde plus proche du corpus.
- **L'effet attendu de la durée du sommeil sur la sortie de l'état dormir n'est pas soutenu.** Son effet sur la fréquence des réveils est observé.
- Le bon fonctionnement de la régulation sommeil, de la consolidation et de la progression vers les buts n'est pas démontré.
- Le Stage 12 reste `IN_PROGRESS`, la récupération atomique M-11/Stage12 reste non certifiée, et aucune validation opérateur ou scientifique finale n'est accordée.

## Recommandation prioritaire

Créer deux chantiers dissociés :

1. **Modèle d'équipement/planning** : exposer en lecture indépendante le motif exact de `no_plan` (entrée inconnue, horizon, modèle incomplet, budget, condition non atteinte), puis entraîner/évaluer une version testable sur des transitions réellement acquises et sur des mondes nouveaux. Pas d'Oracle dans I0, pas de faux succès.
2. **Sommeil** : vérifier la source de pression persistante, la disponibilité des six passes de consolidation dans la vie intégrée Stage12 et les effets réels sur la sélection des options ; comparer à une variante candidate préenregistrée sur nouveaux mondes avant de la promouvoir.

**Le MVP v1.3.1 n'est pas modifié** : clarifier les critères de couverture en version suivante nécessite une validation normative explicite.
