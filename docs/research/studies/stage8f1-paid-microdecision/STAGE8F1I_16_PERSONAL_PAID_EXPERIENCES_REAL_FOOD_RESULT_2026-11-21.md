# Stage8-F1I · 16 histoires personnelles nouvelles, ingestion réelle, causalité adaptative non identifiable

**21 novembre 2026. Verdict primaire strict : `INCONCLUSIVE_COST_GATE`.** L'étude montre que seize `Mind` indépendamment initialisés peuvent acquérir des expériences première personne **réellement vécues, financées et conservées** ; des ressources alimentaires et hydriques sont **effectivement consommées**, avec leurs conséquences mesurables et leurs stocks débités. En revanche, **4/16 comparaisons cognitives préenregistrées ne sont pas appariées**. Les résultats moteurs et corporels sont conservés, mais aucun avantage adaptatif causal sur l'ensemble des 16 origines ne peut être revendiqué. Les résultats nuls et défavorables de F1F à F1H ne sont pas réinterprétés.

## Préenregistrement : AVANT toute naissance logicielle F1I

La [grille de seize origines](STAGE8F1I_FROZEN_EXPERIMENT_GRID_2026-11-21.json) a été scellée au commit Git `9bb5af06cc6e78f4ec86895ee57d6ccfff7f636b`, puis la [règle d'intervention, d'audit et de succès adaptatif](STAGE8F1I_INDEPENDENT_PAID_EXPERIENCES_REAL_RESOURCES_PREEXPOSURE_2026-11-21.md) au commit `ff6b8b0c627797e9443ea4393e5e682e9cc07681`, **avant toutes les exécutions F1I**. Base main `15c6869484c5b47b14d44c9e4e77b431a80b5caa`. La [PR de production et contre-audit #1497](https://github.com/josselin-orta-lab/individual-zero/pull/1497) ne modifie ni les politiques i3 de référence, ni les critères historiques ni les Worlds F1C/F1F/F1G/F1H.

Contrairement aux forks précédents issus **d'une seule expérience synthétique F1C**, chacun des seize `Mind(midpoint(),seed)` est créé avec un **EffectsModel vide, des TD à zéro, un tampon vide et une graine personnelle R01..R16 distincte**, dans un `WorldSpec` natal neuf. Les 4×4 expériences ne sont pourtant **pas un échantillon aléatoire de 16 lignées génétiques** : le génome `midpoint()` est commun et quatre familles de mondes sont répétées avec états et graines fixes.

## Mondes et ressources réellement physiologiques

Dès le tick 0, chaque monde 3×3 présente une eau à stock fini, plus un aliment à quantité finie. Aucune ressource, effet caché ou action motrice n'est accordé directement au cerveau. La conséquence **positive ou adverse** réside dans le moteur natif `WorldSpec.token_effects` et n'entre dans le corps qu'après `collecter` puis `manger` volontaires.

| Écologie (4 origines chacune) | Eau native à `boire` | Aliment à `manger` |
|---|---|---|
| `oasis_fruit` | ici, +25 eau | fruit : +18 nourriture, +2 intégrité |
| `spring_grain` | Nord, +30 eau | grain : +26 nourriture, +0,5 intégrité |
| `patch_tuber` | Est, +18 eau | tubercule : +12 nourriture, +3 intégrité |
| `bitter_tradeoff` | ici, +22 eau | amer : +28 nourriture, **−1,5 intégrité** |

**Événements natifs réellement audités sur les 48 branches expérimentales : 40 `manger` et 48 `boire`**, avec décompte physique des stocks, de l'inventaire et des cinq réserves. Ce sont des événements, **pas 40 ou 48 vies indépendantes**. L'auditeur indépendant vérifie `World.step` et n'attribue aucun gain à une ressource simplement visible.

**Exemple original R01, `oasis_fruit`, `full`, tick 23** : un fruit réellement porté est mangé ; la nourriture augmente **58,56 → 76,36** (gain alimentaire +18, moins 0,2 de métabolisme), l'intégrité **92,4 → 94,4**, l'énergie **1,5246 → 0,8300** après décision cognitive **0,1946 E** et coût moteur `manger` **0,5 E** ; vigilance facturée **0,292 V**. L'inventaire du fruit passe de 1 à 0. Exemple `boire` R01 tick 5 : eau **33,4 → 58,0**, soit +25 moins 0,4 de métabolisme ; stock d'eau local **1 → 0**. **Aucun événement de consommation n'est simulé gratuitement**.

## Acquisition native de la mémoire et interventions sans action imposée

Dans **16/16** histoires, les ticks T1..T4 ont eu lieu sur des `World` neufs, avec **64 vraies transitions d'acquisition**, `Mind.decide`, `World.step`, et `Mind.learn_from_outcome` **uniquement après `prepare_learning` et `World.pay_cognition`**. La première moyenne utilisée comme référence a été **personnellement apprise, financée et scellée au tick T1 de ce même individu**, non copiée de l'histoire F1C d'un autre individu. Le cerveau complet, la perception et les réserves post-paiement sont conservés.

À T5, chacun est cloné sous **trois** conditions : `full`, `sham` et `mask_owned_prior_means`, qui présente **temporairement** les anciennes moyennes T1 réellement vécues pour les seules clés présentes à la fois à T1 et T4. Les comptes, `n_eff`, états TD, buffer, RNG, génome, réserves et perception restent inchangés. **La vraie mémoire T4 est restaurée avant la physique**, puis les décisions T6..T30 et tous les apprentissages réels ont lieu sans nouveau masque ni ordre moteur du laboratoire.

Les **1 248** transitions prospectives (16 origines × 3 bras × 26 ticks) se sont déroulées jusqu'au tick **30**. **Aucune mort** dans les 48 branches, aucun rattrapage de réserves, aucun `run_life`, aucune nouvelle cohorte scientifique.

## Contraste moteur, vraie facture et cause d'invalidation

**Sources et shams valides : 16/16. Parité exacte du travail et des deux débits cognitifs : 12/16, donc FAIL du gate primaire préexposé.** Quatre échecs clairement identifiés, aucun exclu de la population :

| Origine | Monde | Travail naturel `full` | Travail naturel `mask_owned_prior_means` | Gate |
|---|---|---|---|---|
| R07 | `spring_grain` | 4 cycles | 5 cycles | Non apparié |
| R08 | `spring_grain` | 4 cycles | 5 cycles | Non apparié |
| R10 | `patch_tuber` | 4 cycles | 5 cycles | Non apparié |
| R11 | `patch_tuber` | 4 cycles | 5 cycles | Non apparié |

La politique native adapte le **nombre de cycles de délibération** selon le contenu lu. Le coût supplémentaire n'est pas un simple défaut de copie : c'est du calcul réellement différent. **Interdiction de gonfler le coût ou de « payer un cycle fictif » pour recoller les bras après exposition.** Selon le plan préalable, le verdict global reste `INCONCLUSIVE_COST_GATE`.

Dans les **douze** origines où la comparaison est effectivement appariée, **sept** ont choisi une commande `(action,param)` différente à T5 : **R01, R02, R04, R05, R06, R09, R15** ; cinq sont inchangées. Ceci est une description **dans les seules paires valides**, et **pas** un K/16 admissible pour la déclaration causale globale. En particulier, aucun résultat d'une des quatre origines non appariées n'a été réinterprété comme avantage.

## Valeur adaptative à T30 : aucun bénéfice de survie observé

**Toutes les 48 branches survivent à T30**, y compris les contrôles témoins et les quatre paires non appariées. La différence de survie est **nulle descriptivement** à l'horizon fixé, sans réclamer le droit d'ignorer l'échec de parité. Pour les **12** paires appariées :
- **7** présentent un `MIXED_BODILY_TRADEOFF` des cinq canaux : une réserve s'améliore, une autre se dégrade.
- **5** présentent des corps terminaux identiques.
- **0** présente une domination corporelle Pareto stricte du bras à mémoire authentique sur les cinq réserves.

La règle de succès adaptatif préfixée demandait **≥3 origines avec commande modifiée ET meilleure survie**, réparties dans **≥2 écologies**, sans cas défavorable et **16/16 parités valides**. Aucune de ces conditions ne peut être revendiquée ici. **Il est incorrect de transformer la simple consommation nutritive ou des divergences de commande en valeur adaptative démontrée.**

Ce résultat clarifie néanmoins deux mécanismes : (1) les mémoires viennent bien de plusieurs sujets logiciels indépendamment initialisés, et non du même épisode F1C ; (2) les aliments/eaux sont physiquement efficaces et réellement employés. **La parité du coût de délibération, auparavant facile à obtenir en F1F sur des forks similaires, devient une véritable difficulté lorsque les historiques personnels sont distincts.** C'est un verrou méthodologique, pas une conclusion biologique.

## Audit, erreurs visibles et conservation des originaux

[CI finale dédiée #44903988828](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44903988828) : **2/2 jobs PASS**, **16/16 tests adversariaux PASS**. Deux processus Python 3.11 produisent **deux JSON natifs bit-identiques**, chacun **200 347 017 octets**, SHA256 `e9daebdabb3b69671ecaa39c9fb48a0cc60d92d8518d42c7df1ad32ad5346f2a`. Artifact original GitHub #**14707516219**, ZIP SHA256 `101cfab3a1329c19f493cb066ad1ba0acf830e969e97f01e026acbee80127aa7`.

Le second job Python 3.12, **stdlib-only sans importer le moteur**, audite **1312/1312 transactions natives** : 16 origines indépendantes T0, 64 tickets de mémoire financée, 1248 ticks ultérieurs, coûts énergie et vigilance en décision ET apprentissage, stock/inventaire, vraie physiologie de `manger` et `boire`, absence de retour d'entre les morts et critères primaires préfixés. Verdict froid identique `INCONCLUSIVE_COST_GATE`. Artifact audit #**14707815370**, `F1I_COLD_NATIVE_RESOURCE_AUDIT.json` **10062 octets**, SHA256 `c86acb7220fa573949d59ccfc75002b8855f9d52b0bfa7f7f01e1392762a00b3`, ZIP SHA256 `e2a4cdf736973bc7619f65aefdd3b2f55494284f36d179a80389f3ff36ef9051`.

Les premières CI `#44903332167`, `#44903384801`, `#44903394167` ont échoué sur **la forme typée du Mind de référence et des assertions de l'auditeur**, sans réécriture du préenregistrement ni du moteur. La CI `#44903480386` a produit **les mêmes originaux positivement reproductibles** mais son job froid ne trouvait pas les fichiers en raison du **répertoire préfixé `_temp/` dans l'artefact ZIP GitHub**. La correction ne change que la **racine d'emballage CI**. Ces échecs restent consignés, et non réinterprétés comme vies ratées ou adaptatives.

**Archive portable hors expiration GitHub** : `F1I_16_independent_personal_memories_real_food_evidence_20261121.tar.gz` (**17 395 138 octets**, SHA256 `a04bb054b8568d930c5e6b0e4284f83c963eda6f7ee353367305719498dca01f`). Contient le JSON original natif, sa reproduction octet-identique, le contre-audit, les deux préenregistrements et **16 journaux `R01..R16` en gzip**. Ces gzip sont des **extraits déterministes authentifiés du JSON original**, pas de nouvelles vies séparées `run_life` : chaque SHA et sa racine sont consigné dans le [manifeste portable](STAGE8F1I_NATIVE_PROVENANCE_MANIFEST_2026-11-21.json). L'archive et le manifeste complets sont livrés dans la conversation, seuls les hash et rapports résident dans Git. Conservation de tout verdict nul.

## Décision scientifique de fin F1I

**`INCONCLUSIVE_COST_GATE`**. Sont démontrés dans les limites du laboratoire : mémoire personnellement acquise dans 16 sources indépendantes et réellement payées, décisions réellement autonomes, consommation nutritive et hydrique physiquement effective, perturbation du choix dans plusieurs paires, et audit froid des 1312 transitions. **N'est pas démontrée** : une amélioration de survie reproductible, ni une causalité proprement isolée du contenu de la mémoire **à coût égal sur les 16 origines**.

Pour une future expérience distincte, le problème réel est le **temps de délibération et son financement ex ante dans la politique native**, qui peuvent réagir à la mémoire; une nouvelle hypothèse/protocole devra être scellée avant de créer d'autres individus. **Ne jamais recoter F1I ou choisir uniquement les sept paires favorables**, ni assigner une action forcée. F1H reste négatif, F1F positif local 1/8, F1G TD/buffer négatifs 0/8, Stage8-E2 `CLOSED_NO_RETRY` inchangé.
