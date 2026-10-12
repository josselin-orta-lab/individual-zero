# EXP Stage 12 | Préenregistrement exploratoire des comportements | 2026-10-12

**État au dépôt de ce document : OPEN / NO RESULTS.** La présente inscription est créée **avant** l'exécution de la campagne. Ce protocole n'est ni un résultat tenu secret ni un essai scientifique confirmatoire. Le moteur de cognition est figé au commit `1a832bda59f81ac565d3a62aa92a09ad4b064039` (PR #128 intégrée) ; le programme d'essai et son manifeste seront versionnés dans une révision ultérieure, eux aussi antérieurs à toute donnée expérimentale. Ne pas modifier les hypothèses à la lecture des résultats.

## Sources et frontières

- Spécification normative : `docs/architecture/reference/en/mvp-specification-v1.3.1.md`, avec héritage explicite de la v1.2.1, dont §16.1 et Stage 12.
- Fondements : `docs/architecture/reference/fr/architecture-v2.md`, §§24, 25, 27, 39, 40, 41, 43 et limites de la Partie XV.
- Méthode : `docs/research/experiments-vs-tests.md`, `docs/research/experiment-lifecycle.md` et `docs/research/reproducibility.md`.
- Les événements physiques proviennent exclusivement du WorldBody via la frontière Action Control ; jamais d'action scriptée de l'individu, de vérité Oracle ou de récompense post-hoc.
- La campagne ne valide pas la récupération M-11/Stage12, ne ressuscite pas un mort et ne permet pas de correction opérateur de la cognition.
- Issue #110 : attribution subjective vécue non calibrée. Aucun P-47 `conforming` n'est traité comme preuve causale.

## Question et unités

Tester si des différences physiques pré-définies et un profil de pression de sommeil modifient les actions, la progression mesurable des buts et les alertes Stage12 de l'I0 **réellement exécuté**, sans intervention pendant la vie.

**Unité d'analyse = une vie mortelle indépendante**, pas un événement du journal, un pas de temps ni une version Python. Chaque vie est construite dans un processus Python neuf et dispose de son propre WAL et de son propre arrêt opérateur. Aucun snapshot d'une vie précédente, aucune reprise après décès. Toute mort, tout blocage ou arrêt prématuré restent dans le dénominateur initial (« intention to observe »).

## Plan prospectif, sans choix après résultat

Plan factoriel fixe : 3 conditions de monde × 2 états corporels initiaux × 2 profils sommeil = **12 vies indépendantes de 50 pas maximum**, quota *planifié* 600 actions physiques. Tous les pas manquants suite à mort, blocage ou défaillance restent manquants ; **ne jamais les compenser par de nouvelles naissances**.

- `reference` : WorldLayout de référence, source d'eau initiale à (4,2) depuis naissance (2,2).
- `water_available` : même monde avec une source additionnelle d'eau **sur la position initiale** et deux baies `berry_a` ; les ressources sont visibles au début de vie, pas injectées après l'action.
- `path_obstructed` : même monde avec un obstacle additionnel à (3,2) entre naissance et eau ; route alternative physiquement possible. Aucune lésion létale ajoutée.
- Variante initiale `0` : eau corporelle 20 ; variante `1` : eau corporelle 35. Tous les autres paramètres physiques de référence restent identiques. Les variantes sont des **états corporels distincts**, pas des graines stochastiques inventées.
- Profil `sleep_reference` : pression de sommeil et récupération initialement configurées, sans intervention cachée.
- Profil `sleep_pressure_ablation` : fatigue_gain = night_weight = consolidation_weight = 0 avant naissance ; les autres mécanismes restent intacts. Il s'agit d'une **ablation d'ingénierie**, non d'une comparaison à une population naturelle.
- Chaque paire sommeil utilise exactement le même couple physique monde/variante. Ordre des 12 vies lexicographique prédéfini, pas d'arrêt adaptatif.

Les couches P-43/UC et la physique autre que le montage environnemental sont préservées. Toutes les options sont celles effectivement émises puis admises par I0.

## Attentes et réfutations décidées avant les données

**H12-EAU** : les vies `water_available` exécutent plus d'actions `boire` **par pas physique fermé** que leur paire `reference` de même variante et profil. Différence nulle ou négative dans la majorité des quatre paires : direction attendue **non observée**. Valeurs manquantes et arrêt précoce : **INCONCLUSIVE**, pas exclusion. Aucune action `boire` dans les deux groupes : comportement non démontré, même si la CI est verte.

**H12-STAGNATION** : les vies `path_obstructed` montrent davantage de diagnostics de stagnation positifs **par diagnostic évalué** que la référence appariée. Il s'agit d'une attente exploratoire faible, susceptible d'être réfutée par la stratégie alternative de contournement. Une alerte positive ne prouve pas qu'I0 avait une stratégie erronée : calcul d'erreur et vérité physique sont deux objets différents.

**H12-SOMMEIL** : la proportion d'actions `dormir` est supérieure sous `sleep_reference` à l'ablation pour la majorité des six paires physiques. Si aucune vie n'atteint une pression suffisante en 50 pas, résultat **INCONCLUSIVE**, pas PASS négatif. Les coûts UC et l'énergie sont des covariables obligatoires.

**H12-TRACABILITE** : les catégories `goal_directed`, `legitimate_autonomous_intrinsic` et `without_traceable_justification` sont toutes calculées sur les commandes réellement appliquées, avec provenance préalable. L'absence de motif traçable est un résultat **unknown**, pas une preuve d'irrationalité. L'objectif de cette mesure est la couverture, pas un taux de « rationalité » arbitraire.

**H12-META** : les détecteurs de stagnation, boucle et entropie produisent des valeurs `true`, `false` ou `None` selon l'évidence disponible. Les fréquences sont décrites par vie, sans prétendre que la conformité de l'auditeur représente la vérité cognitive indépendante. Une seule classe observée sur toute la campagne ne valide pas la discrimination. La mesure *temporelle* des contextes et la mesure *par module* de S_t sont rapportées séparément.

**H12-ATTRIBUTION** : absence attendue de paires attribution/résultat admissibles tant que #110 n'est pas corrigée. Si l'auditeur affirme une calibration non nulle sans nouveau contrat indépendant, la campagne est **FAIL technique**. « Aucune preuve » n'est pas une absence scientifique de biais.

## Mesures préétablies

Par vie : hachages source/physique/layout/journal ; durée, dernier pas fermé, commandes appliquées par primitive, les trois catégories de motifs, diagnostics tri-state par détecteur, S_t par module (si disponible), préinscriptions et suivi des gains de but, nombre d'UC acceptées/refusées rapportées par les auditeurs, mode de terminaison et erreurs ; préserver le WAL et l'export causal complet.

Comparaison : différences de taux **appariées** à même état initial et profil sommeil, puis médianes descriptives et min/max des effets entre paires. L'absence de variation entre vies n'autorise pas une inférence statistique basée sur 600 pas corrélés. Aucune p-valeur ou intervalle « 95 % » calculé sur les pas comme observations indépendantes. Si le nombre de paires évaluables est inférieur à deux, verdict **INCONCLUSIVE**.

## Critères de rejet et qualité des données

- Refuser en tant que preuve technique un export dont la chaîne, les événements physiques, la chronologie ou les audits croisés ne passent pas.
- L'exécution peut être marquée `software_gate_fail` tout en conservant **tous** les résultats négatifs, incomplets, morts et interruptions ; aucun remplacement silencieux.
- La génération de mondes est **préenregistrée et faite avant naissance** ; les versions et SHA des configurations restent dans les manifests.
- Tous les résultats sont exploratoires, y compris « direction attendue observée ». Aucun effet n'est déclaré causal au sens fort à partir de variations corrélatives non aveugles et de deux variantes.
- On ne modifie ni l'individu ni les seuils après une observation pour faire passer l'hypothèse ; un changement appelle une nouvelle EXP et des conditions tenues à l'écart.
- Les rapports contiennent les cas négatifs, lacunes de couverture, raisons d'abstention, taille réelle de l'échantillon, mesures par vie, et les faits d'échec.

## Décision attendue

Après exécution, délibérer **séparément** sur :
(1) conformité logicielle et provenance, (2) observations de comportements, (3) adéquation des attentes théoriques, (4) opportunité d'une expérience confirmatoire indépendante avec d'autres mondes, graines réellement distinctes et puissance justifiée.

Aucune modification normative du MVP ni validation opérateur du Stage 12 ne peut être déduite de cette seule campagne. Recommandation MVP si nécessaire : préciser le contrat de paires vécues pour l'attribution, distinguer S_t par module et contexte temporel, conserver les 600 pas comme développement et réserver la validation scientifique finale aux campagnes confirmatoires indépendantes.
