# I3 — étape 6 légère : brouillon de protocole (13 novembre 2026)

**Statut : BROUILLON, NON GELÉ, NON AUTORISÉ.** Ce document ne lance rien. Il n'ouvre aucun World, ne crée aucune vie, n'attribue aucun indice et ne lève aucun moratoire. Il ne deviendra un protocole qu'après les décisions du propriétaire listées en section 9, le transport et une répétition scellée.

**Base :** `main` = `3f3a7ef` (13 novembre 2026), fusionné dans la branche de préparation de ce dossier. **Référence testée :** P1.3 funded-v2, **inchangée**. Aucun mécanisme n'est ajouté à l'individu.

## 1. Autorités et périmètre

- L'[ADR-0014](../../../../../docs/decisions/ADR-0014-i3-lignee-enjeu-de-soi.md) pose la thèse : l'inné est façonné par la survie, avec la persistance individuelle pour seul critère de sélection.
- L'[ADR-0018](../../../../../docs/decisions/ADR-0018-i3-cloture-etape-1.md) constate que cette thèse n'a jamais été exercée et recommande d'avancer une étape 6 légère. Il précise que c'est une recommandation et non une décision.
- L'[ADR-0017](../../../../../docs/decisions/ADR-0017-i3-moratoire-deux-phases-repetition-scellee.md) impose deux phases et une répétition scellée avant toute levée. L'[ADR-0020](../../../../../docs/decisions/ADR-0020-i3-owner-selected-development-reference.md) §5 autorise un agent à préparer un protocole, pas à ouvrir un monde.
- L'[ADR-0021](../../../../../docs/decisions/ADR-0021-i3-stage2-internal-hold-no-verdict.md) suspend l'étape 2 et précise qu'il ne libère aucune cohorte des étapes 3 à 6. Le [plan](../../DEVELOPMENT_PLAN.md) ajoute qu'une telle cohorte demande son propre plan prospectif et sa propre autorité. Les décisions DÉC-2 et DÉC-3 de la proposition de feuille de route ne sont pas acceptées. **Ce brouillon est ce plan prospectif. L'autorité reste entièrement à donner.**
- Ce brouillon s'appuie sur la [lecture descriptive de P3](P3_GENE_SHIFT_DESCRIPTIVE_RESULTS_2026-11-13.md) et sur le [modèle nul de dérive](STAGE6_LIGHT_DRIFT_NULL_RESULTS_2026-11-13.md).

Cette étape ne compare pas deux architectures. Elle est donc distincte du [plan à huit populations de l'étape 0](../../STAGE0_DESIGN.md), qui sert les portes de l'ADR-0015.

## 2. Question

**Sous sélection par la seule persistance, le poids de curiosité exprimé se déplace-t-il dans le même sens, par rapport à un bras à parents aléatoires, dans des populations indépendantes ?**

Le critère est bilatéral. La lecture de P3 a montré qu'une direction présumée peut être fausse. Aucun sens n'est attendu d'avance.

## 3. Plan proposé

| Paramètre | Valeur proposée | Origine |
| --- | --- | --- |
| Populations indépendantes | 16 | modèle nul, règle déclarée |
| Génomes par population | 24 | modèle nul, règle déclarée |
| Générations | 3 (G0, G1, G2), soit deux tours de sélection | modèle nul : le bruit de dérive croît avec les générations |
| Bras | `selected` et `random_parent`, génération 0 identique | P3 |
| Persistance d'un génome | nombre de vies censurées, puis total des pas vécus, sur ses 6 vies | P3, ADR-0014 §3 |
| Règle des parents | `selected` : poids linéaires 24, 23, ..., 1 selon le rang, égalités départagées par l'emplacement. `random_parent` : tirage uniforme | P3, généralisée |
| Mutation | `genome.mutate`, échelle 0,1, génome v4 | code de référence |
| Vies par génome | 6 : trois familles F0, deux répétitions, mêmes mondes pour tous les génomes et les deux bras d'une population à une génération | P3 |
| Horizon | 400 pas | P2 |
| Politique de décision | `reference` (P1.3 funded-v2), au SHA exact du transport | référence en vigueur |

Aucune expérience vécue n'est transmise : un descendant ne reçoit que le génome muté de son parent (ADR-0014 §6).

## 4. Critère principal et verdicts

**Quantité principale.** `beta_u_eff = beta_u * (1 + 0.5 * temperament.exploration)`, le poids de curiosité exprimé par la référence. Elle a été déclarée principale avant la lecture de P3.

**Statistique.** Pour chaque population, le contraste entre la moyenne du bras `selected` et celle du bras `random_parent` à la génération 2.

**Règle.** Test de signe exact et bilatéral sur les 16 contrastes. Le seuil est de 13 signes concordants sur 16, de probabilité 0,0213 sous l'hypothèse nulle.

| Verdict proposé | Condition |
| --- | --- |
| `STAGE6_LIGHT_SHIFT_ESTABLISHED` | au moins 13 contrastes de même signe, intégrité complète, contrôles neutres respectés |
| `STAGE6_LIGHT_SHIFT_NOT_OBSERVED` | moins de 13 contrastes de même signe, intégrité complète |
| `STAGE6_LIGHT_INVALID` | défaut d'intégrité ou contrôle neutre violé (section 5) |

**Portée d'un résultat nul.** D'après le modèle nul, ce plan détecte à 80 % de puissance un déplacement d'au moins 0,314, soit environ la moitié de l'écart-type entre génomes fondateurs. Un verdict « non observé » ne réfute donc pas un déplacement plus petit. Il reste publiable tel quel.

**Portée d'un résultat positif.** Il établirait un déplacement directionnel dans les familles F0 et pour cette règle de parents. Il ne dirait rien d'autres mondes, ni d'un avantage de survie des génomes sélectionnés.

## 5. Contrôles et quantités secondaires

- **Bras `random_parent`** et génération 0 appariée.
- **Marqueurs neutres.** `omega`, `temperament.affiliation` et `temperament.reward_sensitivity` ne sont pas lus par la référence. Un [test logiciel](../../../../../tests/i3/test_reference_neutral_marker_genes.py) le confirme sur trois mondes de la cohorte `engineering` : mettre chacun de ces gènes à l'une ou l'autre de ses bornes laisse chaque pas d'une vie de référence identique, alors que mettre `beta_u` à zéro change la vie. Ce test doit repasser sur le SHA exact du transport. Pendant l'essai, chacun a 2,1 % de chances d'atteindre 13 sur 16 par hasard. Le résultat est `STAGE6_LIGHT_INVALID` si au moins deux des trois atteignent ce seuil. Si un seul l'atteint, c'est rapporté comme un avertissement.
- **Quantité secondaire.** `beta_u` normalisé, même statistique, sans verdict propre.
- **Descriptif, sans verdict.** Tous les autres gènes, la part des génomes aux bornes, le nombre de fondateurs encore représentés, la survie à l'horizon et les coûts payés.
- **Calibrage du test de signe.** Le modèle nul signale une asymétrie de la quantité composée quand les lignées se réduisent à un ou deux fondateurs. À trois générations et 24 génomes, il n'en détecte pas. Le nombre de fondateurs restants est donc rapporté pour chaque population.

Les génomes de la génération 2 sont gelés à la fin de l'essai. Leur évaluation sur des mondes réservés ne fait pas partie de cette version légère.

## 6. Mondes, graines et indices

**Besoins.** 288 mondes : 16 populations, 3 générations, 3 familles, 2 répétitions. 384 graines de génomes fondateurs. Des graines de vie, de mutation et de tirage des parents sous des étiquettes propres à cet essai.

**Rien n'est attribué ici.** Deux faits bornent le choix.

- La cohorte `selection` de P2 compte 400 graines. P3 en a consommé les indices 0 à 71, et le plan de l'étape 0 réserve les suivants à partir de 72 ([stage0_design.py](../../../lab/stage0_design.py), `OFFSETS` et `KNOWN_ALLOCATED_THROUGH`). Elle ne peut pas porter 288 mondes de plus sans empiéter sur ce plan.
- La cohorte `engineering` (1 000 graines, [engineering_cohort.py](../../../lab/engineering_cohort.py)) suffit pour une répétition scellée à pleine échelle. Elle n'est jamais admissible comme preuve.

**Proposition.** Déclarer une plage de graines dédiée à côté de `p2_ecologies.py`, comme l'a fait la cohorte `engineering`, sans modifier ce fichier. Le transport doit vérifier qu'elle est disjointe de toutes les allocations antérieures. La réserve `1200000..1200199` reste scellée.

## 7. Garde en deux phases pour une lignée : décision demandée

L'ADR-0017 demande que toutes les vies prévues soient générées avant toute réduction. Une lignée ne peut pas l'appliquer à la lettre : les génomes d'une génération dépendent de la persistance mesurée à la génération précédente. Je propose la lecture suivante, que le propriétaire doit accepter ou corriger avant le gel.

1. **Un panel en deux phases par génération.** Toutes les vies de la génération sont générées et scellées (phase G). Rien d'autre n'est lu ni affiché que l'avancement et les empreintes.
2. **Un réducteur de sélection figé entre deux générations.** Il ne lit, dans les originaux scellés, que le statut terminal et le nombre de pas vécus de chaque vie. Il produit les indices des parents et un reçu scellé. Il n'affiche aucun score.
3. **Une analyse finale unique** (phase R), après le scellement de la dernière génération. Elle relit les originaux, rejoue la sélection pour la vérifier, puis applique la règle de la section 4.
4. **Un défaut du réducteur de sélection clôt la lignée** en `ENGINEERING_FAILURE_NOT_A_DEATH`, sans reprise. C'est plus strict que l'ADR-0017, qui laisse un défaut de réduction réparable : réparer ce réducteur en cours de lignée pourrait changer la sélection. Un défaut de l'analyse finale reste réparable, comme le prévoit l'ADR.
5. **Une seule exécution.** Aucune génération n'est rejouée. Aucun paramètre n'est modifié après le gel.

## 8. Budget

| Poste | Valeur |
| --- | --- |
| Vies scientifiques | 11 520 si la génération 0 n'est vécue qu'une fois par population ; 13 824 si elle est vécue dans les deux bras, comme dans P3 |
| Pas simulés | au plus 4 608 000, ou 5 529 600 |
| Calcul | 1,0 à 2,0 heures-CPU à 0,8-1,3 ms par pas **(hypothèse, hors coût de garde)** |
| Répétition scellée | même nombre de vies techniques sur la cohorte `engineering` |
| Mondes | 288 graines neuves |

Les deux bras partagent des génomes, des mondes et des graines identiques à la génération 0. Leurs vies y sont donc identiques par construction. Je propose de ne les vivre qu'une fois.

## 9. Ce qui reste avant le gel

**Décisions du propriétaire.**

1. Accepter ou modifier le plan : 16 populations, 24 génomes, 3 générations, seuil de 13 sur 16, quantité principale, seuil de détection d'une moitié d'écart-type.
2. Accepter ou corriger la lecture de l'ADR-0017 pour une lignée (section 7).
3. Désigner la plage de graines de mondes et celle des génomes fondateurs.
4. Après la répétition scellée : consigner la levée indexée dans `STATUS.md`.

**Travail d'agent, couvert par l'ADR-0020 §4 et §5.**

1. Transport de lignée avec garde fermée par défaut : aucune graine scientifique n'est admise sans levée.
2. Test logiciel de neutralité des trois marqueurs : fait, à rejouer sur le SHA du transport.
3. Réducteur d'analyse appliquant exactement la section 4, vérifié sur des lignées synthétiques.
4. Répétition scellée à pleine échelle sur la cohorte `engineering`, sur le SHA exact, en Python 3.11 et 3.12.
5. Gel du protocole : commit portant le SHA exact et les empreintes.

## 10. Écarts par rapport à la proposition de feuille de route

La proposition de feuille de route (PR #1359) avançait, à titre d'hypothèse, 8 à 12 populations de 6 génomes sur 4 à 6 générations, soit 2 304 à 5 184 vies, et un « témoin positif » directionnel. Trois points changent.

- **Taille.** 16 populations de 24 génomes sur 3 générations, soit 11 520 à 13 824 vies. Le modèle nul montre que le plan initial n'aurait presque rien pu détecter.
- **Direction.** Le critère est bilatéral. L'attente directionnelle déclarée pour P3 n'a pas été vérifiée.
- **Contrôle neutre.** La règle d'invalidité est calibrée : deux marqueurs sur trois au seuil, et non un seul mouvement.

## 11. Risque de règle imposée ou d'oracle

- **Côté individu : aucun.** La référence n'est pas modifiée. Aucune récompense, aucune action forcée, aucun état hérité, aucun calcul gratuit.
- **Côté concepteur.** Le choix des mondes et de la règle des parents peut favoriser un gène. La parade est de reprendre sans changement le générateur F0 et la règle de P3, et de tirer les graines par une règle figée.

## 12. Non-revendications

Ce brouillon n'est ni un protocole gelé, ni une autorisation, ni une revue indépendante. Il ne dit pas que la sélection façonne l'inné. Il ne modifie ni la référence, ni le registre, ni `ACTIVE_SURFACE.json`, ni un ADR.
