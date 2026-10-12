# Stage 12 | Rapport des observations exploratoires du 12 octobre 2026

**EXP : RESULTS (exploratoire uniquement) ; conformité technique : PASS ciblé ; validation scientifique confirmatoire : NON RÉALISÉE ; Stage 12 : NON ACCEPTÉ ; M-11/Stage12 atomique : NON VALIDÉ.**

## Provenance et antériorité

- Protocole rédigé avant l'exécution dans `docs/research/stage12-exploratory-behavior-preregistration-2026-10-12.fr.md`, premier commit `aa2820f150be383523eb04ec2cf67b9de27c0ee3`. Ne pas modifier les hypothèses après constat.
- Code cognitif de référence initial, incluant PR #128 : `1a832bda59f81ac565d3a62aa92a09ad4b064039`.
- Commit **effectivement exécuté** : `6b8b97489bb10fc5fc5b54d0b2f49a8f15e7bace`, PR [#130](https://github.com/josselin-orta-lab/individual-zero/pull/130).
- [GitHub Actions](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38298279330) : six jobs SUCCESS sur deux versions, dont deux jobs d'essais exploratoires, deux tests Stage 12 et deux vies de 600 pas indépendantes du protocole exploratoire.
- [Archive Python 3.11](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38298279330/artifacts/11770395252) : SHA-256 du ZIP `b174a177a3c105994dc9e37cb07e488374685f98fb042d5b73aab588abfa8142`.
- [Archive Python 3.12](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38298279330/artifacts/11770395261) : SHA-256 du ZIP `d2b95b867f843cff86d470f19fd02e360d5e3049a82568c817ff055971c10ee0`.
- Les ZIP ont été inspectés par un lecteur **externe à l'exécution** le 12 octobre 2026 : 12 manifestes de vie et 12 exports par version, SHA-256 de chaque export conforme à son manifeste, base WAL égale à l'export suivi du séparateur final, 12/12 exports de même configuration strictement identiques octet pour octet entre Python 3.11 et 3.12.
- Important : les manifestes et la chaîne causale sont produits par la même infrastructure logicielle. Ils attestent une cohérence technique et une reproductibilité, **pas** une vérification indépendante de la vérité physique et encore moins de la causalité subjective.

## Plan réalisé et limites d'indépendance

Chaque version exécute **12 vies distinctes** de 50 commandes physiques : 3 conditions de monde (`reference`, `water_available`, `path_obstructed`) × 2 niveaux d'eau corporelle initiaux (20, 35) × 2 profils de sommeil (`sleep_reference`, `sleep_pressure_ablation`). Les 12 vies de chaque version réalisent 600 pas, sans remplacement, erreur d'audit, décès ou arrêt prématuré ; fin expérimentale opérateur prévue à 50 pas.

**N = 12 configurations par version pour les contrastes expérimentaux ; N ne devient pas 24 pour l'inférence grâce à Python 3.12.** Les 12 trajectoires de commandes d'une version ont seulement **deux profils distincts** (50 déplacements, ou 3 déplacements puis 47 sommeils). Les mondes sont physiquement distincts et les journaux ont 12 SHA différents, mais ce n'est pas une diversité de décisions. Aucun tirage aléatoire de graines distinctes n'est présent : `water=20` et `water=35` sont des traitements déterministes, pas des graines indépendantes.

## Résultats de la campagne par version (identiques sous 3.11/3.12)

| Mesure (12 vies × 50 pas) | Sommeil ablation : 6 vies | Sommeil de référence : 6 vies |
|---|---:|---:|
| Pas physiques appliqués | 300 | 300 |
| Commandes `se_deplacer` | 300 | 18 |
| Commandes `dormir` | 0 | 282 |
| Commandes `boire` | 0 | 0 |
| Actions dirigées vers un but, selon auditeur | 0 | 0 |
| Motivations autonomes intrinsèques attestées | 300 | 114 |
| Sans justification traçable | 0 | 186 |
| Diagnostics Stage 12 facturés / publiés | 300 | 204 |
| Stagnation (positifs/négatifs/inconnus) | 270 / 0 / 30 | 0 / 0 / 204 |
| Boucle (positifs/négatifs/inconnus) | 0 / 258 / 42 | 0 / 0 / 204 |
| Faible entropie temporelle (positifs/négatifs/inconnus) | 0 / 282 / 18 | 132 / 54 / 18 |
| Critères de progression de but préenregistrés | 0 | 0 |

Somme totale : **600 pas physiques**, 318 déplacements, 282 sommeils, 414 motivations intrinsèques attestées et 186 sans justification traçable par version. Les 186 cas inconnus correspondent à la configuration avec sommeil : ne pas les présenter comme 186 actions irrationnelles. Les 600 pas ne constituent pas 600 observations statistiques indépendantes.

## Hypothèses préenregistrées : verdicts prudents

### H12-EAU : NON SOUTENUE, défaut comportemental à investiguer

Dans les quatre comparaisons appariées `water_available` contre `reference` (eau initiale × sommeil), **différence d'actions boire = 0 dans 4/4**. Aucune des douze vies n'exécute `boire`, même lorsque la source est sur la position de naissance (2,2). La journalisation de `S_t` au premier pas signale pourtant l'alerte de besoin d'eau et un élément observé `water_source` ; elle ne prouve pas que la source sur la cellule occupée a été consommée cognitivement de façon appropriée. La procédure « augmenter l'accessibilité de l'eau » n'a pas entraîné le comportement prédit.

**À examiner sans contorsion rétrospective :** hiérarchie du Goal Manager (but d'eau actif), évaluations intrinsèques d'exploration, alignement but/option, préconditions de `boire`, options générées/rejetées et coûts UC. Absence d'action ne prouve pas un bogue physique spécifique.

### H12-STAGNATION : EFFET PRÉDIT NON OBSERVÉ ; TEST PHYSIQUE NON DISCRIMINANT

Obstacle en (3,2), mais le premier déplacement de chaque vie est **vers (2,1)**, puis les trajectoires passent par (3,1) : l'obstacle n'est jamais abordé. Les taux de stagnation sont identiques dans tous les mondes à profil sommeil identique : 45 alertes positives par vie sans sommeil, 0 classées positives/négatives et 34 inconnues sous sommeil. Il serait scientifiquement incorrect de conclure que le détecteur est bon ou mauvais face aux obstacles : **manipulation non exercée**. Nouvelle étude nécessaire avec obstacle rencontré réellement, chemin alternatif possible, préinscription et contrôles négatifs.

### H12-SOMMEIL : EFFET D'ABLATION OBSERVÉ, ADÉQUATION NON DÉMONTRÉE

Dans les six paires appariées : **47/50 = 94 %** d'actions `dormir` sous `sleep_reference`, contre **0/50** sous l'ablation (différence +94 points de pourcentage ; 6/6 paires dans le sens préenregistré). Cette observation soutient un **effet du paramétrage du sommeil sur les commandes**, non une bonne régulation physiologique.

En sommeil de référence : les trois premiers pas sont des déplacements, suivis de 47 commandes dormir, **16 entrées en sommeil et 15 réveils pour durée maximale**, puis réentrée en sommeil avant toute nouvelle action physique de veille. Les 50 pas ne permettent pas d'affirmer une pathologie universelle ; ils montrent une **domination du sommeil dans ce banc déterministe**, à investiguer. Examiner séparation fatigue/pression de consolidation, réveil, période réfractaire éventuelle seulement si théoriquement justifiée, et impact des budgets UC sur l'option sommeil. Toute correction de seuil comportemental nécessitera une nouvelle EXP, pas une modification silencieuse du protocole.

### H12-TRACABILITÉ : COUVERTURE PARTIELLE, PAS DE BUT EXÉCUTÉ ATTESTÉ

414/600 actions sont associées à une motivation intrinsèque admise avant commande, en utilisant le décodeur canonique `$f64` corrigé par la PR #128. **0/600** ont la catégorie `goal_directed`. Le reste (**186/600**) n'a pas de motif admissible sous le contrat auditeur, principalement durant les commandes de sommeil avec capture réduite. Ce sont des **inconnus**, pas une preuve d'absence de motivation. Aucun critère de progression de but n'a été préenregistré. Un jugement positif de rationalité serait non justifié.

### H12-META : CONTRATS DE PUBLICATION VÉRIFIÉS, VALIDITÉ DISCRIMINANTE INCONCLUSIVE

La trajectoire éveillée produit 45 alertes de stagnation positives sur 50 pas (les cinq premiers inconnus), **aucune classe négative** ; la trajectoire sous sommeil rend les 34 échantillons diagnostiques classés inconnus pour la stagnation et les boucles. La faible entropie temporelle est négative durant la trajectoire éveillée et comporte des valeurs positives et négatives durant celle avec sommeil. Cela témoigne d'une mesure sensible au contexte du protocole, **pas d'une calibration scientifique contre une vérité comportementale indépendante**. L'occupation par module de S_t est distincte de l'entropie temporelle des contextes. Ne pas conclure que toutes les alarmes positives sont vraies.

### H12-ATTRIBUTION : INCONCLUSIVE / NON ÉVALUABLE

Pas de source indépendante de paires vécues résultat / attribution admissibles (issue #110). Aucun jugement scientifique sur la prévalence ou la correction des biais d'attribution d'I0 n'est possible. La conformité d'une prédiction P-47 ne constitue ni succès d'objectif ni preuve de causalité personnelle.

## Délibération, décisions et étapes proposées

1. **Résultat logiciel : PASS ciblé.** Runtimes mortels indépendants, WAL et exports chaînés, 12/12 vies auditées par version, reproductibilité exacte des 12 configurations et arrêt opérateur. La CI ne constitue pas une étude scientifique confirmatoire.
2. **Résultat scientifique exploratoire : MIXTE.** Effet de l'ablation de sommeil nettement observé ; hypothèse de consommation d'eau non soutenue ; obstacle non rencontré donc test non discriminant ; comportements exclusivement exploration ou sommeil, aucune progression de but documentée.
3. **Action technique P1 :** analyser la compétition entre besoin en eau visible, but actif, action `boire`, exploration intrinsèque, options envisagées/rejetées et éventuelle saturation de sommeil. Ne pas modifier les seuils avant de publier une hypothèse testable et une expérience de confirmation.
4. **Action expérimentale P1 :** dessiner un nouvel obstacle sur une trajectoire que le sujet peut réellement rencontrer, puis préenregistrer **un autre protocole** avec manipulation contrôlée ; ne pas modifier rétroactivement `path_obstructed` ici.
5. **Action de qualité P0 :** terminer les sources admissibles de résultat et jugement d'agence (#110), et l'atomicité M-11/Stage12, avant réception globale du stage.
6. **Pas de modification immédiate du MVP :** conserver 600 pas comme hypothèse de développement, clarifier la différence entre couverture des mécanismes et simple quota, et réserver les preuves confirmatoires multi-mondes/graines réellement variées à la validation finale.

**Aucune validation opérateur du Stage 12, scientific GO ou certification d'atomicité M-11/Stage12 n'est émise.**

## Reproduction de l'audit externe

Télécharger l'archive GitHub de la version désirée, vérifier son SHA-256 et inspecter chaque `life-result.json`. Pour chaque vie, comparer `journal_sha256` à l'empreinte SHA-256 du `canonical.jsonl`, puis vérifier que `life.wal` est égal à l'export canonique suivi du séparateur de ligne. Dérouler l'auditeur indépendant du dépôt avec `expected_head` et `expected_count` issus du manifeste, en conservant leur limite de garde commune. Regrouper les comptages **par vie** et par facteurs monde/eau/sommeil, puis calculer les six contrastes appariés du sommeil, les quatre contrastes appariés de l'eau et les quatre de l'obstacle. Les données et tous les résultats négatifs restent présents dans les archives.

Ce rapport a été rédigé **après** le dépouillement, sur un commit documentaire séparé des programmes et protocoles gelés. Il constitue une interprétation, pas un préenregistrement.
