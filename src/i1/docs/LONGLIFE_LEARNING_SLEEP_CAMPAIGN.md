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


## Premier lot observé et amendement prospectif A1 (2026-10-18)

**SHA du premier lot :** `3938913fea8e600aead19f25b38bd39063481a58`, [Actions #39112506390](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39112506390). La CI logicielle du commit de protocole `08059828` est [verte](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39112553248). Les simulations du premier lot se terminent indépendamment, et les résultats partiels ne sont pas un verdict comparatif.

Premier bloc de vie Oasis, variante physique 1, graine 773001, **une vie par bras**, horizon 300 :
- poids 0.0 : morte au pas 295, 94 `dormir` (31,9 %), eau nulle durant 108 pas ;
- poids 0.1 : morte au pas 297, 104 `dormir` (35,0 %), eau nulle durant 110 pas ;
- poids 0.2 : morte au pas 299, 122 `dormir` (40,8 %), eau nulle durant 112 pas ;
- poids 0.65 : active, *censurée au pas 300*, 240 `dormir` (80 %), eau nulle durant 113 pas, intégrité physique seulement 9,4.

Ces chiffres proviennent de l'inspection des quatre rapports et journaux WAL téléchargés depuis [les artefacts du lot](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39112506390). Aucun coefficient ne peut être déclaré supérieur avec une seule paire de cartes, une forte mortalité de déshydratation et une censure à 300. Malgré la présence de sources dans la carte opérateur, **aucun individu ne se trouvait à une source d'eau au moment où son hydratation était critique**; ne jamais remplacer ce fait par l'hypothèse qu'il connaissait la source.

**Amendement préanalytique distinct pour la suite, pas rétroactif** : nouveau preset `longlife-garden` avec 49 positions hydriques réparties, nourriture stationnaire abondante, zéro piège létal, aucun mécanisme de ravitaillement forcé. Son SHA de layout varie avant chaque naissance sous la même règle `i1-longlife-layout-v1`. Ce monde sert de témoin favorable au maintien d'une vie longue, **pas** de preuve de l'apprentissage spatial dans un monde rare. Il possède sa propre strate analytique : ne jamais regrouper naïvement avec la première série. Les mondes et physiques antérieurs sont conservés tels quels.

Ce complément ne rend ni l'absence de recul mnésique ni un apprentissage non observé démontrés. Les résultats restent `NOT_ESTABLISHED` jusqu'au traçage contenu -> récupération -> décision -> résultat physique différé.

## Série prospective B1000 : 40 nouvelles vies à horizon 1000 (2026-10-18)

Cette série **distincte** est déclenchée par [I1 1000-step paired sleep and learning](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39113415179), SHA d'exécution prévu `32761a6b715c5763a115522766fa9d9d275b2a7c`. Plan fixé avant analyse : cinq mondes (oasis, foraging, dry-valley, blocked-route, longlife-garden), poids 0/0.1/0.2/0.65, variantes de ressources **101 et 102** appariées avec graines 880101 et 880102, une naissance mortelle par cellule, soit 40 individus indépendants par identité mais seulement deux paysages tirés par monde. Horizon maximal **1000**, arrêt irréversible à la mort, aucun survivant exclu, sommeil non forcé. Les poids sont des perturbations expérimentales in-memory avant naissance ; le canon de `main` et I0 sont inchangés. Exécuter `tools/summarize_i1_1000_cohorts.py --input <dossier-reports-complet> --output <dossier-sortie> --sha <sha-physique-exact> --variants 2 --variant-start 101` **après récupération de tous les 20 artefacts et inspection des erreurs éventuelles**. L'agrégateur échoue si des cellules manquent, si les physiques varient entre bras appariés ou si plusieurs commits sont mélangés. Ne pas publier d'effets d'apprentissage causaux ni d'IC convaincants sur seulement deux variantes. Toutes les vies vivantes au pas 1000 sont censurées, et une mort avant 1000 ne devient jamais un arrêt arbitraire de simulation. 
