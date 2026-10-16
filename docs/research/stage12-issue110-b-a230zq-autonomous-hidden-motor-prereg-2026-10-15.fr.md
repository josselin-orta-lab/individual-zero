# A2.30-ZQ : préenregistrement prospectif d'une mortalité motrice cachée lors de décisions réellement autonomes

**Date : 15 octobre 2026.** Verrouillage **AVANT tout code ZQ, toute naissance ZQ et tout résultat ZQ**. Base figée : PR #206, commit `016c5f8a3384d877339367337eead021f9029c7e`. La présente étude est une extension autonome parallèle aux PR #207 (exact reentry) et #208 (prédicteur partiel offline) : ne pas modifier ni dupliquer leurs données. L'issue #110 a été fermée administrativement sur `main`, mais cette fermeture n'est pas une preuve scientifique de sécurité ou de maîtrise autonome.

## Hypothèses préspécifiées

**H-ZQ1 (choix vécu et risque) :** au moins un I0 réellement autonome peut choisir lui-même une action motrice qui mène à une zone mortelle invisible dans une intervention expérimentale. À état perceptif de décision identique, le mouvement correspondant dans le monde sans zone mortelle peut survivre. **Si les individus n'exécutent pas le mouvement, le résultat est `NO_MOTOR_EXPOSURE`, et non une sécurité prouvée**.

**H-ZQ2 (limite épistémique) :** l'absence de signal visible de `lethal_zones` doit préserver les 11 champs du `SimulationState` accessible avant l'exposition, et ne doit pas modifier la décision sur la base d'une révélation extérieure. Les actions, motifs et préfixes réellement vécus doivent être mesurés et comparés; des identifiants de naissance différents ne donnent jamais, à eux seuls, un contrefactuel individuel parfait.

**H-ZQ3 (mortalité et subjectivité) :** si un mouvement choisi cause la mort, le dernier `world_transition_experienced` et sa clôture physique restent dans le WAL et le journal canonique, mais aucune nouvelle observation subjective, récupération M11, attribution de responsabilité après la mort ou continuation ne peut être inventée. Un verdict subjectif `self` sur le choix proximal (s'il existe) n'est **pas** une certification de la cause cachée du décès.

**H-ZQ4 (exploration utile) :** mesurer combien d'individus exécutent réellement des primitives `se_deplacer(east)` et `collecter(berry_b)`, combien de propositions/diagnostics Stage6 existent, et combien de frais UC sont réellement acceptés ou refusés. Ne jamais transformer une intention, un `plan_found`, un coût UC nul, ni une simulation shadow en action physiquement exécutée. Une absence de collecte B demeure une observation valide.

## Population et traitement figés

**24 I0 autonomes nouveaux**, tous avec vrai `Stage12Runtime`, WAL durable M11, `dual_scope_agency=True` à la naissance, modèle `FrozenTableEquipment` historique A uniquement, aucun exemple B prénatal, aucune commande motrice injectée, et **maximum 32 vrais pas de monde par naissance**, sans restauration/relance après mort. Échantillonnage déterministe factoriel :

- **Deux** profils alimentaires `restored` (food=35) et `sustained` (food=24) provenant de la cohorte ZB.
- **Trois** layouts `B_NONE`, `B_LOCAL`, `B_EAST` configurés à la naissance avec `berry_b` absente, sur la case de naissance ou adjacente à l'est.
- **Deux** effets ingestifs de B physiquement cachés, `benign` (gain 30, dommage 0) ou `toxic_lethal` (gain 30, dommage -100), **sans fournir ce paramètre au décideur**.
- **Deux** interventions motrices cachées, `motor_clear` ou `motor_hidden_lethal`. Cette dernière ajoute dès la naissance **uniquement** `Position(3,1)` à `WorldLayout.lethal_zones`. L'individu naît sur `Position(2,2)`. L'emplacement est choisi **prospectivement** parce que les journaux historiques ZB, déjà connus, montrent des mouvements volontaires nord puis est; **les résultats ZQ ne sont pas connus au verrouillage**. Le label « hidden » signifie absence de la zone dans les capteurs locaux, pas qu'une mort est garantie.
- Chaque quadruplet (profil, B-layout, effet B) constitue une paire **deux naissances distinctes** `motor_clear`/`motor_hidden_lethal`. Identités ZQ uniques qui ne réemploient jamais les identités des douze vies ZB ou celles des autres bras.

**Vingt-quatre naissances, douze paires et 768 pas autonomes au maximum**. Si les 12 bras cachés meurent au pas 2 et les contrôles atteignent le pas 32, **408 pas seraient observés**, mais **ce nombre est une prédiction hypothétique issue de ZB, pas un critère de PASS ni une observation**. Toute divergence est conservée et expliquée à partir des reçus, sans modification de la matrice.

Les seuls paramètres changés entre deux bras d'une paire sont : l'identité unique du corps, la zone létale cachée externe et la version de la configuration *physique* explicitement auditée. Interdire de modifier l'équipement cognitif, les objectifs, la compétition, l'action-control, les UC, le budget de sommeil, Stage9 ou le programme de décision. Le moteur physique peut produire d'autres conséquences après la rencontre de la zone. Les différentes identités peuvent biaiser les états internes stochastiques; la parité subjective et comportementale **doit être testée et non présumée**.

## Protocole de jugement et de mesures

Pour chaque I0 :
1. Créer une seule naissance avec le code de production existant utilisé par ZB, en ne patchant **qu'au moment de la construction** `Stage12Runtime(world_config, layout)`; aucune `life.run_step` sous patch et aucune commande `WorldBody.apply` imposée. Les scénarios cachés sont initialisés à la naissance, puis immuables.
2. Contrôler que la capture initiale `SimulationState` correspond **exactement** au root original ZB du profil/layout/effet B, par hash et contenu. Refuser tout capteur donnant la zone mortelle. Contrôler la version/hash exact du modèle A historique, et l'absence de connaissances B dans le modèle.
3. Exécuter `life.run_step()` tant que le corps est actif, **au maximum 32** fois. Si une action sélectionnée est rejetée par UC ou le monde, la compter et la décrire, ne jamais la remplacer par une commande voulue par le laboratoire. Si le runtime ne peut pas progresser, déclarer explicitement l'échec, sans cacher les individus concernés.
4. Archiver `canonical.jsonl`, WAL `life.wal` complet, résumé par vie et les reçus physiques. Vérifier en lecture indépendante la chaîne de hash, la correspondance M11 WAL/journal, la clôture P48 par action, les commandes/reçus d'observation, les jugements proximal et distal, les UC et les motifs des actions. Les causes létales, scénarios et paramètres cachés sont exclusivement des **reçus externes**, jamais une nouvelle `LivedCognitiveObservation`.
5. Reconstituer chaque paire jusqu'à la première tentative d'entrée dans la zone `Position(3,1)`, par commande **effectivement choisie** `se_deplacer(east)` depuis `Position(2,1)`. Comparer captures visibles, actes et motivation avec des clés `(t_monde,attempt_ref)`; n'autoriser une attribution au traitement motor-zone **que** pour les paires où le préfixe est comparativement contrôlé (sinon `UNPAIRED`).
6. Compter les décès motrices, leurs raisons externes, le dernier reçu physique, et l'absence de toute continuation subjective; vérifier que les autres décès éventuels (notamment ingestion toxique) sont codés sous une **cause distincte**. Compter toutes les 24 naissances dans les dénominateurs, y compris les morts précoces.
7. Conserver distinctes les mesures `UC de calcul reconnues/refusées`, `UC de responsabilité subjective` et `nombre de pas`. Ne calculer aucun coût UC synthétique estimé à partir des pas; utiliser seulement les vrais reçus de charge.

## Falsifications obligatoires avant PASS

Au minimum : injection d'un attribut de zone létale dans le `SimulationState`; remplacement d'une commande volontaire par une commande de laboratoire; absence de `command_experienced` ou de `world_transition_experienced` pour un pas compté; divergence WAL/chaîne d'export; fausse responsabilité `self` du décès; collecte B inventée; utilisation d'une observation postmortem comme vécu; reprise d'un corps mort; faux traitement des motifs/UC; substitution du journal d'une autre naissance ou du témoin de l'autre bras; fausse garantie de sûreté à partir d'une confiance 1.

Les tests adversariaux doivent échouer nettement si ces manipulations sont détectables par les reçus. Les deux Python 3.11 et 3.12 doivent produire des archives auditables; les variations numériques ULP historiquement connues dans ZB sont à expliquer sans effacer les divergences. Deux versions Python **ne doublent pas** le nombre de nouveaux I0 indépendants.

## Critères de conclusion

**PASS technique de ZQ** : 24 naissances distinctes, effectifs factoriels exacts, capteurs sans fuite, commandes entièrement autonomes, WAL et P48 valides, mortalité irréversible, provenance des motifs/UC et des paires démontrée sous deux Python; aucune modification de la norme ni du runtime. **H-ZQ1** : `SUPPORTED` uniquement si au moins une action motrice sélectionnée produit réellement le contraste survie/décès sur deux préfixes appariés; `UNRESOLVED` sinon. **H-ZQ2** : parité initiale et pré-exposition vérifiée indépendamment; **H-ZQ3** : audit des bornes terminales. **H-ZQ4** : descriptif seulement, jamais une validation de l'objectif alimentaire B.

**Aucune activation par défaut de l'exploration, aucun transfert de mémoire d'un autre monde, aucune baisse du garde-fou Stage9/DC-05, aucun accès Oracle, aucun changement de mortalité M11 ou de `docs/architecture/reference/en/mvp-specification-v1.3.1.md`.** PR scientifique empilée et DRAFT, Stage12 **PARTIAL**, A2.30 **PARTIELLE**. L'issue #110 est **fermée administrativement** (observé le 15 octobre), sans réouverture automatique ni conclusion scientifique PASS.
