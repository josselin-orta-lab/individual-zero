# Individual Zero · A2.30-ZO · préenregistrement prospectif d'un prédicteur factorisé à couverture et risques explicitement incomplets

**Date : 15 octobre 2026.** Référence de travail : #207 ZM/ZN, commit `95b8a91308c8a1ad7f68040fa01b50aa941c3564`. **Ce protocole est déposé AVANT tout code ZO, avant la première action physique ZO et avant tout résultat ZO.** Les résultats ZK/ZL, ZM/ZN sont déjà connus. Le tracker GitHub #110 a été fermé administrativement par d'autres travaux ; cette recherche ne le rouvre pas et ne prétend pas valider rétrospectivement l'autonomie d'I0.

## Question falsifiable

ZM/ZN montre que la mémorisation exacte `SimulationState complet × commande` manque de couverture dès qu'énergie, nourriture, eau ou horloge changent, y compris après retour aux mêmes coordonnées. **ZO** demande si un modèle **strictement expérimental et externe** des *variations de quelques variables directement observables* peut généraliser à des coordonnées, valeurs corporelles et phases diurnes non rencontrées à l'entraînement, tout en révélant explicitement ses limites lorsqu'un échec d'action ou danger physique est caché.

La modélisation ZO **ne** produit **pas** de `EquipmentPrediction`, `SimulationState` complet, `safe`, probabilité de risque, `terminal=False`, ni commande autonome. Elle estime uniquement les deltas empiriques `dx,dy,energy,food,water,inventory.berry_b` du mouvement est ou de la collecte B, lorsque ces deltas sont invariants dans ses exemples de formation. **`integrity`, `terminality`, `next-adjacent/remote features` et la sûreté restent systématiquement `UNKNOWN`**, même sur les exemples non terminaux et lorsque les six deltas numériques sont parfaitement prédits. Aucune supposition sur les coûts physiques connus du banc ne peut être injectée dans la fonction d'estimation.

## Matrice physique avant résultats : exactement 120 mondes indépendants, 120 actes physiques

Utiliser `physical_fixture_config()`, grille 32×32, configuration de laboratoire non normative, action énergie `se_deplacer=1.0`, `collecter=0.75`, `food_decay=0.5`, `water_decay=0.2`, intégrité initiale 100, créature/danger absent sauf contrôle déclaré, baie `berry_b` quantité 2 **sur la position courante** dans chaque monde. Ne **jamais** exécuter `manger`. Les deux commandes fixées avant action sont `se_deplacer(east)` et `collecter(berry_b)`, chacune éligible dans la perception initiale. Effectif et cellules :

| Bras | Facteurs | Mondes | Actes attendus |
|---|---|---:|---:|
| **TRAIN** | positions `(5,5),(7,7)` × food `35,45` × t0 `1(day),201(night)` × commande `MOVE_E,COLLECT_B`; énergie 50, eau 40, effet B bénin | **16** | **16** |
| **NOMINAL HELDOUT** | positions `(9,9),(11,11),(13,13),(15,15)` × corps `(energy,food,water)=(35,25,30),(70,55,65)` × phase `1,201` × commande `MOVE_E,COLLECT_B` × B latente `benign,toxic_lethal` | **64** | **64** |
| **HIDDEN INTERVENTION HELDOUT** | mêmes quatre positions × commande × `hidden_lethal_east`, `hidden_danger_here`, `hidden_forced_action_failure`, au t0=1 et corps `(35,25,30)`, B bénigne | **24** | **24** |
| **CLAMP-BOUNDARY HELDOUT** | quatre positions × commande × t0 `1,201`, corps `(0.5,0.25,0.1)`, B bénigne | **16** | **16** |
| **TOTAL** | mondes/identités indépendants, exactement une application physique chacun | **120** | **120** |

Les paramètres cachés de B `benign=(food_gain=12, integrity_delta=0)` et `toxic_lethal=(food_gain=12, integrity_delta=-100)` ne concernent **que l'ingestion**, qui reste interdite. Les observations initiales et les deltas non ingestifs des deux mondes jumelés sont donc attendus identiques. Le banc peut utiliser les labels cachés **uniquement après action pour scorage externe**, jamais dans l'entrée du prédicteur.

**Trois contrôles hors distribution :**
- `hidden_lethal_east` : zone létale uniquement à la case située à l'est. Attendus **4 décès moteurs** (MOVE_E), contre quatre collectes survivantes. Zone invisible avant action ; aucune perception vécue après un décès.
- `hidden_danger_here` : `danger_zone_damage=10` au lieu actuel ; attendu **8 dommages d'intégrité invisibles** (4 mouvements ? Attention : le mouvement est quitte la case. Pour produire exactement huit dommages, placer les zones dangereuses sur la case de destination **du geste** : à l'est pour MOVE_E, sur place pour COLLECT_B). Le même `SimulationState` préaction que le nominal est attendu.
- `hidden_forced_action_failure` : un programme d'échec physique sur la primitive effectivement engagée, non exposé à Perception ; attendu **8 effets primitifs supprimés** (MOVE_E reste sur place ou COLLECT_B ne fournit aucune baie), mais coût corporel/temps toujours appliqué.

Le préenregistrement prévoit **4 décès**, **8 dommages d'intégrité** et **8 échecs d'effet primitif** dans les 24 mondes d'intervention. Dans le bras limite, le calcul des deltas non bornés mènerait à des valeurs négatives; le prédicteur doit donc **s'abstenir dans 16/16 cas**, sans convertir les observations en états physiques impossibles.

## Séquence et gel des modèles

1. Construire et exécuter physiquement les **16 mondes TRAIN indépendants**, enregistrer avant/après, commande, phase, date relative, SHA de corpus, terminal externe. **Geler** avant toute création de monde HELDOUT :
   - `FrozenTableEquipment` exact baseline, entraîné seulement sur ces 16 exemples.
   - prédicteur partiel : grouper les exemples uniquement par **commande visible** (`MOVE_E` ou `COLLECT_B`), mesurer six deltas sur les huit exemples d'un groupe; si l'une des six valeurs varie ou qu'un exemple est terminal, marquer le composant `UNSUPPORTED` et ne jamais émettre de valeur unique pour lui. Aucune lecture des coordonnées, corps ou paramètres cachés des futurs mondes pour calibrer ces deltas.
2. Fixer un seuil mathématique d'abstention **à partir des deltas déjà appris** : si `energy`, `food`, `water` avant l'action sont inférieurs à la diminution apprise, `ABSTAIN_CLAMP`. Les cas inconnus et commandes non candidates valent `ABSTAIN`.
3. Créer **ensuite** les 104 mondes HELDOUT ; effectuer la prédiction depuis le `SimulationState` préaction, figer ce reçu et son SHA, puis **seulement alors** appliquer la commande au `WorldBody`. Ne pas utiliser le résultat physique pour adapter le modèle. Toute correction de modèle après observation HELDOUT invalide la comparaison prospective.
4. Calculer les taux séparés, avec dénominateurs exacts : `TRAIN=16`, `NOMINAL=64`, `HIDDEN=24`, `BOUNDARY=16`. Publier les erreurs par composant, toute prévision de déplacement/collecte erronée, les 4 décès avec capture externe finale, la couverture du modèle exact original sur les 104 premiers états heldout, et le nombre `UNKNOWN` pour intégrité et terminalité. **Jamais** déclarer qu'une prédiction partielle « sûre » pourrait être exécutée par Stage6 sans un nouveau contrat.
5. Les résultats des deux versions Python 3.11/3.12 correspondent aux **mêmes 120 recettes déterministes**, pas à 240 expériences indépendantes. En cas de divergence, publier et conserver les deux résultats ; ne pas supprimer les cas adverses.

## Attentes, sans hypothèse de sûreté

Sur le bras NOMINAL avec corps loin des limites et physique visible identique à la formation, les six deltas d'un groupe sont supposés invariants (**hypothèse à réfuter** par 64 actions). Le modèle exact d'entrée complète est censé refuser les 64 racines inédites, alors que le modèle partiel devrait produire des estimations. Sur les 24 interventions cachées, certains deltas peuvent rester justes mais **aucune prévision valide de sûreté n'existe** : la létalité, la blessure et l'échec masqué ne sont pas inférables à partir du seul visible. Un modèle qui en conclurait `safe` ou `terminal=False` échoue automatiquement. Sur les 16 cas aux frontières, la bonne action du prédicteur est **abstention**.

**Important :** « invariance sur un petit échantillon » n'est pas loi générale. Une variante cachée `set_action_failure_schedule` peut violer le mouvement nominal à observation constante. Un état observé en t0 n'autorise pas à prétendre connaître toutes les nouvelles ressources/obstacles visibles depuis le t1. L'absence de dommages d'intégrité dans les données d'entraînement ne permet pas de prédire zéro blessure.

## Contrôles adversariaux obligatoires

SHA source falsifié; ajout de `WorldPhysicsConfig` ou `lethal_zone` à la perception d'entrée; échantillon HELDOUT ajouté à TRAIN; réétiquetage `terminal=False` à la place de `UNKNOWN`; fausse sûreté ou inventaire B après échec physique; fusion des deux variants cachés en un seul dénominateur; voisin distant prédit sans perception; erreur sur les bornes clamped; commande B ingérée; postmortem fictif; trajectoire avec deux actes; métriques revendiquant UC réelle, cognition autonome ou mémoire I0 personnelle. Tous doivent être refusés et les erreurs honnêtement reportées.

**Statut initial :** PR de science externe seulement ; données ZO = 0, aucun PASS revendiqué. Stage12/attribution causale/autonomie alimentaire non validés par ce protocole. Ne pas modifier `src/i0`, Stage9/DC-05, M11, Oracle, UC, MVP v1.3.1, ni transformer automatiquement en PR fusionnable. La clôture administrative de #110 ne remplace pas la preuve subjective manquante.
