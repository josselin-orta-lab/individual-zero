# A2.30-S-shadow : effet alimentaire vécu, causes cachées et Stage6 observateur

**15 octobre 2026.** Protocole préenregistré **avant toute implémentation S-shadow** au commit `ea7b1374212e0fd6888b8e37a181c1bea40908e2`. [CI physique #38740664255](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38740664255) : **SUCCESS Python 3.11 et 3.12**, mêmes 3 fichiers JSON octet à octet, source `0046d8b2b30f44fe5e4fd0b4b165c88e724a8881`. Fichiers et workflows de cette PR sont volontairement distincts de ceux de [#190](https://github.com/josselin-orta-lab/individual-zero/pull/190), étude en parallèle des sondes perceptives ; sa science ne doit pas être comptée ici comme une réplication de notre cohorte.

## Monde réel de laboratoire et observations accessibles

**72 `WorldBody` indépendants**, dont **64 mondes ayant physiquement exécuté des commandes** et 8 contrôles de perception sans action. Les 64 mondes actifs appliquent réellement **196 transitions** : 120 alimentaires, 76 de déplacement. Ils comprennent **44 ingestions** et **24 terminaisons physiques irréversibles** (8 dans les variantes alimentaires, 16 dans les variantes spatiales), immédiatement arrêtées. Un `WorldBody` de test mort n'est pas restauré. Aucune instance cognitive I0, aucun pas autonome I0, aucune commande choisie par Stage6 ou Stage12. Le journal externe atteste aussi les `set_danger_zone` déclenchés par le laboratoire : ce ne sont **pas** des commandes I0.

La capture utilisable pour analyser *ce qui pourrait être perçu* provient uniquement de `SymbolicPerception.capture` et `state_from_capture`. Les classifications cachées des zones et l'effet nocif réel des baies ne sont présents que dans les configurations/réceptions externes. La capture technique de l'état final d'un monde tué est **un reçu opérateur**, pas une sensation utilisable pour une décision future de l'individu mort.

## Résultats scientifiques

| Contrôle | Effectif / résultat | Portée |
|---|---:|---|
| Baie `berry_a` dommage interne −7 vs baie bénigne + zone dangereuse exogène 7 | **8 paires de captures identiques** avant ET après première ingestion | L'observation de la baisse d'intégrité **ne permet pas d'identifier la cause** |
| Après ingestion, `attendre` | **4/4 contrastes différenciés** : intégrité 93 vs 86 | L'attente rend la persistance de la zone discernable, mais **coûte réellement 7 points d'intégrité dans le monde dangereux** |
| Après ingestion, manger une seconde baie | **4/4 contrastes encore identiques** | Répéter une ingestion ne discrimine pas les deux mécanismes dans cette fixture |
| Première ingestion d'une baie à effet −100 | **8 morts à t3** | Aucune observation subjective future possible ; 8 recherches Stage6 après ingestion sont logiquement absentes |
| Après entrée dans une zone cachée à dégâts répétés : préfixe préengagé `attendre` vs `se_deplacer(west)` | **8/8 mondes `wait` terminaux ; 8/8 mondes `escape` non terminaux** | Contraste physique externe, **pas** démonstration d'une politique de fuite connue ou choisie par I0 |
| Danger létal dès l'entrée dans une case | **8 morts à la première action** | La connaissance post-action n'est pas utilisable par l'individu terminé |
| Resource locale ou obstacle est visible avant toute action | **8/8 contrôles perceptifs** avec **0 pas** | Certaines préconditions sont observables sans s'exposer au danger |

La paire « baie toxique / danger apparu au moment de manger » est particulièrement discriminante. Les deux premières `collecter`, le `SimulationState` avant `manger`, l'action `manger`, et le `SimulationState` après `manger` sont **strictement égaux**. Le laboratoire sait que les deux causes sont différentes parce qu'il a contrôlé la physique et l'intervention cachée, mais **I0 ne peut pas déduire cette distinction de ces seules observations**. Un compte rendu Stage12 qui déclarerait « la baie m'a blessé » avec certitude serait abusif dans ce cas.

## Shadow : le vrai algorithme Stage6 et une mémoire accessible idéale

**56 recherches `SimulatorPlanner.search` réelles mais passives** ont été effectuées **sans déployer le moindre nouveau modèle chez I0 ni exécuter une commande choisie par le planificateur** :

- **32 recherches** juste avant la première ingestion, avec seulement les deux collectes antérieures dans une `FrozenTableEquipment` de laboratoire ;
- **24 recherches** juste après la première ingestion **non létale**, contenant uniquement deux collectes et l'ingestion déjà perçue. Aucune recherche postmortem n'est effectuée.

Le but artificiel est `food>=65`, profondeur maximale `3`, R=1. Ces paramètres sont figés dans le préenregistrement, pas choisis après observation. L'Equipment de chaque recherche est construit exclusivement avec les conséquences des actes antérieurs du **même monde physique**, sans données d'un autre monde, sans révélation du dommage latent de l'environnement et sans aucun événement futur.

**56/56 recherches retournent `incomplete_model`, zéro première arête connue.** Malgré une observation alimentaire antérieure dans les 24 cas vivants, la correspondance exacte `SimulationState × PrimitiveCommand` ne retrouve pas une transition utilisable depuis l'état présent. La raison immédiate est l'absence de clé complète actuelle, même lorsque des résultats sont déjà archivés dans la mémoire idéale du laboratoire. Le diagnostic Stage6 ne prouve **pas** que la commande alimentaire est impossible physiquement ni que l'individu réel sait apprendre les transitions dans cet ordre. L'horizon plus long **ne suffirait pas** à corriger ces 56 racines sans arête connue.

**Important :** l'ajout artificiel des transitions vécues à une table `FrozenTableEquipment` dans le *shadow* n'est **pas** l'implémentation du mécanisme réel d'apprentissage et de mémoire d'I0 ; c'est un témoin hypothétique maximisant l'accès aux exemples individuels sans oracle. Les jugements subjectifs de Stage12 ne sont jamais produits dans cet essai.

## Réponse H1/H2/H3 et limites

**H1 soutenue localement :** le modèle exact est incapable d'exploiter ces expériences antérieures au nouvel état accessible, même sous une hypothèse avantageuse de mémoire parfaite des transitions déjà vécues. Certaines connaissances perceptives élémentaires (baie présente, obstacle passable) sont pourtant accessibles sans action. **H2 : l'horizon seul est exclu pour les 56 recherches qui ne disposent d'aucun premier pas connu**, sans démonstration générale d'impossibilité physique. **H3 :** le résultat n'établit pas un défaut BFS ; il montre une limite effective de couverture et d'encodage, dont la correction d'architecture nécessiterait une démarche opérateur distincte.

L'affirmation scientifique ne porte que sur ces cellules préengagées et une physique déterministe de simulation, sans estimation d'une fréquence de danger naturelle. L'intervention environnementale est objectivement connue **du laboratoire**, jamais subjectivement de l'individu. Une observation de dommages est un signal corporel, non une expérience causale discriminante garantie, et le retrait spatial simulé n'est **pas une décision propre à I0**.

**Décision : expérimentation S-shadow techniquement PASS, déploiement cognitif NO-GO, A2.30 PARTIELLE, Stage12 PARTIAL, issue #110 OPEN, PR #191 DRAFT.** Contrôles indépendants T (archives) et U (physique rejouée) documentés séparément.
