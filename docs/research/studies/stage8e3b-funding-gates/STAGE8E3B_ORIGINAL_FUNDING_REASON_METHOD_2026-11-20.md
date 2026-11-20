# Stage8-E3B · Protocole de décomposition des pas sans action par financement et contrôle moteur

**Préspécification exploratoire du 20 novembre 2026 : `READONLY_POSTHOC_PROBLEM_CHOSEN_AFTER_E3A / NO_NEW_LIVES`.** Il ne s'agit pas d'une nouvelle hypothèse confirmatoire, ni d'une reprise des trois racines Stage8-E2 consommées. Le critère causal historique est clos **`STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0 / CLOSED_NO_RETRY`** et ne peut être réévalué. L'étude E3A a préalablement observé, descriptivement, chez S après swap gamma123, **+2,30 points d'inactivité physique** par pas vécu et moins de sommeil et cognition financée. [Source vérifiée E3A](../stage8e3a-original-motor-cost/STAGE8E3A_ORIGINAL_G2_MOTOR_COST_RESULT_2026-11-20.md).

## Question ciblée

La hausse d'inactivité `None` (à distinguer de l'action volontaire `attendre`) se compose-t-elle, dans les **vies déjà vécues**, de pas où :
- `NO_PROCESSING_BUDGET` : l'individu ne peut payer la préparation de la décision ;
- `NO_FUNDED_SCORE` : la préparation a commencé, aucun plan n'a pu être évalué avec le budget de calcul disponible ;
- `NO_FUNDED_MOTOR` : les options évaluées existent, mais toutes les commandes sont rejetées par les contrôles moteurs ;
- `FUNDED` : au contraire, une action motrice admise a effectivement été exécutée.

Ces **quatre champs exacts** proviennent du `info.funding` natif de `src/i3/modules/mind.py` **dans chaque trace de première personne**. Ils ne sont pas inférés rétrospectivement des réserves corporelles. `NO_FUNDED_MOTOR` ne révèle pas, à lui seul, le sous-motif exact de rejet moteur (dépense, géométrie, intégrité ou ressources). L'absence de sous-motif est consignée `NOT_IDENTIFIABLE`.

## Sources verrouillées et falsificateurs

- [Science source-figée #44637950471](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44637950471) ; moteur historique `03faff4b9c194a5288b92e394f6a75cbe62cd095` ; SHA-256 source `e816ff5f5ee679253fc57f6e9ee79d21dff73dd72d6adf3c7f55ba7aa0f3e7f6`. Original G2 : **36 864 gzip**, artefact GitHub `14601222013` ; manifeste original G2 SHA-256 `61eb74a1f429c2f9189ee13da5c52593776d2b6f9d2b2d8ac41bfdea31a6ba00`. Autres sources de cette exécution : métadonnées `14601206944`, audit original/primaires `14601838862`, second contrôle statistique `14601778656`.
- [E3A post hoc, workflow #44706318958](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44706318958) : `STAGE8E3A_FULL.json` SHA-256 **`16e69fdcb664f73b7d67fa6e620017dc30e78bec834ddb148a2c58c6b0939d8b`**, artefact `14615936609` ; `SECOND_REDUCTION.json` SHA-256 **`16040d0da069ac25bb3be014729a129f1202d2f7812b13c688466013f45be027`**, artefact `14615911856`. E3A contient déjà les 64×4 taux d'inactivité complets ; la somme E3B des trois causes doit les **reproduire exactement**, pas modifier la population analysée.
- **Rehash intégral obligatoire** de chaque gzip original comprimé et de son JSON décompressé, identités, source, génotype, World, 9 chaînes parentales préalablement auditées, traces physiques et coûts cognitifs payés. Aucune comparaison S/M n'est acceptée avant vérification des **36 864 / 36 864** sources et des **256 cellules population×bras (144 vies chacune)**.
- Chaque pas possède un champ `info.funding` strictement dans les quatre catégories, exactement **un** motif ; `None` exige l'une des trois raisons d'échec, une action non nulle exige `FUNDED`. `attendre` est compté uniquement comme action motrice admise, jamais comme inactivité. Tout conflit, motif absent, compte divergent, action non financée présentée comme financée ou originaux manquants invalide **tout** le tableau.
- Les pas `NO_PROCESSING_BUDGET` ne déclarent **aucun travail de décision payé**, selon la branche originale du moteur. Les réserves d'énergie et vigilance **avant décision** sont vérifiées et sommées par motif ; toute moyenne d'un motif absent est `null`, jamais zéro artificiel.

## Tableau descriptif, sans seuil ni p-value

Pour chacun des 64 `p` et des quatre bras S_sham/M_sham/S_swap/M_swap, compter chaque motif par **pas effectivement vécu**, et séparément les **20 premiers pas observés de chaque vie**. Les décès précoces diminuent le dénominateur initial, sans imputation. Conserver les totaux absolus et la moyenne des réserves énergie/vigilance **avant chaque motif**, notamment les proportions de réserves inférieures à 10. Les proportions de quatre motifs doivent sommer à **1** pour chaque cellule.

Agrégation **à poids égal des 64 populations**, non des individus traités comme indépendants. Pour les huit descripteurs (quatre motifs × deux fenêtres), fournir les moyennes des bras, le contraste `(S_sham−M_sham)−(S_swap−M_swap)`, les deux variations `S_swap−S_sham` et `M_swap−M_sham` et les **64 contrastes descriptifs intégraux**, y compris tous signes défavorables. La somme DID des trois motifs d'échec doit égaler **le DID d'inactivité E3A −0,02915478521145825** ; celui de `FUNDED` doit être opposé.

Aucun test confirmatoire, valeur `p`, « médiation » ou promotion gamma3 n'est autorisé. Même un changement de motif observé n'identifie pas une cause unique de survie ou une intervention gene-specific. Les taux par pas sont sensibles à la composition des survivants. Contrôles indépendants sur le tableau complet, sur une autre version de Python, **après** tous les gzip.

**Arrêt :** toute divergence donne **`NO_DESCRIPTIVE_REPORT`**, pas une relance biologique. Réparer un outil d'audit en nouvelle source est distinct de la répétition interdite des 193 536 vies historiques. Les archives sont conservées seulement 90 jours dans Actions et nécessitent l'export durable de [#1463](https://github.com/josselin-orta-lab/individual-zero/issues/1463). I1 actif, i3 non promu, Stage2 général `NOT_ISSUED/HOLD_NO_VERDICT`.
