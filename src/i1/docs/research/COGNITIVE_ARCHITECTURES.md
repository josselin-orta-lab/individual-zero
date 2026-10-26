# Étude externe archivée : six architectures pour Individual Zero / I1

> Cette étude est un instantané du **26 octobre 2026**, non un état à jour des capacités actuelles. Voir [l'index](REFERENCES.md) pour le protocole de relecture et [les questions](RESEARCH_QUESTIONS.md) pour les hypothèses.

# Individual Zero / I1 : dossier de recherche externe

**Date : 26 octobre 2026.** Lecture critique de six architectures cognitives, de leurs sources et de leurs résultats, puis cartographie des mécanismes pertinents pour I1.

**I1 audité :** [`main` `972aac6ca64a8517dbbee8604f7a1e5108474473`](https://github.com/josselin-orta-lab/individual-zero/tree/972aac6ca64a8517dbbee8604f7a1e5108474473).

**Portée :** recherche et proposition expérimentale. Aucun code I1 modifié, aucun benchmark externe exécuté, aucune revendication de maturité scientifique supplémentaire.

## 1. Méthode et niveaux de preuve

- **SOURCE** : lecture directe du code, du manuel, d'un article ou d'une licence. Les liens GitHub sont figés aux SHA de cette collecte.
- **RESULTAT PUBLIE** : constat rapporté par les auteurs, non reproduit dans ce dossier.
- **INFERENCE I1** : application potentielle à I1. Ce n'est ni une conclusion de l'article ni une propriété démontrée d'I1.
- **A TESTER** : hypothèse falsifiable, avec témoins négatifs et critère de validation.

La théorie de référence reste *Architecture d'un individu artificiel, v2 enrichie* (26 septembre 2026), notamment ses blocs 4 (prédiction), 7-8 (homéostasie / allostasie), 22 (curiosité), 25 (métacognition), 28-34 (mémoires, consolidation), 39-42 (décision et crédit causal) et 43 (sommeil). Les rapprochements théoriques sont des jugements de conception, pas des preuves expérimentales.

## 2. Inventaire des projets et versions figées

| Projet | Dépôt / publication | Version de lecture | Licence / disponibilité |
|---|---|---|---|
| Soar | [SoarGroup/Soar](https://github.com/SoarGroup/Soar) | `3fc337a1ab2d` | BSD, verified LICENSE.md |
| MicroPsi2 | [joschabach/micropsi2](https://github.com/joschabach/micropsi2) | `74a2642d20da` | MIT, verified license.txt (unless marked otherwise) |
| OpenCog Hyperon | [trueagi-io/hyperon-experimental](https://github.com/trueagi-io/hyperon-experimental) | `3f76dc460da6` | MIT, verified LICENSE |
| DreamerV3 | [danijar/dreamerv3](https://github.com/danijar/dreamerv3) | `e01491fad643` | MIT, GitHub repository metadata |
| LIDA Framework | [CognitiveComputingResearchGroup/lida-framework](https://github.com/CognitiveComputingResearchGroup/lida-framework) | `26bc3b2b34bf` | LIDA Framework Non-Commercial License v1.0, source headers and license/ |
| iSEED | [Article iSEED](https://doi.org/10.3389/fnbot.2026.1920808) | Article 2026-09-17 | article CC BY; source license not verified |

## 3. Etude par projet : mecanismes, preuves, limites, transferts possibles

### Soar : utiliser les souvenirs et les sous-buts sans les transformer en ordres

**SOURCE.** Son mécanisme de mémoire épisodique conserve le flux d'expérience et permet une recherche par indices positifs et négatifs. Les réponses exposent score de correspondance, date, et parfois correspondance structurelle. La documentation reconnaît des risques de coûts combinatoires ou de balayage linéaire. Sources : [mémoire épisodique](https://soar.eecs.umich.edu/soar_manual/07_EpisodicMemory/) et [mémoire sémantique](https://soar.eecs.umich.edu/soar_manual/06_SemanticMemory/).

**SOURCE.** Le RL sait propager une somme actualisée de récompenses sur des intervalles sans nouvelle sélection d'opérateur. Le *chunking* condense un raisonnement ayant résolu un blocage en une production plus directe et prévoit des outils d'explication ainsi que des avertissements contre la surgénéralisation. Sources : [RL](https://soar.eecs.umich.edu/soar_manual/05_ReinforcementLearning/) et [chunking](https://soar.eecs.umich.edu/soar_manual/04_ProceduralKnowledgeLearning/).

**INFERENCE I1.** Les concepts réutilisables sont : requêtes épisodiques indexées, recherche bornée par contexte/commande, trace explicative d'une connaissance compilée, attribution du crédit à travers `collecter -> manger`. Conserver la propriété Memory, le paiement UC et le veto d'ActionControl. Ne pas introduire un moteur de règles Soar ni des faits externes à la naissance.

### MicroPsi2 : besoins, urgence, perception orientée et plans interruptibles

**SOURCE.** Bach (2015) distingue l'intensité d'un besoin (*urge*) et son urgence, laquelle dépend du risque de franchir rapidement un seuil critique. La satisfaction/frustration d'un besoin renforce des associations entre situations, actions et séquences antérieures ; les buts sont dérives de ces associations. Article : [Modeling Motivation in MicroPsi 2](https://agi-conf.org/2015/wp-content/uploads/2015/07/agi15_bach.pdf). Le prolongement de 2019 décrit l'effet de la satisfaction anticipée et de la modulation affective : [article 2019](https://agi-conf.org/2019/wp-content/uploads/2019/07/paper_30.pdf).

**CODE.** [`stepoperators.py`](https://github.com/joschabach/micropsi2/blob/74a2642d20da9da1d64acc5e4c11aeabee192a27/micropsi_core/nodenet/stepoperators.py) contient `DoernerianEmotionalModulators`, combinant urgence, importance d'intention, succès attendus et changements de besoin. [`nodefunctions.py`](https://github.com/joschabach/micropsi2/blob/74a2642d20da9da1d64acc5e4c11aeabee192a27/micropsi_core/nodenet/nodefunctions.py) implémente des scripts hiérarchiques avec chaînes d'inhibition, attente, confirmation et échec. Les fonctions de la théorie ne sont pas toutes présentes dans ce code historique.

**INFERENCE I1.** Conserver les besoins corporels réels inchangés, mais examiner une urgence prédictive distincte de la pression instantanée ; faire remonter un souvenir par sa pertinence pour un besoin, non par un privilège moteur. L'intention prospective doit s'interrompre lorsque le contexte change (#326). Ne pas importer des variables émotionnelles supplémentaires pour l'instant.

### LIDA : attention, diffusion et apprentissage procédural

**CODE.** Les *codelets* d'attention constituent des coalitions en concurrence ; [`GlobalWorkspaceImpl.java`](https://github.com/CognitiveComputingResearchGroup/lida-framework/blob/26bc3b2b34bf7ccfe2c62e1f12314db27d9719ec/src/edu/memphis/ccrg/lida/globalworkspace/GlobalWorkspaceImpl.java) possède décroissance, période réfractaire et diffusion aux abonnés ; [`ProceduralMemoryImpl.java`](https://github.com/CognitiveComputingResearchGroup/lida-framework/blob/26bc3b2b34bf7ccfe2c62e1f12314db27d9719ec/src/edu/memphis/ccrg/lida/proceduralmemory/ProceduralMemoryImpl.java) indexe les schémas par contexte. [`EpisodicMemoryImpl.java`](https://github.com/CognitiveComputingResearchGroup/lida-framework/blob/26bc3b2b34bf7ccfe2c62e1f12314db27d9719ec/src/edu/memphis/ccrg/lida/episodicmemory/EpisodicMemoryImpl.java) exploite une mémoire distribuée clairsemée, mais sa méthode `learn()` est annotée `TODO`. La synthèse [Learning in LIDA](https://doi.org/10.1016/j.cogsys.2020.11.001) reconnaît le décalage entre engagement conceptuel et implémentation.

**INFERENCE I1.** Représenter une compétence comme `contexte -> action -> conséquence attendue` peut aider la consolidation, mais son stockage ne doit pas l'autoriser à agir. Une politique de décroissance des associations insuffisamment reconfirmées mérite un examen futur. Ne pas copier le code Java, sous licence **non commerciale**.

### DreamerV3 : prédiction des transitions et planification interne

**RESULTAT PUBLIE.** [Nature 2025](https://doi.org/10.1038/s41586-025-08744-2) rapporte plus de 150 tâches sur huit domaines avec un algorithme largement commun. L'agent apprend un état latent récurrent, prédit la suite sous l'effet d'une action et utilise des trajectoires imaginées pour mettre à jour acteur et critique.

**CODE.** [`rssm.py`](https://github.com/danijar/dreamerv3/blob/e01491fad6434b2245a3b8ca201dd7faedcc458c/dreamerv3/rssm.py) expose `observe`, `imagine` et la perte du modèle de dynamique. [`agent.py`](https://github.com/danijar/dreamerv3/blob/e01491fad6434b2245a3b8ca201dd7faedcc458c/dreamerv3/agent.py) relie modèle, récompense, continuation et apprentissage acteur/critique. Le [`configs.yaml`](https://github.com/danijar/dreamerv3/blob/e01491fad6434b2245a3b8ca201dd7faedcc458c/dreamerv3/configs.yaml) consulté indique `imag_length: 15` et `horizon: 333` dans sa configuration par défaut ; ces paramètres **ne sont pas des prescriptions pour I1**. Le dépôt précise qu'il s'agit d'une réimplémentation indépendante de Google/DeepMind.

**DONNEES.** Les courbes par domaines et baselines sont accessibles dans [`scores/`](https://github.com/danijar/dreamerv3/tree/e01491fad6434b2245a3b8ca201dd7faedcc458c/scores). L'inventaire de 27 fichiers JSON compressés figure dans le manifeste structuré. Les fichiers binaires n'ont pas été téléchargés dans ce dossier.

**INFERENCE I1.** Commencer par un petit modèle d'effet corporel conditionné par l'action, basé sur de vraies transitions première personne, avant toute simulation imaginative. Mesurer sa calibration sur des expériences tenues à l'écart. Un monde imaginé faux pourrait entraîner des décisions plus mauvaises qu'une absence de planification.

### OpenCog Hyperon : structures de connaissance explicites

**CODE.** Le [`README` Hyperon](https://github.com/trueagi-io/hyperon-experimental/blob/3f76dc460da6961f57f69f6c3e550c59c74ada83/README.md) décrit MeTTa et un noyau Rust avec espaces de connaissances et interfaces Python. Le projet est en pré-alpha. Les exemples séparés [ECAN](https://github.com/trueagi-io/metta-examples/tree/main/ecan) montrent une attention à intensité variable ; les exemples [STRIPS](https://github.com/trueagi-io/metta-examples/tree/main/strips) décrivent des relations de préconditions et d'effets. Il ne faut pas confondre exemples d'inférence et apprentissage de ces règles par un agent vivant.

**INFERENCE I1.** On pourrait s'inspirer de schémas lisibles et traçables pour `source -> hypothèse -> contexte -> incertitude`, sans remplacer `CausalModel` par Hyperon ni injecter des règles `WorldBody` dans la connaissance de l'individu.

### iSEED (2026) : structurer les épisodes et mesurer la consolidation

**RESULTAT PUBLIE.** Le système observe en continu à partir d'une tête robotique iCub, avec cinq caractéristiques perceptives ; une rupture d'épisode intervient lors d'une déviation perceptive importante. Les épisodes sont condensés en vecteurs de dimension 528 incluant des composantes issues de modèles préentraînés ; une consolidation quotidienne les regroupe sans étiquettes supervisées. Des attentes sur les contextes temporels sont ensuite évaluées. [Article 2026](https://doi.org/10.3389/fnbot.2026.1920808).

**DONNEES PUBLIEES.** Bureau : 449 épisodes sur 24 h/4 jours ; conférence : 2304 épisodes sur 15 h/3 jours. Reconnaissance du contexte (bureau) : 0.23, 0.87, 0.93 sur les jours successifs évalués ; cohérence d'anticipation 0.24, 0.95, 0.96. En conférence, la cohérence d'anticipation reste faible (0.26 puis 0.08). Ces mesures sont celles des auteurs, non reproduites ici.

**LIMITES.** L'article indique explicitement que l'influence de la mémoire sur le choix d'action n'est pas encore implémentée ; code source officiel non vérifié et données brutes promises dans un Zenodo à accès restreint sur demande.

**INFERENCE I1.** Introduire ou tester une segmentation des expériences guidée par la surprise sur les signaux déjà disponibles : position, perception locale, action et corps. Ne pas importer de perception visuelle ni de 528 dimensions. Tester la stabilité et l'utilité des contextes consolidés avant tout renforcement moteur.

### Table de resultats iSEED extraite de la publication (donnees des auteurs)

| Milieu | Episodes et duree | Reconnaissance par jour | Coherence de l'attente par jour |
|---|---|---|---|
| Bureau | 449 / 24 h / 4 jours | non mesuree ; 0,23 ; 0,87 ; 0,93 | non mesuree ; 0,24 ; 0,95 ; 0,96 |
| Conference | 2 304 / 15 h / 3 jours | non mesuree ; 0,83 ; 0,73 | non mesuree ; 0,26 ; 0,08 |

La reconnaissance signifie ici la concordance des etiquettes de contexte entre traitement en ligne et reclassement apres consolidation. Ce n'est ni une mesure de survie ni un gain de decision. Les comptes quotidiens et la stabilite temporelle figurent egalement dans le JSON. [Tableau 1 de l'article](https://doi.org/10.3389/fnbot.2026.1920808).

## 4. Etat I1 recoupe aux resultats externes

- `ValueAndNeeds.reward_between` calcule la différence entre les sommes des écarts **absolus** aux consignes. L'issue [#306](https://github.com/josselin-orta-lab/individual-zero/issues/306) documente un crédit négatif après une hydratation améliorant les réserves mais dépassant la consigne.
- `LinearTDValues` a déjà `PendingTDSegment` et des traces d'éligibilité ; la question est l'effet **effectivement attribué**, pas seulement l'existence de traces. Voir [#305](https://github.com/josselin-orta-lab/individual-zero/issues/305).
- `EpisodicMemory.closed_applied_action_witnesses` assemble des commandes physiques et leurs transitions personnellement admissibles, sans attribuer de causalité. La garde d'accès parcourt **les 32 derniers épisodes fermés**, non toute la vie. Voir [#535](https://github.com/josselin-orta-lab/individual-zero/issues/535).
- La jonction avec Stage8 générique est actuellement **sans score ajouté** (`context_score_applied=False`) ; de simples reçus de rappel ne prouvent pas que la décision change. Voir [#526](https://github.com/josselin-orta-lab/individual-zero/issues/526).
- La consolidation Stage10 possède six passes, mais leur publication cognitivement utile, la persistance multi-propriétaire et leur influence sur les choix restent des questions scientifiques ouvertes. Voir [#293](https://github.com/josselin-orta-lab/individual-zero/issues/293).
- Le code actuel possède un prédicteur hydrique à partir des propres expériences, mais pas encore un modèle général des conséquences corporelles pour toute primitive.

## 5. Regles d'integration non negociables

1. I0 reste strictement inchangé ; I1 conserve son monde et son corps simplifiés.
2. Aucune connaissance oracle sur les effets cachés, les sources, les dangers ou l'avenir n'est injectée dans les propriétaires cognitifs.
3. Les besoins proposent des motifs ; aucune mémoire, procédure, prédiction ou règle apprise ne court-circuite Competition ou ActionControl.
4. Le calcul du sommeil (P-42) et de la veille (P-43) reste payé, borné et auditable ; aucun accès gratuit ou lecture illimitée au journal.
5. La provenance des souvenirs, la fermeture d'épisode, la continuité de vie M11 et la mort irréversible restent préservées.
6. Séparer tests de code, comportement observé, apport causal et preuve scientifique répliquée.
7. Aucune architecture externe ne devient une autorité normative. Un mécanisme n'est adopté que si un test I1 montre son utilité ou corrige un défaut causal démontré.
8. Respecter les licences : BSD / MIT avec notices ; LIDA non commerciale, aucun code repris sans analyse juridique.

## 6. Hypotheses de recherche et criteres de validation

Les fiches suivantes sont des **propositions**, non des travaux déjà effectués. L'ordre découle des dépendances de fiabilité, pas d'un budget ou d'une échéance.

### H01 / P0 : Cohérence du signal de valeur homéostatique

**Hypothèse :** Une valeur sensible aux déficits évite de pénaliser une amélioration corporelle viable tout en conservant les coûts métaboliques réels.

**Rattachement I1 :** `ValueAndNeeds, LinearTDValues` ; `src/i1/modules/value_needs.py`, `src/i1/modules/td_values.py`. Issues : [#306](https://github.com/josselin-orta-lab/individual-zero/issues/306).

**Idées scientifiques :** MicroPsi2 : besoins et satisfaction; Soar : récompense retardée.

**Expérience :** Faire naître des I1 dans des mondes et graines appariés ; comparer uniquement la définition de la valeur par écart absolu et par déficit, avec dépassement de la consigne hydrique et collecte avant consommation.

**Contrôles :** physique identique; Competition et ActionControl inchangés; contrôle sans lecture du signal appris.

**Condition de validation :** La valeur suit les améliorations corporelles viables sans dégrader les choix autonomes ni la survie mesurée ; les contre-exemples sont explicités

### H02 / P0 : Attribution du crédit aux actions préparatoires

**Hypothèse :** Plusieurs actions volontaires peuvent recevoir une part pertinente du bénéfice physique ultérieur sans identité motrice forcée.

**Rattachement I1 :** `LinearTDValues, CausalModel, EpisodicMemory` ; `src/i1/modules/td_values.py`, `src/i1/modules/causal_model.py`, `src/i1/modules/memory.py`. Issues : [#305](https://github.com/josselin-orta-lab/individual-zero/issues/305), [#304](https://github.com/josselin-orta-lab/individual-zero/issues/304).

**Idées scientifiques :** Soar : extension temporelle du renforcement; MicroPsi2 : chaînes besoin-situation.

**Expérience :** Comparer des naissances appariées avec deux baies dont les propriétés nourrissantes cachées sont inversées selon le monde ; examiner segments TD, traces et séquences de collecte puis consommation, avec ablation de la lecture.

**Contrôles :** aucune récompense synthétique; aucune consommation imposée; identité alimentaire cachée.

**Condition de validation :** Les actions futures sélectionnent plus souvent la chaîne réellement nourrissante dans les deux permutations, sans fausse attribution de succès

### H03 / P0 : Publication sémantique durable et causalement utile

**Hypothèse :** Des expériences personnelles closes engendrent une connaissance durable non vide qui peut modifier une action future.

**Rattachement I1 :** `EpisodicMemory, Consolidation, CausalModel, ValueAndNeeds` ; `src/i1/modules/consolidation_semantics.py`, `src/i1/runtime/i1_cognitive_publication.py`. Issues : [#293](https://github.com/josselin-orta-lab/individual-zero/issues/293).

**Idées scientifiques :** Soar : distinction épisodique-sémantique; LIDA : procédures contextuelles; iSEED : stabilité après consolidation.

**Expérience :** Tracer les formes sémantiques de chaque propriétaire avant et après consolidation, les références vécues exactes, les UC, la reprise froide M11, le rappel et le choix ultérieur.

**Contrôles :** lecture mémoire désactivée; consolidation sans source; mises à jour simultanées issues de la veille.

**Condition de validation :** Chaîne effectivement observée de la source à la connaissance, au choix et à son effet, non expliquée par Q ou la perception seules

### H04 / P1 : Rappel ancien indexé et payé en UC

**Hypothèse :** Une recherche par indices donne accès à des souvenirs plus anciens que les 32 derniers épisodes sans parcours illimité.

**Rattachement I1 :** `EpisodicMemory` ; `src/i1/modules/memory.py`. Issues : [#535](https://github.com/josselin-orta-lab/individual-zero/issues/535).

**Idées scientifiques :** Soar : requêtes par indices, métadonnées de correspondance et risques de coût.

**Expérience :** Créer plus de 32 épisodes personnellement clos ; retenir une action ancienne rare ou contradictoire ; tester propriété et index de source, puis un unique rappel borné et payé.

**Contrôles :** références en double; épisodes futurs ou non clos; vue M11 périmée; source inconnue.

**Condition de validation :** Une source ancienne authentique redevient accessible par indice pertinent avec un travail mesuré strictement borné et sans lecture gratuite

### H05 / P1 : Prédiction générique des effets corporels

**Hypothèse :** Les transitions personnellement observées permettent d’estimer avec incertitude les effets physiques des actions et de s’abstenir face à l’inconnu.

**Rattachement I1 :** `CausalModel, ValueAndNeeds` ; `src/i1/modules/lived_prediction.py`, `src/i1/modules/causal_model.py`. Issues : [#473](https://github.com/josselin-orta-lab/individual-zero/issues/473), [#526](https://github.com/josselin-orta-lab/individual-zero/issues/526).

**Idées scientifiques :** DreamerV3 : prédictions conditionnées par l’action; LIDA : effets attendus associés aux schémas.

**Expérience :** Prédire des variations de variables corporelles déjà existantes pour les primitives ordinaires, à partir de preuves vécues indépendantes ; mesurer erreur, signe et calibration sur des épisodes non utilisés pour apprendre.

**Contrôles :** aucun accès privilégié à WorldBody; abstention pour les contextes non observés; aucun bonus Stage8 automatique.

**Condition de validation :** Erreur de prédiction et incertitude mieux calibrées que les références de récence et de variation nulle

### H06 / P1 : Influence non redondante des souvenirs sur Competition

**Hypothèse :** Un rappel peut apporter à Stage8 une information absente de Q et Stage6 et affecter naturellement certaines options.

**Rattachement I1 :** `Stage8, Competition, ActionControl` ; `src/i1/runtime/i1_natural_runtime.py`, `src/i1/modules/td_values.py`. Issues : [#526](https://github.com/josselin-orta-lab/individual-zero/issues/526), [#317](https://github.com/josselin-orta-lab/individual-zero/issues/317), [#512](https://github.com/josselin-orta-lab/individual-zero/issues/512).

**Idées scientifiques :** LIDA : comportements conditionnés par contexte; Soar : usage d’une connaissance rappelée pour choisir.

**Expérience :** Comparer des vies appariées avec ou sans la lecture mémoire pertinente, en conservant l’état physique, la valeur Q et la base Stage6 identiques.

**Contrôles :** absence d’histoire; preuves contradictoires; concurrents éveillés; budget dégradé.

**Condition de validation :** Des choix changent pour un effet attendu justifié indépendamment, sans privilège moteur ni double comptage

### H07 / P1 : Mémoire du sommeil entier et de ses bénéfices retardés

**Hypothèse :** La valeur du sommeil dépend des conséquences physiques et cognitives personnellement éprouvées, pas du nom de la commande.

**Rattachement I1 :** `EpisodicMemory, Consolidation, ValueAndNeeds` ; `src/i1/runtime/i1_natural_sleep.py`, `src/i1/runtime/stage10_runtime.py`. Issues : [#467](https://github.com/josselin-orta-lab/individual-zero/issues/467), [#473](https://github.com/josselin-orta-lab/individual-zero/issues/473), [#465](https://github.com/josselin-orta-lab/individual-zero/issues/465).

**Idées scientifiques :** iSEED : épisodes indexés dans le temps; MicroPsi2 : distinction besoin-urgence.

**Expérience :** Comparer des sommeil et attentes vécus au même endroit, l’état au réveil, les transitions corporelles complètes et les conséquences cognitives ultérieures ; aucune récompense accordée à la consolidation sans effet mesuré.

**Contrôles :** dommage ambiant du lieu; énergie saturée; alerte hydrique de réveil; reprise M11.

**Condition de validation :** Prédictions correctes selon les situations et absence de domination apprise du sommeil lorsqu’une preuve contraire existe

### H08 / P1 : Segmentation des expériences par surprise et stabilité

**Hypothèse :** Des changements imprévus de prédiction peuvent délimiter les épisodes mieux que des durées fixes seules.

**Rattachement I1 :** `EpisodicMemory, Perception` ; `src/i1/modules/memory.py`, `src/i1/modules/perception.py`.

**Idées scientifiques :** iSEED : ruptures épisodiques par déviation et stabilité des contextes.

**Expérience :** Utiliser uniquement les signaux de corps, position, action et perception existants ; comparer les frontières, la conservation des événements rares, la stabilité des contextes et la prédiction future.

**Contrôles :** aucun nouveau capteur social; aucune vision préentraînée; frontières existantes préservées.

**Condition de validation :** Moins de fusions entre expériences incompatibles et meilleur rappel tardif sans explosion des UC ou faux découpages

### H09 / P2 : Compilation de procédures sur preuve personnelle

**Hypothèse :** Les réussites répétées peuvent devenir des procédures contextuelles moins coûteuses et réversibles lors des échecs.

**Rattachement I1 :** `Consolidation, ProceduralMemory, Competition` ; `src/i1/modules/consolidation_semantics.py`, `src/i1/runtime/i1_active_value_needs.py`. Issues : [#326](https://github.com/josselin-orta-lab/individual-zero/issues/326).

**Idées scientifiques :** Soar : compilation après résolution de blocage; LIDA : schémas conditionnels; MicroPsi2 : scripts hiérarchiques.

**Expérience :** Tester des séquences vécues répétées dans des contextes variés ; mesurer gain en UC, incertitude et retour à la délibération après échec.

**Contrôles :** aucun script exécutable par défaut; interruption si les besoins changent; rejet du contexte inconnu.

**Condition de validation :** Moins de dépenses UC par succès répété sans perte de sécurité ni d’adaptation

### H10 / P2 : Séparer intensité du besoin et urgence

**Hypothèse :** Le déficit, le délai prévu avant le danger et le coût des occasions manquées sont des signaux distincts.

**Rattachement I1 :** `ValueAndNeeds, GoalManager` ; `src/i1/modules/value_needs.py`, `src/i1/modules/goal_manager.py`. Issues : [#307](https://github.com/josselin-orta-lab/individual-zero/issues/307), [#453](https://github.com/josselin-orta-lab/individual-zero/issues/453).

**Idées scientifiques :** MicroPsi2 2015 et 2019 : pression d’un besoin et urgence.

**Expérience :** Mesurer intensité et horizon de risque inférés des dynamiques corporelles actuelles ; conserver les propositions de besoins et la compétition motrice indépendantes.

**Contrôles :** aucune obligation programmée de boire ou manger; télémétrie physique intacte; aucun accès oracle au délai avant la mort.

**Condition de validation :** Meilleure calibration des urgences et changements de buts adaptés à l’approche des seuils critiques sans oscillation excessive

### H11 / P2 : Fiabilité adaptative et changement de contexte

**Hypothèse :** Les preuves incertaines ou contradictoires doivent ajuster la confiance plutôt que produire un savoir catégorique faux.

**Rattachement I1 :** `CausalModel, MetacognitionHealth` ; `src/i1/modules/causal_model.py`, `src/i1/modules/memory.py`. Issues : [#535](https://github.com/josselin-orta-lab/individual-zero/issues/535).

**Idées scientifiques :** iSEED : stabilité contextuelle; Soar : score de correspondance et âge; DreamerV3 : stabilité aux échelles de récompense.

**Expérience :** Faire varier les effets d’une ressource entre conditions de monde isolées, puis comparer confiance, abstention et réapprentissage.

**Contrôles :** aucun indicateur caché de changement; aucune suppression arbitraire de souvenirs.

**Condition de validation :** Incertitude calibrée et révision ultérieure des choix avec conservation des preuves contradictoires

### H12 / P3 : Simulation interne courte et bornée

**Hypothèse :** Une fois les modèles d’effets fiables, de courtes projections internes peuvent améliorer le choix sans consulter la vérité du simulateur.

**Rattachement I1 :** `Planning, CausalModel, ValueAndNeeds` ; `src/i1/modules/stage6_planning.py`, `src/i1/modules/lived_prediction.py`.

**Idées scientifiques :** DreamerV3 : trajectoires imaginées; Hyperon : relations symboliques explicites.

**Expérience :** Comparer des projections apprises sur un pas et sur deux ou trois pas, uniquement à partir des prédictions personnelles et avec référence Q seule ; mesurer les UC.

**Contrôles :** aucun oracle WorldBody; abstention devant branches trop incertaines; UC réellement comptabilisées.

**Condition de validation :** Le bénéfice prédictif et décisionnel dépasse son coût de calcul et le risque d’erreur du modèle

## 7. Protocoles d'experimentation transversaux

- **Niveau A (logiciel)** : preuves de provenance, cas invalides, déduplication, budgets UC, invariants mort/cold recovery et absence d'oracle.
- **Niveau B (capacité)** : mécanisme appelé dans une vie réelle, trace observable, état propre de l'owner avant/après.
- **Niveau C (effet causal)** : même physique + graines appariées + expérience inversée + suppression ciblée de lecture ; différence sur l'action réelle, pas seulement sur l'activation d'une option.
- **Niveau D (bénéfice généralisé)** : réplications indépendantes, critères avant naissance, incertitude statistique, nouvel environnement, performances retenues sur longue vie et mesure de la survie censurée à droite.

Le nombre de récompenses, de souvenirs ou de confirmations de consolidation n'est jamais un substitut au niveau C/D.

## 8. Donnees experimentales vraiment recuperees

Ce dossier inclut des **données structurées bibliographiques et techniques** : `recherche_i1_donnees_structurees_2026-10-26.json` (projets, SHA, licence, résultats, hypothèses inventaire DreamerV3 et metriques iSEED), et `recherche_i1_sources_2026-10-26.csv` (références de fichiers à ouvrir ultérieurement).

- DreamerV3 : **27 fichiers JSON.gz** de séries de scores sont publiés (dont proprioception, vision, Minecraft et procgen). Leur liste, tailles et URLs figées figurent dans le JSON ; les octets binaires **ne sont pas copiés** ici. Ils restent directement consultables dans le dépôt.
- iSEED : seuls les **tableaux publiés dans l'article** et sa méthodologie sont repris sous forme de métadonnées. Le jeu de données brutes n'est pas public en libre téléchargement selon la section disponibilité ; aucune donnée individuelle n'a été importée.
- Soar, MicroPsi2, LIDA et Hyperon : sources et fichiers ciblés ont été lus sur les dépôts officiels via GitHub ; ils sont référencés, pas recopiés ni exécutés.

## 9. Limites de cette recherche

- Les conclusions sur la capacité autonome d'I1 sont des hypothèses, sans nouvelle campagne M11 lancée dans ce travail.
- Des articles présentent des concepts et des performances sur des domaines qui ne sont pas notre monde simplifié : les chiffres ne sont pas directement comparables.
- Le dépôt LIDA public date de 2016, et le code MicroPsi2 de 2022 au plus tard ; un article théorique plus récent n'implique pas une version de code plus récente.
- Les courbes DreamerV3 et les jeux de données iSEED n'ont pas fait l'objet d'une réanalyse numérique indépendante.
- Les liens figés et les statuts cités correspondent à la date indiquée et pourront évoluer.

## Conclusion scientifique

La recherche externe ne justifie **aucune substitution architecturale**. Elle suggère surtout une trajectoire d'expériences : (1) valeur corporelle fidèle ; (2) attribution des effets retardés ; (3) connaissances consolidées durables ; (4) accès épisodique utile et borné ; (5) prédiction conditionnelle ; (6) modification volontaire et démontrée de la décision ; (7) compétences compilées et révisables. La mesure finale reste l'apprentissage naturel et autonome de l'individu I1 au sein de sa propre vie.