# Stage8-F1J · appariement prospectif authentique des deux monnaies et quatre champs du calcul

**21 novembre 2026 · verdict primaire : `FIXED_ROUND_16_OF_16_REAL_COST_PARITY_DEMONSTRATED_LOCAL`.** Les **16/16** nouvelles histoires personnelles satisfont au tick T5 le **même travail cognitif natif complet et les mêmes paiements corporels énergie/vigilance**, sans commandes motrices forcées ni factures artificiellement remplies. Le résultat positif concerne **un nouveau contrôleur expérimental à tours de compétition substantiels fixes** et **non** le `Mind` de référence P1.3, ni une survie adaptative générale. **F1I conserve `INCONCLUSIVE_COST_GATE` avec ses 4/16 comparaisons non appariées.**

## Chronologie de la préexposition, vérifiable sous Git

- Grille de **16 nouvelles** graines, états corporels et ressources des quatre écologies figée **AVANT toute expérience F1J** : [STAGE8F1J_FROZEN_FIXED_ROUND_NATIVE_EQUAL_COST_GRID_2026-11-21.json](STAGE8F1J_FROZEN_FIXED_ROUND_NATIVE_EQUAL_COST_GRID_2026-11-21.json), commit `8f82eea7a8b08e086010dfe497099212fb35508f`.
- Hypothèses, mécanisme, limites, gates d'audit, critère de succès **16/16** et verdicts négatifs fixés **AVANT toute expérience F1J** : [STAGE8F1J_FIXED_ROUND_PAID_COMPETITION_PREEXPOSURE_2026-11-21.md](STAGE8F1J_FIXED_ROUND_PAID_COMPETITION_PREEXPOSURE_2026-11-21.md), commit `b90d6eb13459ddfda4f63c0828f4e39f135a376e`.
- Base de référence `main` `3745952a6c8635072828cdfbe3686229eebe50ba`. [PR #1499](https://github.com/josselin-orta-lab/individual-zero/pull/1499) contenant **seulement** les outils et tests F1J, les garde-fous CI et ses protocoles, sans modifier `src/i3/modules/mind.py`, `World.step` ni F1I.
- [CI scientifique native et audit indépendant #44910526201](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44910526201) : **2/2 jobs PASS**, 13 tests adversariaux PASS. 2 productions natives Python 3.11 **octet-identiques** ; audit indépendamment recalculé en Python 3.12, **stdlib uniquement, sans importer moteur, Mind ni producteur**.

**Ne pas confondre réplication et validation indépendante de F1I** : les 16 graines F1J `J01..J16` sont nouvelles, les initialisations individuelles sont indépendantes mais **les quatre familles écologiques restent celles déjà étudiées**, et les génomes `midpoint()` sont identiques. Les origines ne forment pas 16 lignées génétiques distinctes et les actions T5 ne sont pas interventionnellement assignées.

## Cause F1I : l'arrêt anticipé est un coût réel dépendant de la mémoire

Le `Mind._compete` P1.3 a pour règle de stopper la boucle **au premier franchissement du seuil par un accumulateur**. Lire des moyennes personnelles plus récentes change les scores et donc le seuil temporel atteint ; F1I avait **R07, R08, R10, R11** où `full` payait **4 cycles (3 fixes + 1 de compétition)** contre **5 cycles (3 + 2)** pour `mask_owned_prior_means`. Les `simulated_steps` et `memory_items` étaient pourtant appariés. Ces différences ont **réellement coûté de l'énergie/vigilance** et rendent F1I **non identifiable à coût strictement égal**, selon son plan.

F1J n'a ni rajouté une dette ou un cycle de compensation après `Mind.decide`, ni modifié les coûts physiques : `F1JFixedRoundMind(Mind)` **ne change QUE `_compete`**. Il fait intégrer **chaque option notée** pendant tous les tours réellement autorisés par le `CognitiveBudget` **déjà débité avant calcul**, même si le seuil est franchi tôt. Chaque tour applique `acc[o] = max(0, (1-LEAK)*acc[o] + GAIN*ev[o])`, `ev` étant normalisé à partir de vrais scores de plans. Le meilleur dépassement de seuil, sinon la meilleure activation puis, en égalité, le meilleur score, détermine **à la fin** le gagnant. Les égalités restent du ressort de `Mind._tie` ; l'admission motrice et les interdictions corporelles restent celles de `Mind._admit`.

**Chaque tour supplémentaire est une véritable opération de délibération**, et **modifie l'état des accumulations ; ce n'est donc pas un débit à vide**. Cette variante est néanmoins **une autre politique et peut consommer plus d'énergie qu'un `Mind` de référence qui se serait arrêté plus tôt**. La comparaison F1J n'est donc **PAS** une équivalence du coût avec P1.3, mais une comparaison authentique **entre lectures mémorielles dans la politique fixe F1J**. Aucune admission automatique dans `run_life`.

## Histoires personnelles, ressources et 16 contrasts stricts

Chaque `J01..J16` naît avec un `EffectsModel` **vide**, un TD à zéro et aucun tampon mémoriel. Quatre épisodes natifs successifs, T1..T4, sont **physiquement exécutés et payés** par lui-même, y compris les apprentissages, sans souvenir d'un autre individu. Les moyennes de référence T1 sont des effets **personnellement vécus** ; au tick 5, trois copies : `full`, `sham`, `mask_owned_t1_means` (ancienne moyenne personnelle T1 substituée **uniquement pendant la lecture**, mémoire réellement apprise T4 restaurée **avant** le vrai `World.step`). Ni statistique, incertitude, TD, tampon, génome, perception ni RNG ne sont rendus moins coûteux. Puis jusqu'à **T30 inclus** les décisions et apprentissages sont natifs, librement choisis et **réellement facturés**, sans nouvel effet expérimental.

La famille écologique conserve les vraies `token_effects` de F1I : fruit **+18 nourriture/+2 intégrité**, grain **+26/+0,5**, tubercule **+12/+3**, aliment amer **+28/−1,5**, et vraies sources d'eau de gain **25, 30, 18 ou 22** à stocks finis. **41 `manger` et 45 `boire` réellement exécutés sur les 48 branches**, avec stock, inventaire et physique des cinq réserves recalculés par le vérificateur froid.

**Résultat primaire** : **16/16** histories financées, **16/16** comparaisons `full`/`mask_owned_t1_means` à **identique `CognitiveWork(cycles,simulated_steps,memory_items,replays)`**, **16/16** prix natifs identiques et effectivement débités en **énergie et vigilance**, et **16/16** `sham` neutres pendant toute la continuation T5..T30. **Aucune exclusion** de J01 à J16.

**Exemple concret J05, monde `spring_grain`** : `full` décide **`se_deplacer W`**, `mask_owned_t1_means` décide **`boire`** ; pourtant **les deux** ont `CognitiveWork(cycles=5,simulated_steps=92,memory_items=72,replays=0)` et `World.step` facture **0,2984 unité d'énergie + 0,434 unité de vigilance**, tous débits acquittés et zéro impayé. Personne ne leur a prescrit l'action.

## Ce qui est causalement lisible et ce qui ne l'est pas

La mémoire récente change la **commande native T5 dans 10/16** comparaisons parfaitement appariées : **J01, J03, J05, J06, J07, J09, J11, J13, J14, J16**. Ces dix divergences ne reposent donc pas sur une différence de budget effectivement consommé au moment du contraste. Il s'agit d'un **effet local du contenu personnellement appris dans la politique F1J**, non d'une estimation générale de l'utilité de P1.3 ou d'une preuve de G2.

**Survie descriptive à T30 : les 48 branches (16×3) survivent**, sans meilleur temps de survie dans aucune des 16 comparaisons. Les cinq réserves terminales révèlent :

| Comparaison `full` vs mémoire T1 masquée | Origines / 16 |
|---|---:|
| `FULL_FIVE_CHANNEL_DOMINANCE` (toutes les réserves non inférieures, au moins une supérieure) | **2** : J06, J16 |
| `MASKED_FIVE_CHANNEL_DOMINANCE` (contrôle favorisé) | **1** : J13 |
| `MIXED_BODILY_TRADEOFF` (réserves opposées) | **7** |
| `FIVE_CHANNELS_EQUAL` | **6** |

La **dominance secondaire est hétérogène** et une origine favorise le contrôle. **Aucun avantage de survie, de transmission génétique ou de généralisation adaptative n'a été démontré.** Les coûts futurs, différents si les trajectoires divergent, ne sont jamais égalisés et font partie des conséquences naturelles de la politique.

## Intégrité du coût : audit indépendant sur 1 323 tours substantiels

Chaque exécution source et suite comporte **64 épisodes personnels initiaux + 1 248 pas de continuation = 1 312 transitions `World.step`**. L'auditeur froid Python3.12, sans moteur, a refait leurs factures de `World.step` ET `World.pay_cognition`, les stocks, la prise d'eau, la consommation réelle des aliments et les cinq réserves. Il a **en plus vérifié 1 323 tours de compétition réellement facturés** : à partir des scores, il recalcule `mean/sd/tanh`, preuves normalisées, accumulateurs avant chaque tour, les seuils génétiques, l'activation après chaque tour, le résidu final, le nombre de tours autorisés et le choix admis. Une tentative de falsifier le tour ou de créer une facture fictive est rejetée même si l'enveloppe est rescélée.

**Les deux originaux F1J sont bit-identiques** : fichiers `F1J_NEW_REAL_FIXED_ROUND_ORIGINAL.json` et `F1J_NEW_REAL_FIXED_ROUND_REPRODUCED.json`, **228 550 739 octets chacun**, SHA256 **`439db2f8afa5728831e35c544a5bb17a552c6a40b58e91faa8b91b65d6e98022`**. GitHub artifact original #**14709418620**, ZIP SHA256 `504cfb06e0a65f752ff261d77f0c4b131242b8443ce07d13cc8b94378cec6f91`. Le rapport froid `F1J_COLD_NATIVE_REAL_COMPETITION_AUDIT.json` est **16 255 octets**, SHA256 **`e965ddf85d86bcb15ac1c5cb2b9853ff394de67c245f21add45f34811d83e0db`**, artifact #**14709881175**, ZIP SHA256 `f0d3c326bdd05c824af7287e6ebe59602c763edeb3527428d805a4b2431c6d2a`.

**Preuves conservées hors expiration GitHub Actions** : `F1J_16_fresh_paid_fixed_round_parity_evidence_20261121.tar.gz`, **27 880 798 octets**, SHA256 **`888b5d484be36c07e26dd1ef2c8b358b3637e2f5957be40ce937ef601d0efe8e`**, incluant les deux originaux, l'audit froid, les deux préenregistrements et **16 fichiers gzip, un par racine J01..J16**. Les gzip sont des **dérivations déterministes et archivées du véritable original**, pas 16 nouvelles vies indépendantes `run_life`. [Manifeste de provenance Git](STAGE8F1J_NATIVE_PARITY_PROVENANCE_MANIFEST_2026-11-21.json) : tous les ancrages, l'audit, le nombre de tours, la condition et les limites ; manifeste portable externe complet SHA256 **`4f00393a97e7db65808875e0fc0f719e47e94d705f11a86f4403186fea542c90`** avec les 16 gzip SHA individuels. L'archive portable et le manifeste complet sont joints à la conversation, Git n'en stocke que les empreintes et le protocole.

## Décision scientifique et suite logique

**`FIXED_ROUND_16_OF_16_REAL_COST_PARITY_DEMONSTRATED_LOCAL`**, résultat local reproductible, sous la politique **nouvelle et explicite** `F1JFixedRoundMind`. Ce n'est **pas** une correction rétrospective de `INCONCLUSIVE_COST_GATE` dans F1I, pas une promotion du moteur P1.3, pas un critère de survie positive et pas une preuve de sélection intergénérationnelle.

**Prochaine question distincte, à préenregistrer séparément** : tester le compromis de dépense supplémentaire des tours fixes et leur valeur corporelle sur **d'autres environnements et graines réellement tenus hors conception**, avec budget authentique avant et après divergence et contrôle de politique alternative financée sans action imposée. Il faudra aussi vérifier si les **simulations** et les objets mémorisés peuvent devenir contenus-dépendants, car F1J garantit le nombre de tours de compétition seulement ; le **16/16 global** a été **constaté et audité**, et ne peut être généralisé comme propriété inconditionnelle de toutes les écologies. Aucun `run_life`, descendant G2, nouvelle cohorte scientifique ou mutation des résultats F1F/F1G/F1H/F1I ni de Stage8-E2 `CLOSED_NO_RETRY`.
