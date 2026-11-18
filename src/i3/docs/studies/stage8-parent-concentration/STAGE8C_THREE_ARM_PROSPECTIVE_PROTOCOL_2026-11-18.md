# i3 Stage8-C · protocole prospectif à trois bras, méthode fixée AVANT vies

**Date de gel méthodologique : 18 novembre 2026.** Statut : **SOURCE/PLAN LOGICIEL PRÉEXPOSITION, AUCUNE VIE STAGE8-C CONSTATÉE À LA RÉDACTION**. Le code appartient à I3, moteur de référence non activé. **Aucune naissance scientifique ne peut être déclenchée par ce protocole ou le transport technique.** Autorité propriétaire pour les nouvelles expérimentations internes : [ADR-0022](../../../../../docs/decisions/ADR-0022-i3-owner-authorizes-prospective-experiments-internal-evidence.md). Les 32 populations Stage8-A et Stage8-B ainsi que Stage7 et leurs graines sont consommées et ne seront pas réutilisées.

## Hypothèse et critère primaire falsifiable

**H0** : l'avantage moyen héréditaire de persistance corporelle en G2, entre descendants de parents sélectionnés pour une persistance vécue **S** et descendants de parents de même concentration reproductive mais d'identité brouillée **M**, est nul ou négatif.

**H1** : ce contraste moyen G2 est strictement positif. L'unique estimand et test prévu est, pour chaque population nouvelle p=0..31 :

\`D[p] = mean(steps_lived_G2_S, 24 génomes × 6 mondes F0) − mean(steps_lived_G2_M, 24 génomes × les mêmes 6 mondes F0)\`.

La population est **l'unique unité inférentielle (n=32)**. Les 32 valeurs D sont conservées intégralement, même négatives ou nulles, sans retirer les morts, tronquer les scores ou réallouer après observation.

Le critère primaire de succès, fixé dès maintenant :

- Student t **unilatéral**, 31 degrés de liberté, niveau **α=0,025**, \`t_crit=2.0395134463964077\`.
- Moyenne \`m=mean(D)\`, écart-type empirique \`s=√(Σ(D−m)²/31)\` et borne inférieure 97,5 % \`L=m−t_crit*s/√32\`.
- **Succès** \`STAGE8C_G2_SCORE_IDENTITY_ADVANTAGE_F0\` uniquement si s est strictement positif, finie, et **L>0** ; sinon \`STAGE8C_G2_SCORE_IDENTITY_ADVANTAGE_NOT_DEMONSTRATED_F0\` pour les données valides.
- Dispersion nulle, NaN, matrice incomplète ou incohérence archivistique : **jamais** un succès ; les manques techniques entraînent **\`TECHNICAL_NO_VERDICT_NO_RETRY\`**, non un verdict biologique négatif.
- \`S−U\`, \`M−U\`, fractions survivantes censurées à 400, dimensions du génome et entropie parentale sont **secondaires descriptifs**. Aucun ne remplace S−M ni ne justifie un changement de seuil.

Une naissance exactement au pas 400 avec \`terminal=dead\` est distincte d'une censure à 400 chez un survivant vivant. La persistance est la durée vécue, pas une récompense synthétique ni un avantage proclamé par la CI.

## Taille définitivement fixée et planification de puissance

**32 nouvelles populations F0, deux panneaux disjoints de 16**, chacune ayant 24 génomes G0, puis 24 descendants pour chacun des trois bras S/M/U en G1 et G2. Chaque génome vit six occasions World préallouées (familles \`stable\`, \`depletion\`, \`pulse\`, deux répétitions par famille). Soit pour **chaque répétition technique et pour la future exécution scientifique distincte** :

| Génération | Bras | Vies natives | Calcul |
| --- | --- | ---: | --- |
| G0 | partagé | 4 608 | 32×24×6 |
| G1 | S, M, U | 13 824 | 32×3×24×6 |
| G2 | S, M, U | 13 824 | 32×3×24×6 |
| **Total** | | **32 256** | |

Les **576 opportunités World** (32×3 générations×3 familles×2 répétitions) et les **192 identités des World G2 de réserve** sont figées et publiées **avant la première naissance** ; ces World G2 ne servent pas au classement des parents. G1 et G2 sont des lignées propres à chaque bras. Au total, 768 fondateurs et **4 608 mutations de descendants** sont planifiés par exécution (3 bras×24×32 populations×2 générations).

*Justification déclarée, pas un pouvoir établi* : une différence S−M de **10 pas** est retenue comme taille minimale intéressante (2,5 % de l'horizon 400). La dispersion interpopulation historique de Stage8-A sur S−U déduite de son intervalle de confiance vaut ≈18,012 pas. C'est une **hypothèse de dimensionnement par procuration, non une estimation S−M**. Le calcul normal approximatif \`n≈((1,96+0,84)×18,012/10)²≈25,4\` suggère n=32 avec marge pour le t, **uniquement si** la future variance S−M est comparable. Si S−M est plus variable ou l'effet plus petit, l'étude sera sous-puissante ; aucun ajout de populations, sélection d'échantillon ou deuxième essai post hoc n'est autorisé. Toutes les hypothèses de Student (indépendance populationnelle et approximation de la distribution) restent **non démontrées**.

## Bras génétiques : mécanisme non imposé aux organismes

S sélectionne les parents à partir des **six vies G0/G1 déjà archivées et scellées**, rangées par nombre de censures à 400, puis durée vécue et slot. Poids linéaires 24..1, tirages avec remise. U tire avec remise uniformément **sans lire les scores de persistance**. M prend les **24 indices de parents effectivement choisis par S**, applique à leurs indices une **bijection HMAC-SHA256 préallouée et indépendante** pour cette population et génération, et utilise exclusivement **les propres 24 génomes parentaux M** pour fabriquer ses enfants. Ainsi S/M partagent **exactement le multiensemble des nombres de descendants par parent**, pas nécessairement l'identité des gènes ni la diversité fonctionnelle.

Les trois bras mutent les gènes v4 avec des graines indépendantes préfixées, au même \`scale=0.1\`. Aucune mémoire, place, récompense du World, fait caché ou état mental vécu n'est transmis. Le moteur P1.3 funded-v2, les frais en énergie et vigilance, la perception, la mort irréversible, le générateur de World et l'autorité motrice **ne sont pas modifiés**. Les 3 bras exposent leurs descendants aux **mêmes identités de World** dans une génération ; les générations ont des World différents. Une permutation indépendante peut, par hasard, associer de bons parents M à une haute multiplicité : elle ne force pas une corrélation constatée nulle.

## Une répétition technique complète, deux fois obligatoirement

Exécution au même SHA source et ensemble de fichiers Python du dépôt, **deux nouvelles racines d'entropie OS distinctes**, l'une Python **3.11**, l'autre **3.12**, chacune avec **32 256 vies natives originales** et **18 phases G/S/R chaînées** (neuf par panneau), soit **64 512 vies techniques au maximum**. Les deux répétitions ne sont pas deux essais de l'hypothèse scientifique, mais une vérification intégrale des coûts réels, du transport et des archives.

Ordre obligatoire pour chaque répétition :

1. Sur un Git HEAD propre et exact, fixer un nouveau plan allouant tous les World, ancêtres, permutations, tirages et mutations. Écrire le plan sous son SHA-256 canonique et **publier l'artefact plan AVANT la première vie**.
2. Réclamer une seule fois le dossier d'archive par création atomique, écrire \`CLAIM.json\`. Une panne laisse \`FAILURE.json\` et consume cette allocation : **pas de relance, nouveaux dossiers ou racines de remplacement**.
3. Générer G0, sceller et vérifier tous les originaux gzip et les paiements énergie/vigilance, puis sélectionner les parents G1. Même processus jusqu'à G2. Les 18 étapes de génération/scellé/sélection/réduction sont enchaînées par SHA-256, y compris les mutations, filiations et la trace de vie.
4. Relire **chacune des 32 256 vies originales** depuis gzip, vérifier SHA compressés/décompressés, graines, moteur, facture cognitive, décès/censure, génome, World appariés et ASCENDANCE. Reconstituer **4 608 filiations et mutations** (dont **1 536 filiations M**) à partir des génomes parentaux, des tirages et des graines scellés, puis comparer bit à bit les descendants et les reçus d'ascendance.
5. Publier un reçu technique et toutes les archives (y compris résultats défavorables et morts). Le reçu technique ne divulgue **aucun contraste S−M, signe, p-value ou succès scientifique**. Le contrôle final n'annonce \`STAGE8C_TWO_TECHNICAL_REPETITIONS_COMPLETE_NO_SCIENCE\` que si les **deux** reçus complets du **même workflow HEAD** ont SHA source identique, graines/Worlds/archives disjoints, 32 256 vies rehashées chacun et 18 phases chacun.

Les preuves sont internes à GitHub et à rétention limitée, non une attestation off-host. Sauvegarder les ZIP originaux et empreintes en dehors de l'échéance de rétention.

## Séparation irréversible de la future cohorte scientifique

**Cette livraison n'a pas d'entrée \`allocate-science\`, \`run-science\` ni job scientifique.** Une naissance G0 scientifique à l'avenir nécessitera un nouveau transport source-locké et un nouveau plan \`scientific_admission=true\` avec une **troisième** racine d'entropie OS, distincte des deux techniques, qui vérifie les **deux reçus scellés complets avant publication**, en conservant strictement le présent effectif, le critère primaire, les contrôles et la règle de non-relance. Ce plan scientifique devra être publié sous empreinte avant tout World, puis soumis à un audit indépendant des **32 256** originaux gzip. Les données techniques ne peuvent servir à retoucher la méthode ou choisir des graines avantageuses.

**L'achèvement technique ne démontre aucun gain génétique héréditaire**. Stage8-A demeure positif pour sa moyenne G2 ; Stage8-B demeure négatif pour son interaction F0 (\`p=0,65777\`) ; Stage7 demeure négatif pour sa règle 13/16. I1 reste le runtime actif et I3 la référence de développement non enregistrée ; Stage2.1 science \`NOT_ISSUED/HOLD_NO_VERDICT\`.

[Suivi scientifique #1438](https://github.com/josselin-orta-lab/individual-zero/issues/1438).
