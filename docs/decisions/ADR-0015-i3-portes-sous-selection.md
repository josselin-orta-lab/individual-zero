# ADR-0015 - I3 : les portes jugent une architecture sur ses meilleurs génomes sélectionnés

## Context

L'ADR-0014 confie à la lignée le réglage de l'inné : seuls les génomes qui persistent transmettent leurs paramètres. Jusqu'ici, les portes de I3 (G2, G2b, G2c) comparaient pourtant les architectures sur des génomes de génération 0 tirés au hasard, dans des bornes que le concepteur a choisies.

La porte G2c a montré le problème. Avec des génomes aléatoires, P1.2 perdait 6 vies sur 100 en conditions générales et a été rejeté. Son meilleur génome sélectionné, lui, survivait dans 73 mondes réservés sur 100, contre 66 pour celui de P1.1 et 70 pour le chercheur systématique de référence. La moyenne sur des génomes aléatoires mesure surtout la distribution arbitraire de la génération 0, pas ce qu'une lignée peut atteindre.

## Options considered

| Option | Verdict | Raison |
| --- | --- | --- |
| Génomes aléatoires de génération 0 (pratique actuelle) | Rejetée comme critère principal | Dépend de bornes choisies à la main ; ne mesure pas ce que la sélection atteint |
| Meilleur génome unique | Rejetée | Fragile : un seul génome peut avoir été chanceux à la sélection |
| **Les m meilleurs génomes sélectionnés sur des mondes de développement, évalués sur des mondes réservés disjoints** | **Acceptée** | Proche de ce que fera la lignée, sans biais de sélection à l'évaluation |
| Une lignée complète à chaque porte | Rejetée pour les portes de P1 | Trop coûteux ; réservé aux phases P3 et P4 |

## Experimental evidence or constraints

- [Résultat G2c](../../src/i3/docs/studies/g2c-p12-heldout/RESULTS.md) : écart entre moyenne aléatoire et génomes sélectionnés.
- [ADR-0014](ADR-0014-i3-lignee-enjeu-de-soi.md) : la persistance individuelle est le seul critère de sélection.
- [ADR-0012](ADR-0012-i2-scientific-development-methodology.md) : préinscription, résultats négatifs conservés, aucune retouche après coup.

## Decision

1. **Candidats.** K génomes `generation_zero(s)` sur des graines déclarées. Les gènes ajoutés par une architecture sont tirés en dernier, si bien que deux architectures partagent les mêmes valeurs pour leurs gènes communs.
2. **Sélection.** Chaque architecture choisit ses m meilleurs candidats sur des mondes de développement déclarés, au critère de persistance : nombre de vies menées jusqu'à l'horizon, puis durée moyenne en cas d'égalité, puis graine.
3. **Évaluation.** Les m génomes sélectionnés vivent dans des mondes réservés jamais exécutés pendant le développement ni la sélection. Statistique principale : pour chaque monde réservé, le nombre de génomes sélectionnés qui survivent (de 0 à m). La comparaison est appariée par monde, avec un test des signes exact.
4. **Valeurs par défaut** : K = 40, m = 5. Une préinscription peut les changer avant exécution.
5. **Garde-fous maintenus.** La régression G2 avec des génomes de génération 0, le rejeu exact et le budget de temps restent des conditions plancher.
6. **Descriptif obligatoire.** Survie des génomes aléatoires, part des candidats qui dépassent le chercheur de référence (« évolvabilité ») et survie du chercheur de référence.
7. **Pas de rétroactivité.** Les verdicts G2b et G2c restent inchangés. Une architecture déjà rejetée ne peut être retestée que prospectivement, sur des graines réservées neuves.

## Consequences

Une architecture est désormais jugée sur le plafond que la sélection peut atteindre, et plus sur la moyenne d'une distribution arbitraire. Le risque est de favoriser une architecture dont le bon comportement tient à une région étroite de paramètres ; la part de candidats qui dépassent la référence, publiée à chaque porte, rend ce risque visible. Le coût de calcul d'une porte est multiplié par environ K / m pour la phase de sélection.

## Individuals / axes concerned

I3. Axes : AXIS-ARCH, AXIS-ACTION, AXIS-MEMORY. Méthode de recherche.

## Date and status

5 novembre 2026 : **ACCEPTÉ par le propriétaire.**
