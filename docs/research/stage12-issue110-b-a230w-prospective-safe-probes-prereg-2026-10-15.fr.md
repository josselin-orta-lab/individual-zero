# A2.30-W : préenregistrement prospectif, recherche de signaux alimentaires avant ingestion

**15 octobre 2026, AVANT l'écriture du runner W, des tests W et de toute exécution physique W.** Référence GitHub : PR #193, commit `00363bd1371d3998990027a9ba34c7276ffcec0f`, branch de recherche W issue de ce commit. Issue #110 ouverte, Stage12 PARTIAL, A2.30 PARTIELLE. Les études antérieures S (PR #190), S-causal (PR #191), T/U (PR #192) et V (PR #193) étaient connues **avant** le présent protocole : elles démontrent notamment l'aliasing initial, 56 racines Stage6 non prédictibles et une limite pour les choix alimentation/abstention dans la matrice T. **W utilise de nouveaux mondes physiques mais reste dans la même famille de physiques déterministes**, pas une preuve statistique indépendante sur un milieu naturel.

## Question, règles de perception et résultats inconnus

**Question :** une sonde réellement exécutée, non létale et n'impliquant aucune ingestion, peut-elle révéler avant exposition une différence entre `berry_a` bénigne, nocive, létale ou dépourvue de valeur alimentaire, **sans créer de nouveau canal perceptif ni connaître la configuration latente** ? Les états accessibles proviennent exclusivement de `SymbolicPerception.capture` + `state_from_capture` sur `WorldBody.capture_local` et `telemetry`. Les étiquettes latentes et effets physiques restent hors du calcul de discrimination et sont utilisés **seulement** par le laboratoire pour grouper les mondes avant l'audit et vérifier leurs conséquences.

Préenregistrer les trois hypothèses :
- **W1 (sous la physique actuelle) :** les cinq variantes cachées de `berry_a` produisent la **même histoire complète des `SimulationState`** pour chacun des quatre préfixes sans ingestion, à état initial et préfixe fixés. Si une différence apparaît **avant ingestion**, publier son pas et le champ exact ; ne pas masquer la découverte.
- **W2 (témoin positif) :** le même instrument perceptif doit distinguer, avant toute action, une baie `berry_b` visiblement différente de `berry_a`, ainsi qu'un voisin ouest rendu infranchissable. Le test ne suggère PAS que voir une espèce garantit sa sûreté, seulement que des signaux réellement exposés par Stage3 sont détectables.
- **W3 (coût et choix alimentaire borné) :** toutes les sondes préengagées non alimentaires doivent être effectivement appliquées avec coût corporel mesuré. Après chaque sonde, une séquence laboratoire `collecter(berry_a)` si nécessaire, puis `manger(berry_a)` est appliquée afin de **vérifier externe** les conséquences de chaque variante ; les résultats des ingestions ne servent **jamais** de caractéristiques avant décision. Le laboratoire ne déploie aucun plan ni politique chez I0. Pour les **80 mondes agis** regroupés en 16 classes de pré-exposition (4 préfixes × 2 nourritures × 2 positions), vérifier si toute décision `commit food prefix/abstain` fondée sur l'histoire observable doit choisir la même sortie pour cinq conséquences distinctes.

## Matrice de mondes originaux W (figée)

Physique indépendante de tout I0 vivant : reprendre `build_physics("EAT", variant, food=..., position=...)` de P, sans reprendre son prédicteur ni son entraînement. Paramètres de P : monde 32×32, coûts d'action `attendre=0.5 énergie`, `collecter=0.75 énergie`, `manger=0.5 énergie`, `se_deplacer=1.0 énergie`, `food_decay_per_step=0.5`, `water_decay_per_step=0.2`, nourriture initiale 35 ou 45, position initiale (5,5) ou (7,7). La configuration latente de `berry_a` est choisie **avant** création du monde, parmi :
1. `benign` : gain nourriture +10, intégrité 0.
2. `toxin_7` : gain +10, intégrité -7.
3. `toxin_30` : gain +10, intégrité -30.
4. `toxin_100` : gain +10, intégrité -100, terminalité physique.
5. `gain_zero` : nourriture 0, intégrité 0.

**Quatre séquences de sondes, fixées avant les conséquences :**
- `immediate` : aucune commande avant décision, 0 pas de sonde.
- `wait_twice` : `attendre, attendre`, 2 pas de sonde.
- `collect_first` : `collecter(berry_a)`, 1 pas de sonde, inventaire et disponibilité visibles modifiés avant décision.
- `west_return` : `se_deplacer(west), se_deplacer(east)`, 2 pas de sonde. Terrain initial libre, aucun danger spatial artificiellement injecté.

**Plan factoriel :** 4 sondes × 5 variantes latentes × 2 niveaux initiaux de nourriture × 2 positions = **80 mondes physiques indépendants**, **100 pas physiques de sondes**, si aucune sonde n'est létale. Chaque monde reçoit ensuite les **commandes alimentaires expérimentales préengagées** : `collecter(berry_a)` pour `immediate`, `wait_twice`, `west_return`; puis `manger(berry_a)` pour tous, y compris `collect_first` qui a déjà collecté. **140 pas alimentaires** supplémentaires (60 collectes + 80 ingestions), soit **240 applications `WorldBody.apply`** en 80 mondes. Les **16 mondes `toxin_100`** meurent à leur ingestion et ne sont jamais exécutés de nouveau. Les conséquences postterminales sont des reçus externes, **jamais** des observations vécues utilisables pour une décision ultérieure.

**Témoins positifs purement perceptifs :** 2 nourritures × 2 positions × 3 mondes `resource_berry_a` (référence), `resource_berry_b` (substitution de la ressource locale, même quantité), `west_blocked` (même ressource `berry_a`, seule l'infranchissabilité ouest diffère) = **12 mondes détachés, zéro transition physique appliquée**, `SimulationState` initial enregistré à t1. Le contraste porte exclusivement sur les champs **visibles** et ne doit pas être utilisé pour prédire la toxicité cachée de `berry_a`. Comparaison positive attendue dans chacun des quatre contextes (famille ressource, passabilité). Ces 12 mondes ne sont pas entraînement du modèle (W **n'entraîne aucun modèle**).

**Total planifié : 92 mondes de laboratoire, 240 actions physiques effectivement appliquées, 16 décès externes, zéro I0.** Python 3.11 et 3.12 réexécutent les mêmes 92 conditions déterministes, donc **ne pas doubler ces effectifs**. Aucune graine stochastique n'est introduite par le plan.

## Définition stricte du début et de la fin de décision

- Conserver `initial` et chaque `post_probe_alive` pour les étapes de sonde dans une **histoire première personne** avec `before/after` accessibles uniquement si le monde survit. L'horodatage physique `t_monde` est conservé. L'histoire **ne** contient aucune donnée sur les effets internes de la baie ou l'Oracle.
- Une fois la sonde terminée, figer le **`decision_state` complet et l'histoire observable**. Un résultat de `collecter` dans `collect_first` est autorisé avant décision ; **aucune ingestion** n'est autorisée avant ce gel.
- La phase alimentaire après gel sert uniquement à vérifier le futur par le laboratoire. Mesurer le changement alimentaire entre le corps à la décision et le corps après ingestion ; succès si survie **et** variation d'au moins +5 nourriture sur l'ensemble du préfixe alimentaire. Une sonde n'est PAS un choix d'I0, donc la réussite alimentaire correspond seulement aux conditions physiques imposées et non à un objectif vécu.
- Une politique déterministe `f(histoire_pre_decision) ∈ {commit_protocole_food, abstain}` ne peut pas discriminer des mondes produisant la même histoire. Le certificat de sécurité est **limité à ces sondes/variantes/positions** et au choix de ce préfixe alimentaire contre abstention. À l'intérieur de la matrice, si une classe reste aliasée, engager entraîne 3 succès/survie, 1 terminal, 1 insuffisance. **Ne pas** généraliser à d'autres séquences de navigation, aliments ou mondes.
- Les coûts physiques de sondes doivent être reportés séparément (valeurs corporelles à t_debut et t_decision). Les coûts des opérations alimentaires sont mesurés à part. **UC et intentions d'I0 non mesurées.**

## Tests négatifs et reproductibilité

Écrire un test de non-régression rejetant : (i) un effet caché se retrouvant dans les états accessibles, (ii) une suite inventée après décès, (iii) une sonde létale présentée comme sûre, (iv) une différence visible supprimée par le comparateur, (v) une valeur post-ingestion injectée dans une histoire précédant l'ingestion, (vi) un monde dupliqué et (vii) un faux succès `safe`. Conserver les traces exactes, hashes des commandes, configurations physiques **seulement externes**, horodatages, terminaux et deltas. Rejeu identique sous Python 3.11 et 3.12.

**PASS technique** si matrice et protections reproductibles. **Résultat scientifique** : W1 doit être **testée**, pas imposée comme un axiome logiciel ; un échec de W1 signifie découverte d'un signal réellement accessible. W2 prouve seulement que le banc reconnaît des contrôles visuellement distincts. W3 borne l'information et les conséquences au protocole. L'absence d'observation discriminante n'implique pas l'impossibilité universelle d'une politique alimentaire sûre.

**Décision prévue : Stage12 PARTIAL ; A2.30 PARTIELLE ; issue #110 OPEN ; PR W DRAFT ; déploiement cognitif NO-GO.** Ne modifier ni `src/i0`, ni la spécification MVP v1.3.1, ni Stage9/DC-05, ni Oracle, ni mortalité WAL. Seul un arbitrage opérateur explicite peut autoriser l'intégration ou l'amendement normatif.
