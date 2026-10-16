# Individual Zero : bilan scientifique A2.30-W/X/Y, sondes alimentaires avant exposition

**15 octobre 2026.** Branche : `science/stage12-b-a230w-prospective-preexposure-20261015`, [PR #194](https://github.com/josselin-orta-lab/individual-zero/pull/194), DRAFT empilée sur #193 (puis #189, #188, #187, #186, #185, #184). Les expériences connexes #190/#191/#192 restent des études sœurs à intégrer par revue coordonnée. L'issue principale [#110](https://github.com/josselin-orta-lab/individual-zero/issues/110) reste ouverte ; `main` et la spécification MVP v1.3.1 sont inchangées.

## Question

Peut-on éviter la paralysie alimentaire de Stage6 en recueillant sans exposition toxique une information **effectivement perçue par I0** et discriminante sur les conséquences physiques cachées d'une même baie ?

## Trois preuves complémentaires et indépendances exactes

| Phase | Origine des faits | Fonction du test | Verdict |
|---|---|---|---|
| [W : run #38753518412](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38753518412) | **92 nouveaux mondes détachés**, 80 avec **240 pas physiques** +12 témoins sans acte | 4 sondes, 5 effets de `berry_a`, coûts physiques, équivalences first-person | **PASS** |
| [X : run #38754552318](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38754552318) | Mêmes archives immuables W 3.11/3.12, SHA fixés | Contrôle indépendant des reçus, histoires temporelles et 65 536 choix binaires | **PASS**, **0 nouveau monde** |
| [Y : run #38755394234](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38755394234) | **92 nouvelles instances techniques**, mêmes cellules de physique que W | Rejoue réellement **240 `WorldBody.apply`** avec constructeur et capture indépendants du runner W | **PASS**, **0 nouveau scénario scientifique** |

Toutes les CI passent sous Python 3.11 et 3.12, résultats identiques dans chaque phase. **Ne pas confondre relecture technique, répétition des interpréteurs et réplication scientifique indépendante.**

## Résultat scientifique nouveau et limites

Les sondes non-ingestives `immediate`, `wait_twice`, `collect_first`, `west_return` ne révèlent **aucune différence des histoires perceptives complètes** des cinq variantes cachées d'une même baie avant ingestion : **0/160 paires distinguées**, **16 classes d'équivalence** de cinq mondes. Chacune contient **3 repas avec survie, 1 décès terminal et 1 résultat alimentaire insuffisant**, résultats vérifiés par physique *après* gel de la perception pré-décision. Les témoin positifs sont discriminants : **4/4 changements de ressource visible** et **4/4 obstacles locaux** ; le dispositif est donc capable de détecter une différence réellement représentée.

Les trois sondes actives présentent des coûts corporels mesurés avant ingestion : attendre×2 (−1 énergie, −1 nourriture, −0,4 eau), collecte (−0,75 énergie, −0,5 nourriture, −0,2 eau), ouest puis retour (−2 énergie, −1 nourriture, −0,4 eau). Dans cette matrice, aucun de ces coûts ne révèle de toxicité et le nombre de repas/survie/décès reste 12/4/4 par sonde, pour chaque ensemble de 20 mondes. Une capture postmortem est un fait du banc, jamais une observation subjective de l'individu mort. **Aucune UC, motivation, attribution causale subjective ou action autonome d'I0 n'a été mesurée.**

En bornant chaque classe à la décision `engager le préfixe alimentaire fixe / s'abstenir`, **65 536 politiques déterministes** ont été examinées. Une seule évite toute mortalité dans ces 80 mondes, celle qui s'abstient partout ; **aucune** n'obtient un repas avec **garantie zéro décès dans l'ensemble des cinq variantes**. Ce résultat est une **frontière de connaissabilité et de décision dans ce domaine précis**, pas une impossibilité universelle de se nourrir ni la preuve qu'une stratégie d'exploration adaptative alternative ne pourrait fonctionner.

La limite scientifique est que **la physique actuelle ne publie pas une information de toxicité cachée avant ingestion** dans les observations Stage3 des sondes W. Un meilleur modèle de prédiction, un horizon de planification accru ou des branches supplémentaires ne peuvent *fabriquer* cette observation manquante ; et aucune conclusion de sécurité universelle ne découle de l'absence de preuve de danger.

## Architecture à préserver et priorité suivante

Ne pas modifier silencieusement `Equipment`, `Stage6`, l'Oracle ou la perception pour introduire une étiquette de danger physique caché. Une évolution normative éventuelle pourrait porter sur la **classification des risques et la possibilité de s'abstenir** sans confondre « aucune conséquence dangereuse vécue » et « sûr », mais le protocole actuel ne justifie pas une intégration.

**Prochaine priorité A2.30-Z recommandée :** tester prospectivement **des alternatives réellement accessibles qui évitent l'ingestion risquée** (ressource alimentaire déjà connue par son historique propre, action de collecte non létale, et trajectoires vers un autre aliment) en gardant le coût UC et la mortalité dans le périmètre. Il faut distinguer un résultat du laboratoire d'un plan exécutable Stage6 et des connaissances effectivement acquises par une vie I0. Si une nouvelle capacité perceptive explicite devient nécessaire pour atteindre l'objectif, proposer une option scientifique à l'opérateur ; ne pas modifier la spécification normative sans accord.

**Décision : A2.30 PARTIELLE ; Stage12 PARTIAL ; issue #110 OPEN ; PR #194 DRAFT.** Les études W/X/Y sont techniquement achevées et documentées, mais la planification alimentaire sûre, l'apprentissage vivant et l'attribution causale subjective ne sont pas démontrés. Aucun déploiement de prédicteur, aucune fusion ni révision normative.
