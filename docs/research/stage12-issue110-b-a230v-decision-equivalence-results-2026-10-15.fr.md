# A2.30-V : certificat conditionnel d'indiscernabilité de décision alimentaire

**15 octobre 2026.** Préenregistrement V : commit `3f3733709418dbc0d6347ddb25f2848adf008452` **après connaissance des résultats des études S/T mais avant le code V**, sans prétendre à une nouvelle campagne prospective. Auditeur : `scripts/audit_stage12_issue110_b_a230v_decision_equivalence.py`. Contrôles négatifs : `tests/test_stage12_a230v_decision_equivalence.py`. [CI finale #38750322529](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38750322529) : **PASS Python 3.11 et 3.12**, 14 tests adversariaux, certificat recomputé dans chaque environnement, sorties **strictement identiques octet par octet**.

## Source et reproductibilité

Cet audit n'a créé **aucun nouveau monde, aucune action physique, aucune vie I0 et aucun pas autonome**. Il s'appuie exclusivement sur **six artefacts originaux immuables** de trois études distinctes, disponibles sur GitHub Actions :

1. [S-observable, PR #190, run #38740205272](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38740205272) : 36 mondes / 104 pas physiques d'origine, 36 paires sensorielles.
2. [T-food, PR #192, run #38741620906](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38741620906) : 40 mondes / 132 pas physiques d'origine, 20 paires avec/sans attente avant la prévision shadow.
3. [S-causal, PR #191, run #38740664255](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38740664255) : 64 mondes actifs / 196 pas physiques et 8 témoins passifs d'origine, 56 recherches de l'algorithme Stage6 en shadow.

Pour **chacune** de ces études, le reviewer compare byte-à-byte les JSON Python 3.11 et 3.12 et vérifie les **neuf SHA-256 de fichiers d'origine**, listés en entier dans le préenregistrement et le script. Les trois jeux ne sont pas des répétitions statistiques d'un même protocole et ne sont jamais agrégés en une seule cohorte scientifique.

**Empreinte du certificat final V, identique Python 3.11/3.12 :** `b32f5ac285843d3fba20bfa5f7c92f0d19e5e44d83b15147c115924c932273d6`. Les sources et le certificat ont chacun des hashes intrinsèques; une relecture de fichiers n'est pas une validation indépendante de la physique `WorldBody.apply` (déjà revérifiée par les audits de leurs PR respectives).

## Théorème expérimental borné : cinq mondes, une seule observation

En repartant **exclusivement du `decision_stage3_state` complet**, avant le préfixe alimentaire fixé, le reviewer trouve **8 classes d'équivalence perceptive**, chacune comportant exactement cinq mondes physiques latentement distincts mais **strictement identiques pour les informations accessibles** à cet instant :

| Variante physique cachée de `berry_a` | Issue du préfixe préengagé dans chaque classe |
|---|---|
| Bénigne | Gain alimentaire avec survie |
| Toxicité `−7` | Gain alimentaire avec survie |
| Toxicité `−30` | Gain alimentaire avec survie |
| Toxicité `−100` | **Décès terminal** |
| Gain alimentaire nul | Survie sans gain suffisant |

Les huit classes croisent deux bras (attente ou non), deux niveaux initiaux de nourriture et deux positions. Pour une classe, un décideur déterministe dont l'entrée est **seulement cet état perceptif** doit choisir **la même action** pour les cinq variantes, car la cause latente est cachée et la capture complète est identique.

La décision V est **explicitement limitée** à `commettre le préfixe collecter → manger` ou `s'abstenir de ce préfixe`. S'il s'engage dans une classe, le témoin physique montre **1 issue létale**, **3 gains avec survie** et **1 issue insuffisante** dans les cinq mondes correspondants. S'il s'abstient, ce préfixe ne procure aucun de ces trois repas ; l'expérience **ne simule pas** alors toutes les actions alternatives ou toutes les autres ressources d'I0.

Les **256 fonctions de décision déterministes** sur les huit classes sont énumérées sans apprentissage ni sondage opportuniste. Le compromis exact pour `k` classes engagées est : **k issues létales compatibles, 3k succès alimentaires, k succès insuffisants**, comptés sur les mondes originaux (et non comme fréquences naturelles). Quelques points :

| Nombre de classes où le préfixe est engagé | Succès physiques du préfixe | Décès compatibles avec la même observation | Nombre de politiques |
|---:|---:|---:|---:|
| 0 | 0 | 0 | 1 |
| 1 | 3 | 1 | 8 |
| 4 | 12 | 4 | 70 |
| 8 | 24 | 8 | 1 |

**Résultat : 1/256 politique n'expose aucun monde témoin à un décès, celle qui s'abstient partout. 0/256 politique obtient au moins un succès alimentaire tout en garantissant zéro décès dans la matrice physique étudiée.** C'est un certificat **conditionnel au jeu d'actions et aux cinq causes testées**, pas une impossibilité universelle d'acquérir de la nourriture.

Une politique randomisée ne supprime pas non plus la possibilité physique d'une issue létale : tout engagement de probabilité strictement positive dans une classe peut exposer le monde latent mortel. Il ne s'agit pas d'une estimation de la probabilité du monde caché.

## Valeur de l'attente et compléments des PR parallèles

Les 20 paires OFF/ON montrent que l'attente **ne sépare pas les cinq variantes** et n'améliore ni gain alimentaire ni survie sur ces mondes. Son coût physique préengagé est **−0,5 énergie, −0,5 nourriture, −0,2 eau par paire** ; total technique sur les 20 paires : **−10 énergie, −10 nourriture, −4 eau**. Ces totaux cumulent des corps de test indépendants et ne doivent pas être interprétés comme la consommation d'un seul individu. **Aucun coût UC de cognition n'a été mesuré.**

S-observable (#190) confirme **zéro discrimination avant exposition alimentaire ou spatiale**, avec 20 paires distinguables **pendant** leur survie commune et 16 sans distinction commune avant une fin terminale. S-causal (#191) confirme les **56/56 recherches Stage6 `incomplete_model` à racine non prédictible**, ainsi que huit contrastes de causalité alimentaire indiscernables dans la première observation. Les 56 recherches étaient exécutées passivement avec une mémoire exacte idéale limitée aux expériences passées de la même instance de monde : **cela n'est pas la preuve du mécanisme d'apprentissage réel d'I0**. Ces études sont complémentaires, non des réplications de la matrice T.

## Robustesse informatique et portée

14 tests adversariaux et les deux jobs CI ont vérifié le rejet de : variable latente injectée dans la clé perceptive, observation postérieure introduite prématurément, famille alimentaire manquante, identité dupliquée, décès converti en survie, postmortem fictivement vécu, certificat `safe` fabriqué, fausse facture d'attente, changement d'agrégats, information perceptive déplacée avant exposition, fuite Oracle vers le shadow Stage6 et racine prédictible artificiellement inventée. Le premier run de l'auditeur V a échoué sur **une lecture erronée des champs de reçus physiques et de la ventilation par familles des décès**, puis sur une assertion de test qui exigeait un message d'erreur trop précis. Ces problèmes ont été corrigés **sans modification des archives, du protocole, des critères ni du code cognitif**, avant la CI finale verte. Les historiques rouges restent consultables : #38750048140 et #38750299651.

**V PASS technique comme audit de cohérence et certificat de décision sur données existantes.** Son apport scientifique est la formalisation d'un **compromis de décision irréductible dans ce domaine perceptif**, et non l'invention de nouvelles observations ou la résolution du Stage6. Un signal de risque **observable avant engagement**, effectivement acquis sans danger et vérifié sur des mondes indépendants, serait nécessaire pour lever cette indiscernabilité ; l'existence d'un tel signal n'est pas démontrée. L'absence d'un signal actuel n'autorise pas l'usage de connaissances de l'Oracle comme perceptions subjectives.

**Décision : A2.30 PARTIELLE ; Stage12 PARTIAL ; issue #110 OPEN ; PR #193 DRAFT. Déploiement cognitif : NO-GO.** Aucune modification de `src/i0`, d'Equipment, de Stage6, de Stage9/DC-05, de Stage12, du WAL ou du MVP v1.3.1, et aucune fusion.
