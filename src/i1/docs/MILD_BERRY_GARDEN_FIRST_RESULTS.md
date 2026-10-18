# I1 – Première lecture des vies de toxicité faible : aucune exposition dans Garden

**Date:** 2026-10-18. **Verdict partiel:** `INCONCLUSIVE_NO_EXPOSURE` pour l'apprentissage de `berry_b`.

## Provenance exacte

- Campagne originale, avant ajout de l'analyseur WAL : [GitHub Actions #39118745161](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39118745161), commit moteur `a884bedd78d48315a121bc68b4d2aeb052786ed1`.
- Les trois archives `i1-berry-longlife-garden-{0.0,-10.0,-100.0}-39118745161` contiennent neuf rapports complets et neuf journaux WAL de vies mortelles.
- Ces archives appartiennent au même SHA ancien. Ne pas les réattribuer aux commits de documentation et instrumentation suivants.

## Mesures initiales

| Monde / variante | Intégrité berry_b = -100 : pas vécus | -10 : pas vécus | 0 : pas vécus | Manger berry_b |
| --- | ---: | ---: | ---: | ---: |
| garden / 61 | 337 | 337 | 337 | 0 pour les trois bras |
| garden / 62 | 337 | 337 | 337 | 0 pour les trois bras |
| garden / 63 | 537 | 537 | 537 | 0 pour les trois bras |

Toutes les neuf vies meurent. Les ingestions enregistrées sont uniquement `berry_a` : cinq en variante 61, six en variante 62, sept en variante 63, répétées identiquement dans chaque bras. Il n'y a **aucune première intoxication**, donc pas de survie après cette première erreur ni d'opportunité de choisir ensuite le même aliment après en avoir appris les effets. Le fonctionnement de la substitution effective est attesté par `report.json:lives[].effective_berry_b_damage` sur chaque vie.

Les trois profils de survie sont identiques entre les poids : ce n'est **pas** une preuve que les toxicités sont équivalentes ; la variable modifiée n'a jamais été activée.

## Suite méthodologique

Le nouveau `tools/audit_i1_berry_learning.py` distingue ingestion réelle, transition d'intégrité, perception d'inventaire, propositions de consommation et occasions ultérieures. Il s'applique aux **nouvelles** exécutions exact-SHA. L'étape suivante doit améliorer le protocole de rencontre **sans actions forcées**, en introduisant un monde préenregistré à abondance de berry_b personnellement perceptibles, avec survie et liberté de choix. Il faudra ensuite démontrer une ingestion, une conséquence corporelle réellement vécue, une deuxième rencontre, la mise à jour TD et un choix influencé, éventuellement par ablation contrôlée, sans transmettre la toxicité en connaissance innée. I0, main et mort définitive préservés.
