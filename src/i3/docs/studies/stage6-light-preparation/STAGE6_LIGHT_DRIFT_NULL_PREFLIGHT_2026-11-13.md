# I3 — modèle nul de dérive pour l'étape 6 légère : préflight (13 novembre 2026)

**Statut : PRÉFLIGHT GELÉ AVANT CODE.** Ce document fige un calcul de dimensionnement sans aucune vie. Il ne produit aucun verdict scientifique, aucun GO et aucune autorisation de monde. Il ne lance pas l'étape 6 légère.

**Base :** `main` = `24dadc509e3a96339def0ddb5f68c257feeabf08`, plus les trois commits de la [lecture descriptive de P3](P3_GENE_SHIFT_DESCRIPTIVE_RESULTS_2026-11-13.md). **Worlds et vies créés :** 0.

## 1. Question et décision visée

**Question.** Quand un gène n'a aucun effet sur la persistance, de combien le contraste entre le bras sélectionné et le bras à parents aléatoires s'écarte-t-il de zéro par simple dérive, selon la taille des populations et le nombre de générations ?

**Décision que le résultat peut changer.** Trois paramètres du futur protocole de l'étape 6 légère : le nombre de génomes par population, le nombre de générations et le nombre de populations. La lecture de P3 a montré que six génomes et deux tours de sélection laissent un à quatre fondateurs par population. Il faut donc choisir ces paramètres par un calcul et non par habitude.

## 2. Modèle figé

Le modèle ne manipule que des nombres. Il n'importe ni `World`, ni `Mind`, ni `run_life`, ni aucun runner.

- **Population.** `N` génomes fondateurs, identiques dans les deux bras (génération 0 appariée), puis `G - 1` tours de reproduction, soit `G` générations en comptant la génération 0.
- **Règle des parents.** Celle de P3, généralisée à `N`. Bras `selected` : chaque descendant tire son parent avec des poids linéaires `N, N-1, ..., 1` selon le rang de persistance. Bras `random_parent` : tirage uniforme.
- **Mutation.** Celle de `genome.mutate` : bruit gaussien d'écart-type 0,1 fois l'étendue du gène, puis troncature aux bornes.
- **Deux régimes de rang**, qui encadrent le cas réel pour un gène sans effet.
  - `fresh` : le rang est retiré au hasard à chaque génération. La persistance n'est pas héritable.
  - `heritable` : chaque fondateur reçoit une valeur latente, transmise à l'identique à ses descendants, et le rang suit cette valeur. La persistance est entièrement héritable, ce qui accélère la perte de fondateurs.
- **Quantités suivies.** `z`, un gène générique normalisé, uniforme sur [0 ; 1] à la génération 0. Et `beta_u_eff = b * (1 + 0.5 * e)`, avec `b` uniforme sur [0 ; 2] et `e` uniforme sur [-1 ; 1], comme dans le génome.
- **Contraste.** Pour chaque population simulée, `C = moyenne(selected, dernière génération) - moyenne(random_parent, dernière génération)`.

## 3. Grille, répétitions et graine

- `N` dans {6, 12, 24, 48}. `G` dans {3, 4, 6, 8}. Deux régimes. Soit 32 configurations.
- 4 000 populations simulées par configuration.
- Générateur : `random.Random`, graine textuelle `i3-stage6-light-drift-null/v1` complétée par la configuration et le numéro de répétition. Le résultat est un JSON canonique avec son empreinte SHA-256.

## 4. Sorties figées

Pour chaque configuration et chaque quantité : moyenne de `C`, écart-type de `C` et part des contrastes positifs. Pour chaque bras : nombre moyen de fondateurs encore représentés à la dernière génération. Pour `z` : part moyenne des génomes aux bornes.

**Plus petit déplacement détectable.** Le critère du plan est un accord de signe entre populations. Pour `P` populations, le seuil `k` est le plus petit nombre de signes concordants dont la probabilité bilatérale exacte est d'au plus 0,05. Le plus petit déplacement détectable à 80 % de puissance est `c(P, k) * écart-type de C`, où `c` vient de l'inversion exacte de la loi binomiale et d'une approximation normale du contraste par population. Il est donné pour `P` dans {8, 12, 16}.

**Coût en vies.** `P * G * N * 6 * 2` : six vies par génome (trois familles F0, deux répétitions, comme P3), deux bras, horizon 400.

## 5. Contrôles de cohérence, déclarés avant exécution

- **S1, ordre de grandeur.** Pour `N = 6` et `G = 3`, l'écart-type de `C` pour `z` doit se situer entre 0,10 et 0,45 dans les deux régimes. Cette fourchette large entoure les écarts-types observés entre populations pour les deux marqueurs neutres de P3 (0,224 et 0,330, sur quatre populations seulement).
- **S2, symétrie.** Pour `z`, dans chaque configuration, la moyenne de `C` doit rester à moins de quatre erreurs types de zéro, et la part des contrastes positifs à moins de quatre erreurs types de 0,5.
- **S3, déterminisme.** Deux exécutions donnent la même empreinte.

Si S1 ou S2 échoue, le verdict est `DRIFT_NULL_MODEL_INADEQUATE` et aucune recommandation n'est émise. Pour `beta_u_eff`, les mêmes statistiques de symétrie sont rapportées. Un écart n'invalide pas le modèle, mais il est signalé par `COMPOSITE_NULL_ASYMMETRY` et doit être repris dans le protocole.

## 6. Règle de recommandation, déclarée avant exécution

L'écart-type de `beta_u_eff` entre génomes fondateurs vaut 0,667 (calcul exact sur les lois uniformes). La configuration recommandée est la moins coûteuse en vies dont le plus petit déplacement détectable de `beta_u_eff`, dans le régime `heritable`, ne dépasse pas la moitié de cet écart-type, soit 0,333. En cas d'égalité, on retient le moins de générations. La configuration la moins coûteuse pour le seuil d'un quart (0,167) est aussi rapportée.

Ce seuil d'une moitié est un choix de conception **(hypothèse)**. Il correspond à un gène modérément lié à la persistance. Le propriétaire peut en retenir un autre : le tableau complet est publié pour cela.

## 7. Ce que ce calcul ne peut pas donner

- **La réponse à la sélection.** Seules des vies la mesurent. Le modèle dit quel déplacement serait visible, pas s'il existe.
- **Un test rétrospectif de P3.** Le modèle ne sert pas à juger après coup le contraste observé dans P3. Seul un essai prospectif sur des populations neuves peut le faire.
- **L'héritabilité réelle de la persistance.** Le régime `heritable` est une borne de travail, pas une mesure.

## 8. Plus petit test exécutable et coût

- Tests sans World : comptages exacts sur une population minuscule, seuils binomiaux comparés à des valeurs calculées à la main, déterminisme, imports interdits.
- Coût : 0 World, 0 vie, environ une minute de calcul, un module de laboratoire et un fichier de tests.
