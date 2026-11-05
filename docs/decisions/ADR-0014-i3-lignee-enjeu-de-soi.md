# ADR-0014 - I3 : un individu dont l'enjeu est lui-même, dans une lignée où la survie façonne l'inné

## Context

Objectif posé par le propriétaire le 5 novembre 2026 : **un système dont les enjeux sont le système lui-même.**

Ni I1 ni I2 n'ont établi d'adaptation durable fondée sur l'expérience. A1-C conclut à un NO_GO ciblé (48 vies) ; A2-R n'a pas été exécutée (0/96). Le panel I2 #967 compte six morts de faim au tick 61 avec des actions identiques entre bras ON et OFF.

Un diagnostic du 5 novembre (lecture du code au commit `f9ca3f4` et quelques vies observées, **sans valeur confirmatoire**) trouve deux défauts structurels :

- **I1** : récompense en distance absolue aux consignes (le surplus est pénalisé), horizon TD d'environ 5 pas, simulateur Stage6 en table de transitions exactes presque toujours indisponible, option `permanent:attendre` favorisée par Competition, mémoire sans autorité de décision. Une vie *foraging* meurt de soif à 2 cases de l'eau.
- **I2** : choix par argmax de scores entiers, abstention en cas d'égalité. Une vie s'abstient 108 ticks sur 128 ; une autre meurt de soif au passage, à un déplacement de l'eau.

Cause commune : l'enjeu se réduit à quatre variables corporelles choisies par le concepteur. Perception, mémoire, modèle et délibération sont gratuits et invulnérables.

## Options considered

| Option | Verdict | Raison |
| --- | --- | --- |
| Corriger la récompense de I1 (A2-R) | Rejetée comme voie principale | Ne traite ni la recherche dirigée par le besoin ni l'invulnérabilité de la cognition. A2-R reste un test légitime de I1. |
| Poursuivre I2 par règles de départage | Rejetée | Dérive constatée : 11 drapeaux de naissance, genèse v23, une règle par cas d'échec. |
| I3 avec enjeux fixés par le concepteur | Rejetée comme fondement | L'enjeu reste extérieur au système. Conservée comme bras témoin. |
| I3 avec reproduction déclenchée par l'individu | Rejetée | La sélection favoriserait la reproduction et déplacerait l'enjeu vers la lignée. |
| I3 en lignée, sélection sur la persistance individuelle | **Acceptée** | L'inné devient le produit de la survie ; l'enjeu de chaque individu reste lui-même. |

## Experimental evidence or constraints

- Résultats préservés : [bilan de campagne du 2 novembre](../research/audits/I1_I2_SCIENTIFIC_CAMPAIGN_CLOSEOUT_2026-11-02.md), [audits post hoc A1-C](../research/audits/I1_ECO_A1C_FIXED_TAPE_REWARD_SENSITIVITY_2026-10-30.md), [statut I2](../../src/i2/docs/STATUS.md).
- Contraintes maintenues : [ADR-0001](ADR-0001-strict-generation-autonomy.md) (autonomie de génération), [ADR-0012](ADR-0012-i2-scientific-development-methodology.md) et [ADR-0013](ADR-0013-lived-autonomy-and-experimental-restraint.md) (méthode, retenue expérimentale, droit à l'erreur).
- Contrainte de calcul : une lignée de 8 × 64 × 200 vies de 1 000 pas représente environ 10⁸ pas. I1 tourne à environ 0,6 s par pas ; I2 rejoue tout l'historique à chaque pas. I3 doit viser au plus 1 ms par pas.

## Decision

1. **Deux boucles.** Dans une vie, l'individu perçoit, agit et apprend sans rien recevoir d'autre que son génome. Entre les vies, la persistance sélectionne les génomes.
2. **L'enjeu est l'organisation entière.** Percevoir, évaluer et retenir coûtent de l'énergie (monnaie vitale). Les capacités cognitives dépendent de l'état du corps et d'un canal de vigilance. La norme première est la viabilité.
3. **Un seul critère de sélection : la durée de vie individuelle**, sur un horizon où la plupart des individus meurent. Le laboratoire fait naître les descendants ; l'individu ne se reproduit pas. Écart délibéré avec la biologie.
4. **Génome admissible** : paramètres génériques seulement, invariants par renommage ou permutation des objets, lieux et positions du monde.
5. **Familles de mondes** tirées au hasard à chaque vie ; familles réservées pour l'évaluation.
6. **Invariant de naissance reformulé** : *naissance sans expérience héritée ni fait du monde ; seuls des paramètres innés génériques, admissibles par invariance au renommage et sélectionnés par la persistance, sont transmis.*
7. **Autonomie de génération.** ADR-0001 s'applique : aucun import ni état de I0, I1 ou I2. Les fonctions pures de I2 utiles à I3 sont recopiées avec leur provenance (RAI : ADAPT).

La spécification détaillée vit dans [src/i3/docs/SPECIFICATION.md](../../src/i3/docs/SPECIFICATION.md).

## Consequences

| Élément | Statut dans I3 |
| --- | --- |
| Perception à la première personne, aucun oracle | Conservé |
| Mort irréversible, aucune reprise après décès | Conservé |
| Competition puis Action Control, seul chemin moteur | Conservé |
| Distinction logiciel / comportement / science, échecs publiés, préenregistrement | Conservé |
| Autonomie de génération | Conservé |
| Naissance sans connaissance préalable | Reformulé (décision 6) |
| UC comme compte séparé du corps | Remplacé par la monnaie vitale |
| Custodie complète à chaque pas | Réservée aux vies échantillonnées et de test ; rejeu déterministe pendant l'évolution |
| Génome, registre de lignée, générateur de mondes | Nouveaux |

**Limites des affirmations.** I3 ne pourra jamais établir que quelque chose importe *pour* lui au sens vécu, seulement une organisation fonctionnellement orientée vers sa propre persistance. Aucune affirmation de conscience, de sentiment ou d'intelligence générale.

**Biais assumé.** La sélection inscrira des régularités statistiques du monde dans des paramètres génériques. Les familles tirées au hasard et les familles réservées bornent ce biais sans l'éliminer.

I3 reste `status: proposal`, sans point d'entrée ni enregistrement. I1 reste le seul moteur actif.

## Individuals / axes concerned

I3 (nouvelle génération de recherche). Axes : AXIS-ARCH, AXIS-REGULATION, AXIS-MEMORY, AXIS-ACTION, AXIS-SELF. I1 et I2 restent des références comparatives.

## Date and status

5 novembre 2026 : **ACCEPTÉ par le propriétaire.** Aucune activation de moteur, aucun GO scientifique.
