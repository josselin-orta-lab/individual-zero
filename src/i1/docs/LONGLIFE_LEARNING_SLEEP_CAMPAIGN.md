# I1 : campagne prospective vies longues, équilibre apprentissage / sommeil

## Question et base

Peut-on identifier une **plage de pression** qui autorise une mémoire consolidée **utile** sans sacrifier survie, exploration, hydratation et alimentation ? Étude distincte de la campagne 0.20 close NO-GO. Branche de recherche basée sur le correctif I1 testé de PR #296 (`f91c738a`) ; ce correctif restaure le sommeil physiologique admis et **ne modifie pas I0**. Branche principale au départ `75762dc`; poids canonique `w_F=0.65` reste inchangé. Aucun apprentissage des données historiques cassées.

## Intervention strictement expérimentale

Le **coefficient** (w_F) de la fatigue dynamique (F_cog) est modifié **en mémoire avant chaque naissance** dans un process par bras ; bras 0, 0.05, 0.1, 0.15, 0.2, 0.3, 0.65. Pas de fixation forcée de l'état de fatigue et pas d'injection d'actions. Variations physiques déterministes indexées par hash du monde préenregistré + identifiant de variante : positions de sources hydriques et récoltes déplacées dans un rayon de trois cases, spawn/hazards/obstacles conservés. Les layouts restent **secrets pour I1** ; seul l'opérateur les archive. La carte Oasis conserve sa source hydrique et son aliment au spawn, afin d'avoir un contrôle abondant ; les autres layouts varient. Les graines de tempérament sont appariées entre les bras. Aucun monde expérimental n'est un retour dans le passé d'un individu : **nouveau-nés distincts**, morts irréversibles, WAL chaînée vérifiée.

Le labo exécute automatiquement un **pilote rapide** (4 mondes x 4 poids x une variante x une vie x 300 pas max), puis une campagne manuelle de 5 / 20 / 30 variantes à 300 / 800 / 1600 pas. L'automatisme CI est limité, la matrice longue n'est pas ajoutée aux vérifications ordinaires. Les autres trois valeurs peuvent être ajoutées à une campagne séparée quand les premières limites techniques sont levées ; ne pas comparer des commits moteurs différents dans un estimateur unique.

## Observables et mécanismes

Télémétrie externe passive pour chaque vie : pas et actions exécutées, type de commande par fenêtre de 50 pas, part de sommeil, actions non dormir/attendre, eau et nourriture minima, pas avec eau nulle, fin de vie ou censure à horizon, `stage10_consolidation_committed`, `memory_recall_proposed` et `i1_private_procedure_recall_considered` avec IDs d'événements. SHA Git, SHA layout, graine, variante, identité, poids effectif et hash de WAL conservés.

**La somme des événements de consolidation n'est pas l'apprentissage.** Les courbes de performance ne doivent mesurer que réussite différée : nombre de pas/actions pour boire ou manger après avoir réellement perçu une ressource auparavant ; capacité à rejoindre une ressource précédemment trouvée hors perception immédiate ; retour d'expérience déjà vécu dans le même contexte ; vérification du plan/action/issue avant et après consolidation. Déterminer séparément la rétention des formes sémantiques par propriétaire et la réutilisation dans la décision. L'analyseur actuel indique explicitement `NOT_ESTABLISHED` pour ces derniers endpoints ; leurs courbes ne seront produites que lorsque les preuves causales sont capturées dans la WAL et validées. Pas de reconstruction contrefactuelle par information opérateur.

## Plan statistique et seuils de décision

Les **unités indépendantes d'environnement** sont les variantes de carte, regroupées en clusters par monde et variante. Les comparaisons doivent être **appariées** au niveau de variante/graine/naissance et stratifiées par famille de monde. Tous les décès conservés ; les vies actives à horizon sont **censurées** et ne sont pas immortelles. Prévoir 30 variantes indépendantes par bras/méthode au niveau 3, avec IC bootstrap hiérarchiques à 95 % sur les cartes, puis analyses de sensibilité par famille. Une paire avec même carte et même graine ne signifie pas une même histoire après divergence des décisions.

**Seuils préenregistrés avant GO** : différence de survie à horizon 800 puis 1600 pas non inférieure à -5 points de pourcentage par rapport à `w_F=0` (borne inférieure IC unilatéral 95 % > -0.05) ; absence de sommeil >50 % sur le monde abondant et lorsque les besoins sont critiques ; consommation/boisson effectivement choisies quand elles sont subjectivement disponibles ; preuve d'une amélioration positive de performance différée avec ablation de rappel (pas seulement plus de souvenirs) et IC excluant zéro ; propriétaire(s) de mémoire ayant au moins une forme non vide, persistante et réellement consultée. **GO** uniquement si tous les axes passent. Si perte de survie ou sommeil pathologique significatif : **NO-GO**. Si données insuffisantes : **INCONCLUSIVE**. Une hausse de `committed` ne compense jamais une mortalité accrue.

## Commandes et traçabilité

Pilote par monde/bras : `python tools/run_i1_longlife_science.py --preset oasis --world-variant 1 --seed 773001 --steps 300 --lives 1 --custody wal --experimental-fatigue-weight 0.1 --observe-owner-digests --output-dir reports/oasis/v1/w01`.

Audit : `python tools/analyze_i1_longlife_science.py --input reports/oasis/v1/w01 --output reports/oasis/v1/w01/science-summary.json`.

Workflow GitHub `i1-longlife-learning-sleep.yml`. Paramétrage de 800 ou 1600 pas et répétitions uniquement à la demande. Les sorties `TECHNICAL_FAILURE` et les runs incomplets **ne sont pas des décès**. Aucun résultat ni verdict d'apprentissage ne peut être revendiqué sans les artefacts du SHA précis.
