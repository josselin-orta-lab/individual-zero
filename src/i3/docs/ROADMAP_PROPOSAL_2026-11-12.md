# I3 — proposition de feuille de route de développement (12 novembre 2026)

**Statut : PROPOSÉ (non autoritaire).** Ce document n'est ni un ADR, ni un plan en vigueur, ni une autorisation, ni une revue indépendante. C'est une analyse produite par un agent, soumise à l'arbitrage du propriétaire. Tant qu'il n'est pas arbitré, les seules autorités restent [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md), les ADR acceptés, [ACTIVE_SURFACE.json](../ACTIVE_SURFACE.json) et le [registre](../../../config/engine-registry.json). Il ne crée pas une seconde feuille de route : la section 4.10 dit comment il amenderait `DEVELOPMENT_PLAN.md` et le [chemin critique du 12 novembre](STAGE2_AUDIT_DELTA_AND_CRITICAL_PATH_2026-11-12.md), puis s'effacerait.

**Base lue :** `main` = `ff4cad2d01011828518db5dda1221d9afc96a8d3` (12 novembre 2026, 23:39:48 +01:00). Sauf mention contraire, tout chemin cité est lu à ce SHA. **Exécution :** aucune vie, aucun World, aucun runner scientifique. Seuls ont tourné `git`, le coordinateur en lecture seule, le contrôle de navigation et un test de liens. Les extrapolations sont marquées **(hypothèse)**.

## 0. Synthèse pour le propriétaire

**Où en est I3.** I3 existe et tourne. C'est un individu simulé, mortel, qui ne perçoit que ce qui l'entoure, apprend de ses propres actes et paie chacune de ses pensées en énergie et en vigilance. Il reste un prototype de recherche : le moteur enregistré comme actif est toujours I1, et I3 est la référence choisie pour la suite.

**Ce qui est prouvé** (dans le modèle, sur quatre populations seulement) :

- sans ce qu'il apprend des effets de ses propres actes, il ne survit pas : 84 survivants sur 288 avec cet apprentissage, 0 sur 288 sans ;
- sans sa curiosité innée, il ne survit presque jamais : 110 sur 288 avec, 4 sur 288 sans ;
- le paiement de ses pensées, sa mort irréversible et sa perception strictement locale sont couverts par des tests logiciels.

**Ce qui ne l'est pas :**

- **Que la survie façonne l'inné.** C'est la thèse centrale du projet et elle n'a jamais été mesurée. Le seul essai de lignée donne un avantage faible et incertain : 47 survivants contre 42 sur 144, avec des populations qui se contredisent.
- **Qu'il sache décider combien penser** (étape 2). Aucun verdict n'est émis. Choisir combien rejouer ses souvenirs donne des survies contradictoires. Les essais pour qu'une information supplémentaire payée change un acte ont changé des calculs, jamais l'acte.
- **Qu'il s'adapte à des mondes plus complexes.** Aucun monde nouveau n'a encore été construit.
- **Le besoin social.** Rien n'existe, sauf un gène « affiliation » présent dans le génome et sans aucun effet.

**Ce qui s'est passé le 12 novembre.** La revue interne du matin recommandait d'arrêter. Dans les quinze heures suivantes, 28 commits ont pourtant ajouté 13 études d'ingénierie sur l'étape 2 (57 fichiers, 5 415 lignes). Aucune n'a changé la décision suivante, et la mise en service du moteur n'a pas avancé pendant ce temps. Je conclus à une dérive, sans faute d'autorisation, et je recommande un gel (section 3).

**Les trois prochaines décisions :**

1. **Sortir de l'étape 2.** Geler les ajouts, consolider la décision C01 interne traçable, puis publier `HOLD_NO_VERDICT` si les preuves existantes ne permettent aucune clôture bornée.
2. **Laisser la suite avancer sous ce « pas de verdict ».** Le plan actuel met tout derrière l'étape 2. Je propose de débloquer explicitement ce qui n'en dépend pas.
3. **Lancer la lignée courte** (« étape 6 légère »). C'est le plus petit essai qui teste enfin si la survie façonne l'inné. Il porterait sur la curiosité (`beta_u`). Le gène ω y servirait de témoin neutre, et κ ne peut pas y être testé.

Les chiffres et leurs sources sont en section 2. Les options, les coûts et les conséquences de chaque décision sont en section 6.

## 1. État vérifié

### 1.1 Autorités lues

| Question | Constat | Source |
| --- | --- | --- |
| Moteur actif et référence | `active_generation=I1`, `reference_generation=I3` | [engine-registry.json](../../../config/engine-registry.json) |
| Contrat I3 | `status=proposal`, `entrypoints={}`, `activation=NOT_REGISTERED_NOT_EXECUTABLE`, `scientific.gate=not_established` | [engine.json](../engine.json) |
| Référence interne et étape | P1.3 funded-v2 ; étape 2.1 ; logiciel `REPLAY_GATE_CAPACITY_SHOWN` ; `fresh_lived_worlds_allowed=false`, `scientific_gate_authorized=false`, `next_scientific_cohort_authorized=false` ; `updated=2026-11-11` | [ACTIVE_SURFACE.json](../ACTIVE_SURFACE.json) |
| Étape 1 | `CLOSED_NEGATIVE`, P1.3 conservé, `beta_u` reconnu comme disposition innée (option B) | [ADR-0018](../../../docs/decisions/ADR-0018-i3-cloture-etape-1.md) §5 |
| Étape 2 | verdict scientifique `NOT_ISSUED` ; audit interne C01 `HOLD_NO_VERDICT_FOR_GENERAL_STAGE2` ; aucune attestation indépendante revendiquée | [revue C01 interne](STAGE2_C01_INTERNAL_FUTILITY_REVIEW_2026-11-12.md) §4, commit `8c7b9a4` |
| Délégation aux agents | ingénierie de routine, tests sans World, réduction d'archives, documentation ; aucune extension des permissions de World | [ADR-0020](../../../docs/decisions/ADR-0020-i3-owner-selected-development-reference.md) §4-§5 |
| Ouverture de mondes | deux phases G/R, répétition scellée sur le SHA exact, levée consignée par le propriétaire dans `STATUS.md` | [ADR-0017](../../../docs/decisions/ADR-0017-i3-moratoire-deux-phases-repetition-scellee.md) §1-§3 |

### 1.2 État vivant de GitHub

Relevé le 12 novembre 2026 entre 22:42 et 22:50 UTC. L'API principale était hors quota (IP partagée, pas de `gh`). Les relevés viennent de l'API de recherche, des pages publiques et de `git fetch`.

| Élément | Constat |
| --- | --- |
| HEAD de `main` | `ff4cad2`. Le cadrage de la mission citait `c8b07a8`. Quatre commits ont suivi : `25d17b9`, `de89d13` (PR #1355 fusionnée à 22:38 UTC), `ac5356a` (PR #1357, 22:39 UTC) et `ff4cad2`. |
| Issues et PR ouvertes | 18 : 17 issues et la PR #1309. |
| Issues à vérifier | #1062, #1226, #1276, #1283, #1331, #1339, #1026, #1054 et #1060 sont toutes **ouvertes**. #1062, #1276 et #1283 ont été modifiées le 12/11 à 20:16 UTC. |
| PR #1309 | **ouverte, draft, non fusionnée**. Tête `a8682ec`, un seul fichier de conception de 94 lignes, aucune implémentation. |
| PR #1355 | **fusionnée** (`de89d13`). Elle ajoute à `main` un quatrième chemin critique, [l'audit après le partage des coûts](STAGE2_POST_COST_SPLIT_AUDIT_AND_CRITICAL_PATH_2026-11-12.md), numéroté N0 à N7. |
| Autres issues ouvertes utiles | #1239 (taille d'échantillon B1), #1258 et #1269 (contenu du rejeu), #1111 (biais de comptabilité de l'auto-projection de P1.3), #1061 (étape 1). |
| CI sur le SHA exact | **Aucun contrôle attaché.** Les données de la page des commits donnent `statusCheckStatus=null` pour la trentaine de commits les plus récents de `main`, HEAD compris. La CI logicielle I3 ne tourne que sur `pull_request` et sur des chemins de code ([workflow](../../../.github/workflows/i3-proposal-checks.yml)). |
| Arbre testé et arbre fusionné | La tête testée de la PR #1357 a l'arbre `31d657a`. Le commit fusionné `ac5356a` a l'arbre `8311a6f`. L'écart est le document de la PR #1355 (131 lignes, documentation seule). L'arbre exact de `main` n'a donc pas été testé tel quel. |

### 1.3 Coordinateur : écart consigné

`python tools/research_coordinator.py recommend`, lancé à `ff4cad2`, affiche « Active generation: I1 », ne liste que les questions I1-L3 et I2-H1/H2/H3, et suggère « Implement isolated I2 integrated WorldBody and first-person learning prototype » (issue #664). Le fichier [research-program.json](../../../config/research-program.json) ne contient aucune occurrence de « I3 », et [sa documentation](../../../docs/engineering/RESEARCH_COORDINATOR.md) annonce une couverture limitée à I1 et I2.

**Je ne suis pas cette recommandation.** L'ADR-0020 fait d'I3 la référence de développement, et l'ADR-0001 interdit de dépendre d'I2, qui ne sert ici que de source de leçons. Le chantier RP-F1 propose de combler cet écart.

### 1.4 Divergences entre documentation, code et état vivant

1. **La surface d'entrée ne mène pas aux décisions du 12 novembre.** Les noms `AUDIT_DELTA`, `C01_INTERNAL` et `POST_COST_SPLIT` n'apparaissent ni dans [README.md](README.md), ni dans [STATUS.md](STATUS.md), ni dans [ACTIVE_SURFACE.md](ACTIVE_SURFACE.md), ni dans [AGENTS.md d'I3](../AGENTS.md), ni dans [AGENTS.md racine](../../../AGENTS.md). Un agent qui suit l'ordre de lecture prescrit ne rencontre donc pas la recommandation « 0 implémentation candidate supplémentaire ».
2. **Le manifeste n'a pas suivi le code.** `ACTIVE_SURFACE.json` date du 11 novembre. Sur 71 modules `src/i3/lab/stage2_*.py` (17 810 lignes), 6 y sont classés. Les 13 modules ajoutés depuis la revue C01 n'y figurent pas.
3. **`STATUS.md` fait 2 195 lignes.** Le contrôle de navigation impose une surface courte (100 lignes au plus) à I1 et à I2, pas à I3 ([check_repo_navigation.py](../../../tools/check_repo_navigation.py), lignes 171 à 177).
4. **Quatre numérotations du même chemin critique coexistent** : C00-C05 ([audit du 11/11](STAGE2_COMPLETION_AUDIT_AND_ROADMAP_2026-11-11.md)), R00-R07 ([addendum](STAGE2_POST_E3_AUDIT_ADDENDUM_2026-11-11.md)), C00-C07 (12/11) et N0-N7 (après le partage des coûts).
5. **L'issue #1061 (étape 1) est encore ouverte**, alors que l'ADR-0018 a clos l'étape 1.
6. **Trois gènes du génome v4 ne sont pas lus par la référence.** `omega`, `temperament.affiliation` et `temperament.reward_sensitivity` sont tirés et mutés ([genome.py](../modules/genome.py)), mais `Mind.__init__` ne les lit pas ([mind.py](../modules/mind.py), lignes 109 à 122), et la politique `reference` instancie `Mind` ([life.py](../runtime/life.py), ligne 283). La [spécification](SPECIFICATION.md) confirme qu'`affiliation` et `reward_sensitivity` n'ont pas d'effet.
7. **κ n'est pas un gène du génome actuel.** Le [protocole Candidate-J](STAGE1_CANDIDATE_J.md) l'annonçait pour un « genome v5 ». Le schéma en vigueur est `i3-genome-v4`. Le `kappa0` de `mind.py` (ligne 118) est une constante dérivée du tempérament, sans rapport avec ce gène.
8. **La référence porte un défaut connu et ouvert.** L'issue #1111 décrit un biais de comptabilité de l'auto-projection de P1.3. Toute porte future se compare à cette référence.
9. **Le coordinateur ne couvre aucune question I3** (section 1.3).

## 2. Inventaire des preuves

### 2.1 Tableau

Classement : **ÉTABLI**, **RÉFUTÉ SUR CANDIDAT FIGÉ**, **NON OBSERVÉ**, **NON ÉMIS**. Les quatre verdicts du dépôt sont notés T (technique), E (expérimental), S (scientifique) et Tr (transition). Aucun résultat négatif ou nul n'est réinterprété : les chiffres sont ceux des rapports d'origine.

| # | Objet | Classement | T / E / S / Tr | Source |
| --- | --- | --- | --- | --- |
| 1 | Substrat : corps à cinq canaux, pensée payée en énergie et en vigilance, mort irréversible, perception locale, rejeu exact, invariance au renommage | **ÉTABLI** (technique) | T : tests logiciels présents. E : sans objet. S : aucun, ce sont des tarifs simulés et non des joules. Tr : substrat v2 en vigueur. | [SPECIFICATION.md](SPECIFICATION.md), [TEST_PLAN.md](TEST_PLAN.md) |
| 2 | P1.3 funded-v2 comme référence | **ÉTABLI** (porte préenregistrée) | T : présent. E : porte G2e sous ADR-0015. S : décision `ADOPT_P1_3`, sans GO général. Tr : référence retenue. | [G2e](studies/g2e-p13-v2/RESULTS.md) |
| 3 | P1.2 | **RÉFUTÉ SUR CANDIDAT FIGÉ** | E : rejeté à la porte G2c. Tr : variante historique seulement. | [SPECIFICATION.md](SPECIFICATION.md), [ADR-0015](../../../docs/decisions/ADR-0015-i3-portes-sous-selection.md) |
| 4 | Dépendance aux effets appris de ses propres actes | **ÉTABLI**, borné | E : préenregistré, quatre populations, coûts réalisés différents entre bras. S : borné au modèle et à F0, sans GO. Chiffres : P4b 84/288 contre 0/288 ; P5a 112/288 contre 0/288 ; P5b 98/288 contre 0/288. | [P4b](studies/p4b-paid-outcome-learning/RESULTS.md), [P5a](studies/p5a-paid-component-screen/RESULTS.md), [P5b](studies/p5b-paid-readout-heldout/RESULTS.md) |
| 5 | Dépendance à la curiosité innée (`beta_u`) | **ÉTABLI**, borné | E : préenregistré, quatre populations. S : exploratoire, n = 4. Chiffres : 110/288 normal, 4/288 sans curiosité, 105/288 sans prudence, 7/288 sans les deux. Tr : disposition innée reconnue (ADR-0018 §5). | [P5c](studies/p5c-paid-score-addends/RESULTS.md) |
| 6 | Valeur de conservation du rejeu TD et des valeurs apprises | **NON OBSERVÉ** | E : P5a donne 119/288 sans le résultat du rejeu et 117/288 sans les valeurs, contre 112/288 en normal. S : aucun avantage montré. | [P5a](studies/p5a-paid-component-screen/RESULTS.md) |
| 7 | Avantage de lignée par sélection sur la persistance | **NON OBSERVÉ** | E : préenregistré, quatre populations, deux générations de sélection. P3 : G1 37 contre 50, G2 50 contre 45, sur 144. P4a : 47 contre 42 sur 144, soit [-2, +9, -1, -1] par population, intervalle à 95 % de [-7,01 ; +9,51] survivants par population. S : `NO SCIENTIFIC GO`. | [P3](studies/p3-mutation-pilot/RESULTS.md), [P4a](studies/p4a-g2-heldout/RESULTS.md) |
| 8 | Déplacement des gènes par la sélection (thèse centrale de l'ADR-0014) | **NON OBSERVÉ** | Jamais mesuré. P3 utilisait le génome v3, sans ω. Les rapports P3 et P4a ne contiennent aucune trajectoire de gène (recherche lexicale). | [ADR-0018](../../../docs/decisions/ADR-0018-i3-cloture-etape-1.md), conséquences ; [génomes G2 de P3](studies/p3-mutation-pilot/G2_GENOMES.json) |
| 9 | Étape 1 : remplacer curiosité, pertinence et prudence par une valeur d'information exprimée en détresse prédite | **RÉFUTÉ SUR CANDIDATS FIGÉS** | Candidate-F : `FAIL_FROZEN_STAGE1_OMEGA_GATE`. Candidate-J : `CANDIDATE_J_DEFECT` (J0), capacité non observée. G, H et I : voir ADR-0018, contexte. Tr : étape close négative. | [porte ω](STAGE1_OMEGA_ADR0015_GATE.md), [Candidate-J](studies/stage1-candidate-j-software-falsifier/RESULTS.md) |
| 10 | Étape 2.1 : capacité logicielle de la porte de rejeu | **ÉTABLI** (technique) | T : `REPLAY_GATE_CAPACITY_SHOWN`, R0-R4 PASS, R3 non discriminant. E : aucune vie. S : aucun. | [résultat logiciel](studies/stage2-replay-gate-software/RESULTS.md) |
| 11 | Étape 2.1 : vies de développement | **NON ÉMIS** | E : exploratoire, interventions distinctes, à ne pas agréger. 80/81 : GATE 3/12 contre FIXED 4/12. B1 : 38/96 contre 30/96. Trois bras : 27/64 contre 27/64. Contenu : 17/48 contre 23/48. Décision suivante : 12/24 contre 13/24. S : non-infériorité non établie. | [chemin critique du 12/11](STAGE2_AUDIT_DELTA_AND_CRITICAL_PATH_2026-11-12.md) §E0 et rapports cités |
| 12 | E1 : profondeur de simulation sur grille figée | **RÉFUTÉ SUR CANDIDAT FIGÉ** | 0 changement de moteur natif sur 12 contextes synthétiques. Ne réfute pas la profondeur en général. | [E1](studies/stage2-replay-gate-selected-design/NATIVE_OPTION_SET_DEPTH_DECISION_RESULTS_2026-11-11.md) |
| 13 | E3 : lecture payée de branches personnelles | **RÉFUTÉ SUR CANDIDAT FIGÉ** | 1 score modifié sur 2, 0 moteur modifié sur 2. `CLOSED_NEGATIVE` pour ce candidat seulement. | [E3](studies/stage2-replay-gate-selected-design/E3_NATIVE_PAID_BRANCH_DELIVERY_RESULTS_2026-11-11.md) |
| 14 | Lecture payée de l'incertitude résiduelle (PR #1353) | **RÉFUTÉ SUR CANDIDAT FIGÉ** (arrêt d'ingénierie) | `PAID_RESIDUAL_READOUT_STOP_NATIVE_COST_CONFOUND`. 0 différence motrice propre sur 4 ; 3 différences de coût sur 4 à moteur inchangé. | [résultat](studies/stage2-replay-gate-selected-design/STAGE2_PAID_RESIDUAL_UNCERTAINTY_NATIVE_DECISION_RESULTS_2026-11-12.md) |
| 15 | Étapes 2.2 et 2.3 : choisir les cycles de Competition et la profondeur | **NON OBSERVÉ** | T : absentes de la référence. | [chemin critique du 12/11](STAGE2_AUDIT_DELTA_AND_CRITICAL_PATH_2026-11-12.md) §B |
| 16 | Chaîne complète : information payée, décision native, moteur, corps | **NON OBSERVÉ** | Aucun contraste factuel dans un individu né puis exposé. | idem §B |
| 17 | Non-infériorité de survie et écologie indépendante | **NON OBSERVÉ** | Le test de signes 7/8 peut coexister avec une perte moyenne de 15,42 points. La borne B1 de -4,33 points repose sur des hypothèses non approuvées. | [audit d'inférence](studies/stage2-replay-gate-selected-design/INFERENCE_POWER_AUDIT.md) |
| 18 | Verdict scientifique de l'étape 2 | **NON ÉMIS** | `NOT_ISSUED`. Tri interne : `HOLD_NO_VERDICT_FOR_GENERAL_STAGE2`. La révision RP-A1 ne réclame pas de revue externe. | [revue C01 interne](STAGE2_C01_INTERNAL_FUTILITY_REVIEW_2026-11-12.md) |
| 19 | Individualité acquise (#1026) et question P5d (#1054) | **NON OBSERVÉ** | `NOT_OBSERVED` pour P5d. | [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md), étape 0 |
| 20 | Généralisation hors F0 (familles F1 à F5) | **NON OBSERVÉ** | Contrats prospectifs, générateurs non implémentés. | [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md), familles de mondes |
| 21 | Autres individus (F6) et besoin social | **NON OBSERVÉ** | Hors périmètre. `World` ne porte qu'un corps. | [ADR-0016](../../../docs/decisions/ADR-0016-i3-generalization-without-imposed-rules.md) §6, [world.py](../modules/world.py) |
| 22 | Release du moteur natif | **NON ÉMIS** | T : R0 fait, R1 partiel, R2 à R4 non démontrés, R5 non autorisé. Jamais une preuve scientifique. | [ADR-0020](../../../docs/decisions/ADR-0020-i3-owner-selected-development-reference.md), [README.md](README.md) |

### 2.2 Statut des gènes ω, κ et `beta_u`

| Gène | Dans le génome v4 | Exprimé par la référence P1.3 | Ce qui est montré | Statut |
| --- | --- | --- | --- | --- |
| ω (`omega`) | Oui, bornes [-1 ; 1], tiré de façon symétrique et muté | **Non.** Lu seulement par des candidats d'étape 1 archivés. | Candidate-F a échoué à sa porte. Candidate-J s'est arrêté sur un défaut avant toute mesure de capacité. | Porté mais silencieux. C'est de fait un marqueur neutre. Son déplacement par la sélection n'a jamais été observé. |
| κ | **Non.** Annoncé pour un « genome v5 » jamais adopté. | Non | Rien : J1 à J4 n'ont pas été évalués. | Non testable sur la référence. L'exprimer demanderait un nouveau candidat, ce que l'ADR-0018 §5 exclut. |
| `beta_u` | Oui, bornes [0 ; 2] | **Oui** : `curiosity = beta_u * u * relevance`, modulé par `temperament.exploration` ([mind.py](../modules/mind.py), lignes 116 et 1071). | Sans ce terme, la survie passe de 110/288 à 4/288 (P5c). | Disposition innée reconnue (option B). Forme donnée par le concepteur, poids héritable. Son déplacement par la sélection n'a jamais été observé. |
| `temperament.affiliation` | Oui, bornes [-1 ; 1] | Non | Rien | Sans effet. Emplacement existant, à ne pas interpréter. |

## 3. Diagnostic de dérive

### 3.1 Faits mesurés

| Mesure | Valeur | Source |
| --- | --- | --- |
| Plage | de `8c7b9a4` (12/11, 08:24 +01:00) à `ff4cad2` (12/11, 23:39 +01:00) | `git log` |
| Commits | 28, dont 24 jusqu'à `c8b07a8` | `git log --oneline 8c7b9a4..ff4cad2` |
| Fichiers | 57 ajoutés, aucun modifié ni supprimé ; +5 415 lignes (51 fichiers et +4 960 lignes à `c8b07a8`) | `git diff --numstat` |
| Répartition | 13 modules `src/i3/lab/stage2_*.py` (2 882 lignes), 13 fichiers `tests/i3/` (1 529 lignes), 30 documents ou JSON d'étude (873 lignes), 1 audit (131 lignes) | idem |
| Études | 13, toutes `NOT_ISSUED` au plan scientifique | tableau 3.2 |
| Code du moteur | aucun fichier de `modules/` ou de `runtime/`, ni registre, ni manifeste | `git diff --name-only` |
| Release (#1331, #1339) | aucun commit dans la plage | idem |
| Mondes et vies scientifiques | 0. Des vies techniques ont tourné sur deux mondes DEV déjà exposés (`dev-open-field`, `dev-failing-well`, graines 840061 et 840062). | rapports du tableau 3.2 |

### 3.2 Les 13 études

Chaque rapport est le fichier `STAGE2_<NOM>_RESULTS_2026-11-12.md` du dossier [stage2-replay-gate-selected-design](studies/stage2-replay-gate-selected-design/).

| PR | `<NOM>` | Nature | Verdict d'ingénierie | Science |
| --- | --- | --- | --- | --- |
| #1343, #1344 | `HOST_OPERATION_STAGE_PROFILE` | profilage hôte | `STAGE_PROFILE_PARITY_PASS` | `NOT_ISSUED` |
| #1345 | `ACTUAL_LEARNING_SETTLEMENT` | règlement des coûts, quatre corps fixés | `ACTUAL_WORLD_LEARNING_SETTLEMENT_PASS` | `NOT_ISSUED` |
| #1346 | `NATIVE_CHOICE_COST_BRIDGE` | choix natif et coût optionnel | `NATIVE_CHOICE_COST_BRIDGE_PASS`, `NO_ACTION_MEDIATION_OBSERVED` | `NOT_ISSUED` |
| #1347 | `PREQUENTIAL_NATIVE_EFFECT_RELIABILITY` | observateur passif, 4 trajectoires, 320 événements | `PREQUENTIAL_FIRST_PERSON_EFFECT_CUSTODY_PASS` | `NOT_ISSUED` |
| #1348 | `POSTHOC_ZERO_BASELINE` | analyse post-hoc des 320 événements | `POSTHOC_PAIRED_SCORE_INTEGRITY_PASS` | `NOT_ISSUED` |
| #1349 | `RETROSPECTIVE_RESIDUAL_RISK` | criblage rétrospectif des mêmes événements | `RETROSPECTIVE_RISK_EVALUATION_PASS` | `NOT_ISSUED` |
| #1350 | `ARCHIVED_RESIDUAL_READOUT_PAID` | lecture payée sur registre archivé | `ARCHIVED_RESIDUAL_MODEL_PAID_READOUT_PASS` | `NOT_ISSUED` |
| #1351 | `RESIDUAL_LEDGER_STORAGE_AFFORDABILITY` | admission hypothétique de stockage | `RESIDUAL_LEDGER_STORAGE_MODEL_AFFORDABILITY_PASS` | `NOT_ISSUED` |
| #1352 | `REAL_PAID_ERROR_LEDGER_ENGINEERING` | registre payé dans le World, non lu par le Mind | `ACTUAL_PAID_LEDGER_ENGINEERING_PASS` | `NOT_ISSUED` |
| #1353 | `PAID_RESIDUAL_UNCERTAINTY_NATIVE_DECISION` | **nouvelle sous-classe de Mind en laboratoire** | `PAID_RESIDUAL_READOUT_STOP_NATIVE_COST_CONFOUND` | `NOT_ISSUED` |
| #1354 | `FIRST_NATIVE_COST_SPLIT_DECOMPOSITION` | réconciliation post-hoc de #1353 | `FIRST_NATIVE_COST_SPLIT_ACCOUNTING_PASS` | `NOT_ISSUED` |
| #1356 | `FIRST_SPLIT_ESTIMAND_GUARD` | garde de méthode post-hoc sur les quatre paires de #1353 | METHODS GUARD PASS | `NOT_ISSUED` |
| #1357 | `PREQUENTIAL_SOURCE_IDENTIFIABILITY` | témoin synthétique sans World | `SOFTWARE_SOURCE_SEPARABILITY_WITNESS_PASS` | `NOT_ISSUED` |

### 3.3 Évaluation au sens d'AGENTS.md

[AGENTS.md](../../../AGENTS.md) demande de signaler **DRIFT DETECTED** quand le travail empile de la complexité, des preuves locales répétées ou de la CI sans augmenter l'information scientifique de bout en bout. Les quatre critères sont remplis.

- **Complexité.** +5 415 lignes en une journée, 13 modules de laboratoire de plus (71 au total), un manifeste qui ne les classe pas.
- **Preuves locales répétées.** Douze verdicts sur treize sont des PASS d'invariants d'ingénierie. Les mêmes 320 événements, issus de deux mondes DEV et de deux graines, sont relus par #1348, #1349, #1350 et #1351. Les quatre paires de #1353 sont relues par #1354 puis par #1356.
- **CI.** Chaque PR relance la suite I3 sur Python 3.11 et 3.12. Le dernier rapport cite 1 284 tests par interpréteur.
- **Information de bout en bout.** Aucune ligne de la chaîne « information payée, décision native, moteur, corps » n'a quitté le classement NON OBSERVÉ (lignes 14 à 16 du tableau 2.1). Surtout, la décision suivante est la même avant et après. Le matin, la revue interne demandait une source réellement distincte ou un arbitrage de méthode, et aucun candidat supplémentaire. Le soir, l'audit fusionné (`de89d13`, section F) demande N0, N1 puis N7, sans aucune vie nouvelle.

Deux éléments aggravent le constat.

- **La source candidate a été choisie sur des données déjà vues.** La revue interne exigeait qu'une source nouvelle soit dérivée avant tout essai. Or les « erreurs de prévision personnelles passées » ont été retenues après un criblage rétrospectif de trajectoires DEV déjà inspectées (#1349), puis implémentées dans une sous-classe de Mind (#1353). L'audit du soir le dit lui-même : relire ces quatre trajectoires fait courir le risque de sélectionner des hypothèses favorables après exposition (`de89d13`, section C5).
- **Le seuil que l'audit du soir se fixe a été franchi dans la minute.** Sa section C5 demande de déclarer la dérive si une nouvelle étude d'aval sans World est proposée sans discrimination nouvelle gelée ni réponse méthodologique indépendante. La PR #1357, fusionnée une minute plus tard, est un témoin synthétique sans World, que son propre rapport décrit comme une capacité mathématique très étroite. Je considère le seuil atteint. La clause de « discrimination nouvelle gelée » reste discutable, car deux séquences artificielles ont bien été gelées avant le code, mais après connaissance des résultats DEV.

### 3.4 Délégation de l'ADR-0020

Chaque acte pris isolément est couvert par l'ADR-0020 §4 : tests logiciels sans World, réduction d'archives, documentation, intégration de PR. Aucun GO n'a été revendiqué, aucun monde scientifique n'a été ouvert, et la discipline de preuve a été tenue : préflights gelés avant le code, résultats négatifs et premières CI en échec conservés. **Il n'y a donc pas de faute d'autorisation.**

La délégation ne répond pourtant pas au critère de dérive, pour trois raisons.

1. Le critère d'AGENTS.md porte sur l'information produite, pas sur la permission.
2. L'ADR-0020 donne lui-même la priorité à l'intégrité du cycle de vie natif (R1 et R2) avant de nouvelles têtes de modèle spéculatives. La journée a fait l'inverse : 13 études d'étape 2 et aucun commit sur la release.
3. La recommandation interne d'arrêt n'était pas sur le chemin de lecture des agents (divergence 1 de la section 1.4). C'est une cause probable **(hypothèse)** : la délégation est visible dans AGENTS.md, l'arrêt ne l'est pas.

### 3.5 Ce que la campagne a réellement appris

Trois enseignements d'instrumentation méritent d'être gardés. Ils ne servent que si une étude vivante de type C03 a lieu un jour.

1. **Un tarif de lecture égal ne donne pas un coût total égal.** Une information visible change le nombre de cycles de Competition natifs : 3 paires sur 4 dans #1353, réconciliées par #1354. Ce coût d'aval est un médiateur à mesurer, pas à neutraliser.
2. **Un même `CognitiveWork` nominal recouvre des charges hôte différentes** (#1343, #1344). Cela concerne l'issue #1283.
3. **Le chemin technique « prévision payée dans le World et registre d'erreurs personnelles » existe en laboratoire** (#1352), sans être lu par le Mind.

### 3.6 Conclusion et recommandation

**DRIFT DETECTED**, au sens d'AGENTS.md. Il s'agit d'une dérive d'information et non d'une violation d'autorisation. Je recommande cinq mesures.

1. **Geler immédiatement l'étape 2.** Aucun nouveau module `src/i3/lab/stage2_*`, aucune nouvelle étude, garde ou analyse post-hoc, jusqu'à la décision interne C01 versionnée et au cadrage RP-A2, sans attendre de relecteur externe.
2. **Inscrire ce gel là où les agents lisent** : `next_scientific_action` du manifeste, AGENTS.md d'I3 et section « Current » du README. Cette action touche des fichiers que cette mission n'a pas le droit de modifier. Elle revient au propriétaire ou à un agent mandaté (RP-F2).
3. **Poser une règle d'entrée simple.** Avant toute étude, nommer la décision que son résultat peut changer. S'il n'y en a pas, ne pas l'écrire (RP-F3).
4. **Rediriger l'ingénierie déléguée** vers la priorité de l'ADR-0020 (R1 et R2, issues #1331 et #1339) et vers le protocole de la lignée courte (RP-B1).
5. **Ne pas produire de cinquième audit de l'étape 2.** L'audit du soir suffit comme index. Ce document ne le refait pas.

## 4. Axes et chantiers

### 4.1 Une seule structure

Les plans existants sont fusionnés en sept voies. Les identifiants existants ne changent pas. Les identifiants `RP-` sont provisoires : ils servent à l'arbitrage et disparaissent ensuite (section 4.10).

| Voie | Étapes et familles du plan | Chemin critique du 12/11 et équivalents | Portes de release | Issues | Chantiers |
| --- | --- | --- | --- | --- | --- |
| A. Issue de l'étape 2 | étape 2 (2.1 ; 2.2 et 2.3 absentes), F0 | C00 fait ; C01 = N1 = R01 ; C02 = N2 = R02 ; C03 à C06 = N3 à N6 = R03 à R06 ; C07 = N7 = R07 | aucune | #1062, #1226, #1239, #1258, #1269, #1276, #1283, PR #1309 | RP-A1 à RP-A4 |
| B. Inné façonné par la survie | étape 0 (au moins 8 populations), étape 6 légère puis complète | hors chemin critique de l'étape 2 | aucune | #1060, #1026 | RP-B0 à RP-B3 |
| C. Mondes plus complexes | étapes 3, 4 et 5 ; familles F1 à F5 ; audit transversal de Competition | hors chemin critique de l'étape 2 | aucune | #1054, #1111 | RP-C1 à RP-C3 |
| D. Release du moteur natif | aucune | axe parallèle (C5 du 12/11) | R0 fait ; R1 à R5 | #1331, #1339 | RP-D1, RP-D2 |
| E. Besoin social | F6, hors périmètre | aucun | aucune | aucune | RP-E1, RP-E2 |
| F. Outillage et gouvernance | aucune | aucun | aucune | aucune | RP-F1 à RP-F3 |
| G. Horizon | aucune | aucun | R5 dépend d'une politique de partage | aucune | questions seulement |

**Horizons.** H0 : immédiat, sans aucune vie. H1 : premier palier avec des vies, sous autorisation indexée. H2 : après les verdicts de H1. H3 : horizon, sans calendrier.

**Révisions d'axes, avec leur justification.** L'étape 0 est rattachée à l'axe B, parce que la lignée courte est le premier usage du plan à huit populations. Le gel de l'étape 2 est traité comme une décision (DÉC-1) et non comme un chantier. I2 n'apparaît nulle part comme dépendance (ADR-0001).

### 4.2 Écarts avec l'intention du propriétaire

| Ce que l'intention exige | Ce qui existe | Ce qu'aucun plan ne couvre | Réponse proposée |
| --- | --- | --- | --- |
| L'inné façonné par la survie | Outillage de lignée de P3 (4 populations). Plan à 8 populations sans sélection des parents ni mutation ([STAGE0_DESIGN.md](STAGE0_DESIGN.md)). | Aucune mesure du déplacement d'un gène. ω silencieux, κ absent. L'étape 6 est en fin de plan. | RP-B0 à RP-B3, DÉC-3 |
| Des portes jugées sur les meilleurs génomes sélectionnés | ADR-0015, appliqué à G2e | Aucun génome sélectionné issu d'au moins 8 populations indépendantes n'est disponible pour les portes futures. | RP-B2 |
| Des mondes plus complexes, sans règles imposées | Familles F1 à F5 décrites en une ligne chacune | Aucun générateur, aucun contrat sensoriel figé, aucune mesure de la référence hors F0. Les étapes 3 à 5 attendent l'étape 2. | RP-C1 à RP-C3, DÉC-2 |
| Le besoin social | Un schéma d'une phrase (ADR-0018). Un gène `affiliation` sans effet. | Tout : la forme dans D, l'évolution au cours de la vie, un monde à plusieurs corps, l'ADR. | RP-E1, RP-E2, DÉC-4 |
| Un individu qui agit selon ses enjeux, y compris quand il se trompe | Invariants testés, résultats négatifs conservés | « Combien penser » reste sans verdict et sans décision de fin. | RP-A1, RP-A2, DÉC-1 |
| Partager sans produire d'individus « corrompus et incontrôlables » | Dépôt déjà public : code sous [Apache-2.0](../../../LICENSE), documentation sous [CC BY 4.0](../../../LICENSE-DOCUMENTATION). Génomes sélectionnés de P3 déjà publiés. | Aucune politique de partage, aucune définition d'un individu conforme, aucun suivi. Identité et anti-retour arrière non démontrés. | RP-D1, questions G3, DÉC-5 |
| Un pilotage qui tienne ses propres arrêts | Coordinateur, manifeste, AGENTS.md | Le coordinateur ignore I3. L'arrêt du 12/11 est hors du chemin de lecture. | RP-F1, RP-F2 |

### 4.3 Axe A — issue scientifique de l'étape 2

#### RP-A1 · H0 · Arbitrage méthodologique interne borné et reproductible (S2-C01)

- **Question falsifiable.** Les preuves existantes répondent-elles à une hypothèse de l'étape 2 réellement préannoncée ? Trois issues sont admises : `CLOSE_BOUNDED`, `DISTINCT_SOURCE_REQUIRED` ou `HOLD_NO_VERDICT`.
- **Lien avec l'intention.** L'individu décide seul combien penser. Aucun succès ni échec général de cette capacité n'est déclaré sur la seule base d'un test logiciel ou d'un contraste exploratoire.
- **Falsificateur et règle d'arrêt.** Un verdict de clôture est irrecevable si l'hypothèse d'origine, l'estimand, les unités indépendantes, les contrastes, la puissance et la portée ne correspondent pas aux preuves antérieures à l'exposition. Aucun seuil, aucune population et aucune marge ne peuvent être choisis après observation. En cas d'inférence insuffisante, le résultat est `HOLD_NO_VERDICT` ; aucune attente de relecteur ou de date butoir ne bloque RP-A2.
- **Contrôle ou ablation.** L'audit interne applique à l'identique ses critères aux deux arguments déjà rejetés : « E3 à 0/2, donc négatif général » et « B1 à +8/96, donc succès ». Ils doivent rester rejetés tant qu'aucune preuve de portée et d'indépendance correspondante n'existe.
- **Observable.** Une matrice de décision traçable, datée et versionnée par commit : hypothèse d'origine, estimand, unité statistique, source exacte, traitement, contrôle, puissance et limites, contres-arguments, décision motivée. Ce document est expressément qualifié d'**audit interne**, jamais de validation indépendante.
- **Règle de décision.** `CLOSE_BOUNDED` uniquement si une hypothèse préannoncée est réellement évaluée dans un périmètre suffisamment identifié et avec une inférence défendable ; `DISTINCT_SOURCE_REQUIRED` si une question précise ne peut être traitée qu'avec une source personnelle vraiment nouvelle, définie avant essais ; `HOLD_NO_VERDICT` lorsque les données existantes ne départagent pas honnêtement succès, échec ou continuation. Une clôture d'un candidat E1/E3 ne constitue pas une clôture générale de l'étape 2.
- **Plus petit test exécutable.** Reprendre en lecture seule le dossier C01 interne déjà versionné ([STAGE2_C01_INTERNAL_FUTILITY_REVIEW_2026-11-12.md](STAGE2_C01_INTERNAL_FUTILITY_REVIEW_2026-11-12.md)) et produire une synthèse contradictoire de dix pages maximum, en reliant [STAGE2_LAUNCH.md](STAGE2_LAUNCH.md), contrastes et deux arguments rejetés. Aucun code, aucune nouvelle vie.
- **Dépendances.** Sources archivées et issues #1062, #1226 et #1239 comme références méthodologiques, **sans dépendance à DÉC-1, à un relecteur externe ni à un délai d'avis**.
- **Coût.** 0,5 à 1 jour d'agent pour la consolidation documentaire ; **0 jour de relecteur**, 0 World, 0 vie, calcul expérimental nul.
- **Autorisation requise.** Aucune nouvelle autorisation pour cet audit documentaire délégué ; toute éventuelle nouvelle cohorte exige séparément sa propre autorisation de source, de protocole et d'indices. Les autres portes prospectives des issues #1226 et #1239 ne sont pas levées ici.
- **Risque de règle imposée ou d'oracle.** Aucun changement de comportement de l'individu. Risque méthodologique : biais de confirmation interne, sélection rétrospective et fausse indépendance. Parades : pièces immuables, critères explicites, arguments adverses et portée bornée.
- **Critère de sortie.** T et E : sans objet. S : une des trois issues motivée et versionnée. **À preuve inchangée, la revue C01 déjà publiée soutient `HOLD_NO_VERDICT` pour l'étape 2 générale**, tout en conservant les négatifs strictement locaux E1/E3. Tr : passage immédiat à RP-A2, sans relecteur.

#### RP-A2 · H0 · Décision de fin d'étape 2, variante `HOLD_NO_VERDICT` comprise (S2-C07)

- **Question falsifiable.** Peut-on consigner l'état de l'étape 2 sans réécrire sa définition ? Le chantier échoue si une phrase de la décision dépasse ses sources.
- **Lien avec l'intention.** Les résultats nuls ou défavorables restent publiés, et l'individu garde P1.3, erreurs comprises.
- **Falsificateur et règle d'arrêt.** Chaque affirmation est relue contre le tableau 2.1. Une seule décision est écrite, sans version suivante tant qu'aucun fait nouveau n'apparaît.
- **Contrôle ou ablation.** Les quatre verdicts sont rédigés séparément. `HOLD_NO_VERDICT` est écrit comme une suspension, pas comme une clôture.
- **Observable.** Un ADR proposé (numéro suivant : 0021) qui fixe l'issue, la référence P1.3 funded-v2 avec ses budgets hérités fixes `n_base` et `h_max`, la liste des négatifs par candidat, la règle de transition (DÉC-2) et les conditions de réouverture (point 5 de la revue interne).
- **Plus petit test exécutable.** Un brouillon d'ADR d'une page, relu contre les sources.
- **Dépendances.** RP-A1 et la décision de transition DÉC-2 ; aucun avis ni délai externe.
- **Coût.** 0,5 à 1 jour. 0 World, 0 vie.
- **Autorisation requise.** Acceptation de l'ADR par le propriétaire.
- **Risque de règle imposée ou d'oracle.** Aucun côté individu. Risque de méthode : transformer une absence de preuve en clôture.
- **Critère de sortie.** T : inchangé. E : inchangé. S : `NOT_ISSUED` maintenu, ou verdict borné si RP-A1 le permet. Tr : décision versionnée, issue #1062 mise à jour.

#### RP-A3 · H1, conditionnel · Une seule source distincte, test sans World (S2-C02)

Ce chantier n'existe que si RP-A1 rend `DISTINCT_SOURCE_REQUIRED` et nomme la source.

- **Question falsifiable.** Une information personnelle réellement distincte de celle d'E3, réellement payée, change-t-elle un moteur natif admis, à travail égal entre VISIBLE et PAID_DISCARD ?
- **Lien avec l'intention.** Une information ne vaut que si elle passe par la détresse prédite et par un acte que l'individu choisit.
- **Falsificateur et règle d'arrêt.** Un score modifié sans moteur modifié est un échec. Un échec entraîne l'arrêt immédiat et la publication d'un négatif propre au candidat, sans nouvelle grille.
- **Contrôle ou ablation.** Les mêmes opérateurs sont exécutés et payés, puis masqués. S'y ajoutent les cas sans information, à énergie basse, à vigilance basse, non financé et mort.
- **Observable.** Moteur natif admis, coûts payés en énergie et en vigilance, nombre de cycles de Competition (médiateur, section 3.5).
- **Plus petit test exécutable.** Un protocole gelé avant tout code, sur des cas neufs.
- **Dépendances.** RP-A1. La source « erreurs personnelles passées » a déjà été exposée par les PR #1349 à #1357. Elle ne serait admissible que sur des cas neufs gelés, et seulement si un protocole distinct, préalablement gelé et justifié par une source actionnable, empêche toute retouche sur les résultats déjà vus.
- **Coût.** 2 à 4 jours d'agent. 0 World scientifique, 0 vie scientifique.
- **Autorisation requise.** ADR-0020 §4 pour le logiciel. Aucune ouverture de monde.
- **Risque de règle imposée ou d'oracle.** Élevé dans trois cas : si l'on règle les cas jusqu'à obtenir un moteur différent, si le signal vient de l'état caché du World, ou si la lecture est gratuite.
- **Critère de sortie.** T : test épinglé à la source, Python 3.11 et 3.12. E : protocole gelé respecté. S : aucun, c'est une porte d'accès. Tr : passage à RP-A4 ou arrêt.

#### RP-A4 · H2, conditionnel · Chaîne causale vivante (S2-C03 à S2-C06)

Ces chantiers sont repris sans changement du [chemin critique du 12/11](STAGE2_AUDIT_DELTA_AND_CRITICAL_PATH_2026-11-12.md), sections D et E.

- **Question falsifiable.** Le signal visible change-t-il des décisions factuelles et la détresse nette, contre le même travail payé puis écarté ?
- **Lien avec l'intention.** C'est la seule chaîne complète de l'étape 2 : expérience vécue, décision native payée, moteur, corps.
- **Falsificateur et règle d'arrêt.** Un résultat nul, défavorable ou non financé arrête le candidat. Si la puissance de confirmation est hors d'atteinte, l'issue est `HOLD_NO_VERDICT`, sans marge relâchée après coup.
- **Contrôle ou ablation.** PAID_DISCARD, FIXED et RANDOM-EQUAL-MEAN, tenus distincts et jamais agrégés.
- **Observable.** Tous les assignés : moteurs exécutés, énergie et vigilance avant et après, survie, inactivité, morts, censures.
- **Plus petit test exécutable.** La répétition G/R sur cohorte `engineering` (S2-C04).
- **Dépendances.** RP-A3 réussi, nouveau transport, autorisation indexée.
- **Coût.** S2-C05 : 48 à 96 vies, 19 200 à 38 400 pas au plus. S2-C06 : l'[analyse de puissance](studies/stage2-replay-gate-selected-design/CONFIRMATORY_SURVIVAL_POWER_STUDY.md) donne à titre hypothétique 7 198 paires indépendantes, soit 14 396 vies et 5 758 400 pas. Le réalisme de ce chiffre est traité par RP-F3.
- **Autorisation requise.** Protocole gelé, répétition scellée, levée consignée (ADR-0017), indices neufs.
- **Risque de règle imposée ou d'oracle.** Pseudo-réplication, coût d'opportunité omis, bifurcation détachée présentée comme une vie.
- **Critère de sortie.** Les quatre verdicts de la section G du chemin critique du 12/11.

### 4.4 Axe B — lignée et inné façonné par la survie

La référence P1.3 n'est pas modifiée par cet axe : aucun mécanisme n'est ajouté à l'individu. L'outillage de P3 existe déjà ([p3_pilot.py](../lab/p3_pilot.py), [p3_schedule.py](../lab/p3_schedule.py)) : 4 populations, 3 générations, bras `selected` et `random_parent`, 864 vies.

**Erratum du 13 novembre 2026.** RP-B0 est fait, et le dimensionnement avancé ci-dessous pour RP-B1 et RP-B2 est caduc. Ce texte évoquait 8 à 12 populations de 6 génomes sur 4 à 6 générations, soit 2 304 à 5 184 vies, et un « témoin positif » directionnel. Une lecture descriptive de P3 et un modèle nul de dérive, tous deux sans aucune vie, montrent qu'un tel plan n'aurait presque rien pu détecter et que la direction présumée était fausse. Le plan proposé devient : 16 populations de 24 génomes sur 3 générations, critère de signe bilatéral à 13 sur 16, soit 11 520 à 13 824 vies. Les coûts de RP-B1, de RP-B2, de la section 5.1 et de DÉC-3 sont à lire en conséquence. Les sources sont dans le dossier `src/i3/docs/studies/stage6-light-preparation/` de la branche `research/i3-stage6-light-preparation-integrated-20261113` (PR #1391). Cet erratum n'autorise rien : selon l'ADR-0021, aucune cohorte des étapes 3 à 6 n'est libérée.

#### RP-B0 · H0 · Lecture descriptive des génomes de P3 déjà archivés

- **Question falsifiable.** Dans P3, la distribution de `beta_u` du bras sélectionné s'écarte-t-elle de celle du bras à parents aléatoires ? La réponse est descriptive.
- **Lien avec l'intention.** C'est un premier regard, sans aucune vie, sur la thèse « la survie façonne l'inné ».
- **Falsificateur et règle d'arrêt.** Aucun verdict n'est admis : quatre populations et deux générations de sélection ne permettent pas d'inférer. La règle de réduction est gelée avant la lecture, et la lecture est unique.
- **Contrôle ou ablation.** Bras `random_parent`. Gènes sans effet du génome v3 (`temperament.affiliation`, `temperament.reward_sensitivity`) comme marqueurs neutres.
- **Observable.** Moyenne, quantiles et part aux bornes de chaque gène, par population, par bras et par génération.
- **Plus petit test exécutable.** Un script en lecture seule sur les [48 génomes G2](studies/p3-mutation-pilot/G2_GENOMES.json) (6 par bras et par population) et sur les graines de P3.
- **Dépendances.** DÉC-3, pour ne pas lancer une analyse orpheline.
- **Coût.** 0,5 à 1 jour. 0 World, 0 vie.
- **Autorisation requise.** ADR-0020 §4 (réduction d'archives).
- **Risque de règle imposée ou d'oracle.** Aucun côté individu. Le risque est la sur-interprétation : le résultat sert à dimensionner RP-B1, pas à choisir un seuil de décision.
- **Critère de sortie.** T : script reproductible. E : sans objet. S : aucun. Tr : paramètres de RP-B1 justifiés.

#### RP-B1 · H0 · Protocole gelé de l'étape 6 légère, transport et répétition scellée

- **Question falsifiable.** Sous sélection par la seule persistance, `beta_u` se déplace-t-il dans le même sens, par rapport au bras à parents aléatoires, dans des populations indépendantes ?
- **Lien avec l'intention.** C'est la thèse centrale de l'ADR-0014, que l'ADR-0018 dit n'avoir jamais été exercée.
- **Falsificateur et règle d'arrêt.** Deux témoins sont fixés d'avance. Témoin positif : `beta_u` est le gène dont l'effet connu sur la survie est le plus fort (ligne 5 du tableau 2.1). S'il ne bouge pas, la lignée telle qu'elle est outillée ne façonne pas l'inné à cette échelle, et l'étape 6 complète doit être redimensionnée. Témoin neutre : si ω, `affiliation` ou `reward_sensitivity` bougent dans le même sens entre populations, le résultat est invalide. L'exécution est unique, le nombre de générations est fixé d'avance, et aucune reprise n'est admise.
- **Contrôle ou ablation.** Bras `random_parent`, génération 0 appariée entre les bras, marqueurs neutres. Dans une lignée sans recombinaison, un gène neutre peut suivre un génome gagnant à l'intérieur d'une population. Seul compte donc l'accord de signe entre populations.
- **Observable.** Génomes de chaque génération, durée de vie individuelle, survie à l'horizon, coûts payés, part des gènes aux bornes.
- **Plus petit test exécutable.** Une répétition scellée à pleine échelle sur la cohorte `engineering`, en Python 3.11 et 3.12 (ADR-0019). Un test dynamique confirme aussi que les trois marqueurs neutres n'ont aucun effet sur une vie de référence, ce que ce document n'a établi que par lecture du code.
- **Dépendances.** DÉC-2 et DÉC-3. Issue #1060. RP-B0, facultatif.
- **Coût.** 2 à 4 jours d'agent. 0 vie scientifique. L'arithmétique est à figer dans le protocole **(hypothèse de dimensionnement)**. Avec 8 populations, seul 8/8 atteint p = 0,0078, et 7/8 donne p = 0,0703 ([DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md)). Avec 12 populations, 10/12 donne p ≈ 0,039. Douze populations coûtent peu (voir RP-B2).
- **Autorisation requise.** ADR-0020 §4 et §5 pour le protocole et la répétition. Aucune ouverture de monde.
- **Risque de règle imposée ou d'oracle.** Nul côté individu. Côté concepteur, le risque est de choisir des mondes de sélection qui favorisent un gène. La parade : familles F0 existantes et indices neufs tirés par une règle figée.
- **Critère de sortie.** T : G/R complet en `engineering`. E : protocole gelé au SHA exact. S : aucun. Tr : demande de levée indexée adressée au propriétaire.

#### RP-B2 · H1 · Étape 6 légère : exécution unique

- **Question falsifiable.** Celle de RP-B1, sans modification.
- **Lien avec l'intention.** C'est la première mesure de bout en bout de la boucle longue : vies vécues, décisions natives payées, corps, persistance, sélection, inné.
- **Falsificateur et règle d'arrêt.** Ceux du protocole gelé. Un échec de génération donne `ENGINEERING_FAILURE_NOT_A_DEATH`, clôt le panel et interdit toute reprise (ADR-0017).
- **Contrôle ou ablation.** Ceux de RP-B1. S'y ajoute une évaluation des génomes finaux sur des mondes réservés jamais ouverts, comme dans P4a, rapportée sans être le critère principal.
- **Observable.** Ceux de RP-B1, pour tous les assignés, morts et censures comprises.
- **Plus petit test exécutable.** La répétition scellée de RP-B1.
- **Dépendances.** RP-B1, levée, indices.
- **Coût.** **(hypothèse)** 8 à 12 populations, 4 à 6 générations, 6 génomes, 3 familles F0, 2 répétitions et 2 bras donnent 2 304 à 5 184 vies de sélection, plus quelques centaines de vies d'évaluation. Cela fait au plus environ 2,4 millions de pas, soit moins d'une heure-CPU à 0,8-1,3 ms par pas (mesures : [répétition scellée](studies/stage2-replay-gate-development-80-81/HARDENED_REHEARSAL.md), [G2e](studies/g2e-p13-v2/RESULTS.md)). L'analyse demande 0,5 à 1 jour.
- **Autorisation requise.** Protocole gelé, répétition scellée sur le SHA exact, levée consignée par le propriétaire dans `STATUS.md` (ADR-0017), plage d'indices neuve vérifiée contre toutes les allocations antérieures. La réserve `1200000..1200199` reste scellée.
- **Risque de règle imposée ou d'oracle.** Nul côté individu. Le risque est d'inférence : prendre un accord directionnel pour une preuve.
- **Critère de sortie.** T : originaux scellés, réduction unique. E : protocole respecté, tous les assignés comptés. S : un verdict préenregistré parmi « déplacement établi », « non observé » et « invalide ». Tr : décision sur RP-B3, et génomes sélectionnés mis à disposition des portes de l'axe C (ADR-0015).

#### RP-B3 · H2 · Étape 6 complète

- **Question falsifiable.** Les dispositions d'apprentissage génériques sélectionnées par la persistance donnent-elles un avantage sur des familles de mondes réservées, contre des parents aléatoires ?
- **Lien avec l'intention.** L'inné façonné par la survie, jugé sur ses meilleurs génomes, sans aucune expérience héritée.
- **Falsificateur et règle d'arrêt.** Le plan retient au moins 7 populations sur 8 avec un avantage du bras sélectionné. Ce critère est directionnel. Il doit être complété par une règle d'incertitude avant l'exécution.
- **Contrôle ou ablation.** Parents aléatoires. Contrôle « apprentissage désactivé » à coût réel explicite. Reprise de P4a sur des conditions neuves.
- **Observable.** Survie à l'horizon, coûts payés, trajectoires de gènes.
- **Plus petit test exécutable.** RP-B2.
- **Dépendances.** RP-B2, au moins une famille nouvelle (RP-C1), recombinaison à implémenter.
- **Coût.** **(hypothèse)** L'ordre de grandeur est celui de l'ADR-0014 : 8 × 64 × 200 vies de 1 000 pas, soit environ 10^8 pas, donc 22 à 36 heures-CPU à 0,8-1,3 ms par pas.
- **Autorisation requise.** Nouveau protocole, nouvelle levée, indices neufs pour chaque famille.
- **Risque de règle imposée ou d'oracle.** Transmettre par mégarde un état appris (poids, carte, mémoire), ce que l'ADR-0014 §6 interdit.
- **Critère de sortie.** Les quatre verdicts. Un résultat nul ou défavorable reste publiable.

### 4.5 Axe C — mondes plus complexes sans règles imposées

L'ordre du plan est conservé : étapes 3, 4 puis 5. Trois règles valent pour tout l'axe. Le contrat physique et sensoriel d'une famille est figé avant toute exposition. Chaque porte ne teste qu'un mécanisme. Tout mécanisme passe par la détresse prédite D, avec son coût payé en énergie et en vigilance.

Je propose de commencer par F2 (sources saisonnières). Elle n'exige aucun capteur nouveau, et une strate de révision existe déjà ([STAGE0_REVISION.md](STAGE0_REVISION.md)).

#### RP-C1 · H1 · Contrat de la première famille nouvelle (F2) et mesure de base de la référence

- **Question falsifiable.** Dans un monde à sources saisonnières, la référence P1.3 révise-t-elle ses croyances, et avec quelle latence, sans aucun mécanisme ajouté ?
- **Lien avec l'intention.** Mesurer d'abord ce que l'individu fait seul dans un monde plus complexe, avant de lui ajouter quoi que ce soit.
- **Falsificateur et règle d'arrêt.** Le contrat est rejeté si F2 n'est qu'un générateur F0 renommé. La mesure de base ne donne lieu à aucune retouche de la référence.
- **Contrôle ou ablation.** Impulsions de F0. Contrôle à changement gelé.
- **Observable.** Latence de révision définie en première personne, survie à l'horizon, coût cognitif par pas vécu.
- **Plus petit test exécutable.** La spécification du générateur et un contrôle structurel sans vie (parité et collisions des spécifications).
- **Dépendances.** DÉC-2. Génomes sélectionnés de RP-B2 pour une mesure conforme à l'ADR-0015. À défaut, génomes de génération 0, en descriptif.
- **Coût.** 2 à 4 jours pour le contrat et le générateur. **(hypothèse)** 100 à 300 vies de développement pour la mesure de base.
- **Autorisation requise.** ADR-0020 pour le contrat. Autorisation indexée pour toute vie. Les partitions de développement, de sélection, de validation et de réserve sont déclarées d'avance.
- **Risque de règle imposée ou d'oracle.** Le calendrier des saisons reste caché. Aucun capteur nouveau, aucune étiquette, aucun conseil d'action.
- **Critère de sortie.** T : générateur testé. E : contrat gelé. S : aucun, la mesure est descriptive. Tr : base de comparaison de RP-C2.

#### RP-C2 · H2 · Étape 3 en trois portes séparées

- **Question falsifiable.** Chaque mécanisme, pris seul (détection de changement, puis causes latentes, puis factorisation par attributs perçus), réduit-il la latence de révision sans perte de survie, sur des génomes sélectionnés ?
- **Lien avec l'intention.** S'adapter à un monde qui change, par la détresse prédite et son coût payé.
- **Falsificateur et règle d'arrêt.** Non-infériorité de la survie avec une marge figée avant exposition, et latence de révision. Un échec conserve la référence précédente.
- **Contrôle ou ablation.** Contrôle à changement gelé. Transfert vers un objet jamais vu qui partage des attributs perçus.
- **Observable.** Survie à l'horizon, latence de révision, coût par pas vécu.
- **Plus petit test exécutable.** Un falsificateur logiciel sans vie pour chaque mécanisme, exécuté une fois.
- **Dépendances.** RP-A2 pour la règle de transition, RP-B2 pour les génomes sélectionnés, RP-C1.
- **Coût.** **(hypothèse)** 3 à 6 jours par porte. Le nombre de vies dépend du plan d'échantillonnage de l'étape 0.
- **Autorisation requise.** Protocole gelé et levée indexée pour chaque porte. Indices de validation neufs, au moins 120.
- **Risque de règle imposée ou d'oracle.** Un détecteur écrit comme « si tel signe, alors explorer » serait une règle imposée. Il doit rester un calcul payé, évalué par D.
- **Critère de sortie.** Les quatre verdicts, pour chaque porte.

#### RP-C3 · H2 à H3 · Étapes 4 et 5, familles F1 et F3 à F5

- **Question falsifiable.** Celles du plan : crédit différé évalué par la détresse courante (étape 4), puis topologie apprise dans des mondes plus grands avec obstacles (étape 5).
- **Lien avec l'intention.** Des mondes plus complexes, toujours sans carte ni poids hérités.
- **Falsificateur et règle d'arrêt.** Ceux du plan. Un résultat nul ou défavorable reste publiable, sans réglage sur une porte ouverte.
- **Contrôle ou ablation.** Ablation des valeurs apprises sur conditions neuves (étape 4). Mécanisme de frontière actuel comme comparateur (étape 5).
- **Observable.** Survie à l'horizon, coûts payés, latences.
- **Plus petit test exécutable.** Le contrat de chaque famille, puis un falsificateur logiciel sans vie.
- **Dépendances.** RP-C2. F1 exige un contrat sensoriel nouveau (percevoir un obstacle adjacent), à rayon de perception inchangé. Sous `HOLD_NO_VERDICT`, « planifier dans le financement de l'étape 2 » se lit « budget fixe hérité ».
- **Coût.** Non estimé à ce stade. À chiffrer dans chaque protocole.
- **Autorisation requise.** Protocole gelé et levée indexée pour chaque porte et chaque famille.
- **Risque de règle imposée ou d'oracle.** Carte complète cachée ou héritée, détour écrit par le concepteur, capteur accordé en silence.
- **Critère de sortie.** Les quatre verdicts, pour chaque porte.

**Hors chemin critique.** L'audit transversal de Competition reste en priorité basse, comme dans le plan. L'issue #1111 est à instruire avant la première porte de l'axe C, pour décider si le biais de l'auto-projection est accepté comme trait figé de la référence ou corrigé par une porte dédiée.

### 4.6 Axe D — release du moteur natif I3

Cet axe est parallèle. Aucun de ses succès ne compte comme preuve scientifique.

#### RP-D1 · H1 · R1 et R2 : naissance native enregistrée et M11 hors hôte

- **Question falsifiable.** Une autorité indépendante, hors hôte, rejette-t-elle le retour arrière complet des magasins locaux et de son propre magasin ?
- **Lien avec l'intention.** Un individu dont l'enjeu est lui-même doit avoir une identité unique et une mort qui ne se rejoue pas.
- **Falsificateur et règle d'arrêt.** La matrice de fautes de l'issue #1339. Tout retour arrière accepté fait échouer R2. Aujourd'hui, le retour arrière intégral du magasin de l'autorité est encore accepté ([README.md](README.md), entrée R2.4).
- **Contrôle ou ablation.** Le serveur de test en boucle locale existant.
- **Observable.** Résultats de la matrice de fautes, débit.
- **Plus petit test exécutable.** Rejouer les tests de retour arrière existants contre une autorité hébergée et administrée à part, avec une clé protégée.
- **Dépendances.** Issues #1331 et #1339.
- **Coût.** **(hypothèse)** 3 à 8 jours d'agent, plus un hébergement séparé. 0 vie scientifique.
- **Autorisation requise.** ADR-0020 §4 et §6 pour le code. Propriétaire pour l'hébergement et les clés.
- **Risque de règle imposée ou d'oracle.** Aucun pour la cognition. Il reste interdit de restaurer un état incertain ou terminal.
- **Critère de sortie.** T seulement : R1 et R2 démontrés sur le SHA exact. E, S et Tr : sans objet.

#### RP-D2 · H2 à H3 · R3 à R5 : exécution intégrée, tests sur la source exacte, bascule I1 vers I3

- **Question falsifiable.** Une session native complète passe-t-elle ses tests sur le SHA exact, avec injection de fautes, sans importer aucun état d'une autre génération ?
- **Lien avec l'intention.** Un moteur qui porte des individus nés sans jamais les ressusciter ni les migrer.
- **Falsificateur et règle d'arrêt.** Un seul état d'I1 importé, ou une seule reprise après la mort, fait échouer R4.
- **Contrôle ou ablation.** Parité avec une vie de référence `run_life`. Isolation des générations.
- **Observable.** Tests sur le SHA exact en Python 3.11 et 3.12. Aujourd'hui, aucun contrôle n'est attaché aux commits de `main` (section 1.2).
- **Plus petit test exécutable.** Une session native de fumée, sur fixture `engineering`.
- **Dépendances.** RP-D1. R5 n'est pas autorisé par l'ADR-0020 et demande un acte de release distinct. Je propose de lier R5 à une politique minimale de suivi des individus nés (questions G3) **(proposition)**.
- **Coût.** Non estimé à ce stade.
- **Autorisation requise.** Tests objectifs pour R3 et R4 (ADR-0020 §6). Acte de release pour R5.
- **Risque de règle imposée ou d'oracle.** Une autorité de contrôle moteur extérieure à l'individu, ajoutée au nom de la sûreté sans arbitrage.
- **Critère de sortie.** T seulement. La bascule ne dit rien de l'étape 2.

### 4.7 Axe E — besoin social

Cet axe se limite à une conception et à ses prérequis. Aucune vie n'y est prévue.

#### RP-E1 · H0 · ADR proposé « besoin social » : conception

- **Question falsifiable.** Peut-on définir un besoin social inné et générique comme un canal interne de plus dans la détresse D, de poids héritable, sans prescrire aucun comportement et sans oracle d'identité ?
- **Lien avec l'intention.** Le propriétaire le conçoit comme inné, générique, de force héritable, avec un gène qui évolue au cours de la vie. L'ADR-0018 en donne le schéma.
- **Falsificateur et règle d'arrêt.** La conception est rejetée dans deux cas. Soit le besoin ne peut s'écrire que comme une prime attachée à un acte (s'approcher, suivre, partager). Soit il exige de savoir qui est « un autre comme moi » autrement que par des attributs perçus.
- **Contrôle ou ablation.** À prévoir par l'ADR : ablation à génome égal (poids mis à zéro), bras de « socialité instrumentale » sans besoin propre, marqueurs neutres en lignée.
- **Observable.** Un texte d'ADR qui tranche quatre points : le canal et sa loi de restauration, son caractère létal ou non, son évolution au cours de la vie, et le sort du gène `temperament.affiliation`.
- **Plus petit test exécutable.** Une note d'une à deux pages, relue contre l'ADR-0014 §4 et §6.
- **Dépendances.** DÉC-4. Ce chantier n'attend ni l'axe A ni l'axe B.
- **Coût.** 1 à 2 jours. 0 World, 0 vie.
- **Autorisation requise.** Acceptation d'un nouvel ADR. Il étend le périmètre fixé par l'ADR-0016 §6 sans modifier ce texte.
- **Risque de règle imposée ou d'oracle.** C'est le chantier le plus exposé. Trois points demandent la lecture du propriétaire.
  1. **« Un gène qui évolue au cours de la vie ».** Je propose de le lire comme une valeur innée, plus une loi de plasticité elle-même innée. La [spécification](SPECIFICATION.md) cite cette allostasie parmi les sujets hors périmètre. La valeur vécue meurt avec l'individu. La transmettre reviendrait à hériter une expérience, ce que l'ADR-0014 §6 interdit. **(hypothèse de lecture)**
  2. **Une loi générique plutôt qu'une loi sociale.** Une loi de plasticité valable pour tous les canaux est moins une règle qu'une loi réservée au canal social.
  3. **La sélection peut éteindre le besoin.** Sous sélection par la seule persistance, un besoin social ne se maintient que si le lien aide à persister. Sinon, son poids dérivera vers zéro. Ce résultat doit rester acceptable et publiable.
- **Critère de sortie.** T, E et S : sans objet. Tr : ADR accepté ou refusé.

#### RP-E2 · H2 · Contrat F6 minimal à deux individus : prérequis

- **Question falsifiable.** Un `World` à deux corps conserve-t-il le rejeu exact, l'invariance au renommage (individus compris), la perception locale et le paiement individuel des pensées ?
- **Lien avec l'intention.** Sans autres individus perçus en première personne, un besoin social n'a pas d'objet.
- **Falsificateur et règle d'arrêt.** Échec si le monde à un seul individu ne redonne pas exactement le `World` actuel, ou si l'ordre des individus change une vie.
- **Contrôle ou ablation.** Parité avec le `World` actuel. Permutation des individus.
- **Observable.** Empreintes de rejeu, reçus de coûts par individu.
- **Plus petit test exécutable.** Un falsificateur logiciel, sans vie scientifique.
- **Dépendances.** RP-E1 accepté. Le contrat doit trancher l'ordre d'action, l'occupation des cases, le partage des ressources et l'unité statistique indépendante, qui devient le monde et non l'individu. Aujourd'hui, `World` ne porte qu'un corps ([world.py](../modules/world.py)).
- **Coût.** **(hypothèse)** 4 à 8 jours. 0 vie scientifique.
- **Autorisation requise.** ADR de RP-E1. ADR-0020 pour le logiciel.
- **Risque de règle imposée ou d'oracle.** Donner à l'individu l'identité ou l'état interne de l'autre serait un oracle. Un canal de communication accordé en silence serait un capteur non déclaré.
- **Critère de sortie.** T : contrat testé. E et S : aucun. Tr : ouvre une porte « besoin social » à l'horizon H3, non décrite ici.

### 4.8 Axe F — outillage et gouvernance de la recherche

Ces trois chantiers sont hors chemin critique : ils n'ajoutent aucune information scientifique et ne débloquent pas la release. Ils évitent que la dérive se reproduise.

#### RP-F1 · H0 · Couverture d'I3 par le coordinateur

- **Question falsifiable.** Après correction, `recommend` nomme-t-il une question I3 et ses résultats négatifs au HEAD courant ?
- **Lien avec l'intention.** Les agents doivent être orientés vers I3, la référence choisie.
- **Falsificateur et règle d'arrêt.** Échec si la sortie oriente encore vers I2 par défaut. Une seule passe, sans refonte de l'outil.
- **Contrôle ou ablation.** La sortie actuelle, consignée en section 1.3.
- **Observable.** Questions I3 dans [research-program.json](../../../config/research-program.json) : valeur du calcul (étape 2), sélection de l'inné (étape 6), généralisation (étapes 3 à 5), portes R0 à R5.
- **Plus petit test exécutable.** Un test de l'outil sur une fixture.
- **Dépendances.** Aucune.
- **Coût.** 1 à 2 jours. 0 World, 0 vie.
- **Autorisation requise.** ADR-0020 §4.
- **Risque de règle imposée ou d'oracle.** Aucun. Une recommandation n'est jamais une autorisation.
- **Critère de sortie.** T : test vert. E, S et Tr : sans objet.

#### RP-F2 · H0 · Surface d'entrée I3 réconciliée, gel inscrit

- **Question falsifiable.** Un agent qui suit l'ordre de lecture d'AGENTS.md rencontre-t-il le gel et le chemin critique en vigueur en trois documents au plus ?
- **Lien avec l'intention.** Un arrêt décidé doit être lisible là où le travail commence.
- **Falsificateur et règle d'arrêt.** Échec si l'un des documents du 12/11 reste introuvable depuis README, STATUS ou AGENTS.
- **Contrôle ou ablation.** L'état actuel (section 1.4, divergences 1 à 5).
- **Observable.** `next_scientific_action` mis à jour, modules de laboratoire classés, entrées « Current » alignées, issue #1061 close ou requalifiée, `STATUS.md` raccourci avec historique conservé.
- **Plus petit test exécutable.** Une recherche textuelle ajoutée au contrôle de navigation.
- **Dépendances.** DÉC-1.
- **Coût.** 0,5 à 1,5 jour. 0 World, 0 vie.
- **Autorisation requise.** Ce chantier modifie `ACTIVE_SURFACE.json` et AGENTS.md. Il demande donc un mandat explicite, que cette mission n'a pas.
- **Risque de règle imposée ou d'oracle.** Aucun.
- **Critère de sortie.** T : contrôle de navigation vert. Tr : gel visible.

#### RP-F3 · H0 · Budget de calcul et de CI, règle d'entrée des études

- **Question falsifiable.** Chaque étude ouverte nomme-t-elle la décision que son résultat peut changer, et un plafond de calcul ?
- **Lien avec l'intention.** Dépenser pour ce qui informe de bout en bout.
- **Falsificateur et règle d'arrêt.** Une étude sans décision nommée n'est pas écrite. Une confirmation dont le plafond est dépassé rend `HOLD_NO_VERDICT`.
- **Contrôle ou ablation.** La journée du 12/11 (section 3) sert de contre-exemple.
- **Observable.** Un tableau de budget par chantier : jours, vies, pas, heures-CPU.
- **Plus petit test exécutable.** Appliquer la règle aux 13 études du tableau 3.2, sans les rouvrir.
- **Dépendances.** Aucune.
- **Coût.** 0,5 à 1 jour. 0 World, 0 vie.
- **Autorisation requise.** ADR-0020 §4 pour la note. Propriétaire pour en faire une règle d'AGENTS.md.
- **Risque de règle imposée ou d'oracle.** Aucun.
- **Critère de sortie.** T : sans objet. Tr : règle adoptée ou refusée.

Trois constats chiffrés alimentent ce chantier.

- **Le calcul n'est pas le goulot des 7 198 paires.** Les vies seules représentent 5 758 400 pas, soit 1,3 à 2,1 heures-CPU à 0,8-1,3 ms par pas **(hypothèse)**. La contrainte est l'indépendance. La source précise qu'aucun cadre d'échantillonnage défendable ni assez d'indices neufs n'existent.
- **L'indépendance, elle, coûte cher.** Si l'unité indépendante est une population sélectionnée selon l'ADR-0015 (K = 40 candidats), la sélection domine. Avec 12 à 24 vies de sélection par candidat, 7 198 populations et 2 architectures demandent 6,9 à 13,8 millions de vies, soit 2,8 à 5,5 milliards de pas et 600 à 2 000 heures-CPU **(hypothèse)**. Un critère continu fondé sur D, plutôt que sur la survie binaire, pourrait réduire ce besoin. Ce point relève de l'arbitrage méthodologique interne RP-A1 pour le périmètre actuel ; tout futur plan confirmatoire doit justifier séparément son indépendance et sa puissance.
- **La CI coûte peu en minutes, beaucoup en surface.** Le dernier rapport cite 1 284 tests en 127 à 144 secondes par interpréteur. Le coût réel est la surface à maintenir : 121 modules de laboratoire, dont 71 pour l'étape 2, et 13 fichiers de tests ajoutés en une journée.

### 4.9 Axe G — horizon

Cet axe ne contient que des questions, des prérequis et des risques. Il n'a pas de calendrier.

**G1. Échanger avec la communauté de recherche.**

- Question : quel est le premier objet d'échange ? Les résultats négatifs bornés et la méthode (pensée payée, exécutions scellées en deux phases) sont présentables tels quels. Le premier objet concret est le dossier C01 interne traçable suivi de la décision de transition RP-A2 ; une lecture externe ultérieure reste facultative.
- Prérequis : un dossier de preuves stable (gel) et une issue écrite de l'étape 2 (RP-A2).
- Risque : présenter des PASS d'ingénierie comme des résultats.

**G2. Enjeux éthiques.**

- Question : l'ADR-0014 exclut toute affirmation de vécu ou de conscience. Quel résultat du projet ferait réviser cette position, et qui en juge ?
- Question : la sélection repose sur la mort de la plupart des individus. Une lignée complète en compte de l'ordre de 100 000 (8 × 64 × 200). Faut-il une revue avant chaque changement d'échelle ?
- Question : un monde à plusieurs individus ajoute des torts possibles entre eux. Le cadre doit-il précéder RP-E2 ?
- Prérequis : une position écrite du propriétaire.

**G3. Partager sans produire d'individus « corrompus et incontrôlables ».**

- Fait : le dépôt est déjà public, sous licences ouvertes, et des génomes sélectionnés y sont publiés.
- Question : que partage-t-on ? Le moteur, des génomes sélectionnés et des individus nés sont trois objets différents.
- Question : une licence ouverte déjà accordée peut-elle être restreinte après coup ? Ce point est à faire vérifier par un juriste.
- Question : qu'est-ce qu'un individu « corrompu » ? Définition opérationnelle possible **(hypothèse)** : un individu produit hors des invariants du projet, c'est-à-dire avec une pensée gratuite, une action forcée, un oracle, un état hérité, une mort annulée ou une récompense façonnée. Ce sont les interdits d'AGENTS.md.
- Prérequis : identité unique, provenance et anti-retour arrière (R1, R2, R4). Sans eux, aucun suivi n'est vérifiable. L'axe D conditionne donc l'axe G.
- Risque : un suivi seulement déclaratif, ou l'ouverture d'individus nés avant toute politique.

**G4. Versions plus avancées.**

- Question : quelle preuve minimale autorise à dire qu'une version est « plus avancée » ? Proposition : une porte ADR-0015 passée sur une famille réservée.

**G5. Mondes ouverts et robotique.**

- Question : dans un corps physique, que deviennent le coût payé, la mort irréversible et l'absence d'ordres, face à une autorité de sécurité ? AGENTS.md demande un arbitrage dès que cette autorité doit changer.
- Prérequis : contrat sensoriel et physique figé, budget de temps réel, politique de garde.
- Risque : un arrêt d'urgence externe est une action forcée au sens des invariants. Il faut le dire avant, pas après.

### 4.10 Amendements proposés

**Aucun de ces amendements n'est appliqué par cette PR.** Ils ne valent que si le propriétaire accepte les décisions correspondantes.

À [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md) :

1. Ligne « étape 2 » : statut `HOLD_NO_VERDICT` (suspension, non clôture), référence P1.3 avec budgets hérités fixes, renvoi à l'ADR de RP-A2.
2. Règle de dépendance : préciser qu'une suspension assortie d'une décision de référence explicite vaut « décision explicite » pour les étapes qui ne dépendent pas d'un budget de pensée adaptatif.
3. Ligne « étape 6 » : la scinder en « 6 légère, avancée » et « 6 complète, différée ».
4. Ligne « étape 0 » : nommer la lignée courte comme premier usage du plan à huit populations.
5. Étape 5 : lire « financement de l'étape 2 » comme « budget fixe hérité » tant que l'étape 2 est suspendue.
6. Ligne F6 : « conception autorisée, implémentation hors périmètre », après l'ADR de RP-E1.

Au [chemin critique du 12 novembre](STAGE2_AUDIT_DELTA_AND_CRITICAL_PATH_2026-11-12.md) :

1. Déclarer canonique la numérotation C00 à C07. N0 à N7 et R00 à R07 en sont les équivalents terme à terme. La numérotation C00 à C05 du 11/11 n'est plus employée.
2. C01 : remplacer l'exigence de relecteur par une matrice interne versionnée à trois issues, sans date butoir ; à pièces inchangées, retenir `HOLD_NO_VERDICT` pour l'étape 2 générale.
3. C02 : une source ne devient candidate que si l'audit C01 interne identifie une question distincte, un signal personnel nouveau et un falsificateur préannoncé ; les cas déjà exposés ne peuvent servir à la sélection.
4. C07 : ajouter la variante `HOLD_NO_VERDICT` et sa règle de transition.
5. Ajouter la règle de gel de la section 3.6.

**Sort de ce document.** Après arbitrage, deux issues sont possibles. Soit ses amendements sont portés dans les deux documents ci-dessus et ce fichier est marqué comme remplacé. Soit la PR est fermée sans suite. Les identifiants `RP-` ne survivent dans aucun des deux cas.

## 5. Chemin critique et pistes parallélisables

### 5.1 Chemin critique (7 chantiers)

Chaque ligne dit pourquoi le chantier y figure : il augmente l'information scientifique de bout en bout, il en est un maillon nécessaire, ou il débloque la release.

| Ordre | Chantier | Horizon | Pourquoi il est sur le chemin | Dépend de | Coût |
| --- | --- | --- | --- | --- | --- |
| 1 | RP-A1 puis RP-A2, sans attente externe | H0 | **Transition.** Par lui-même, il n'ajoute pas d'information de bout en bout et ne débloque pas la release. Il est maintenu parce que le plan en vigueur place les étapes 3 à 5 derrière une décision explicite de l'étape 2. Sans cela, il serait hors chemin critique. | Dossier C01 interne | 1 à 2 jours d'agent, 0 relecteur, 0 vie |
| 2 | RP-B1 | H0 | **Maillon** de RP-B2 : protocole, transport, répétition scellée. | DÉC-2, DÉC-3 | 2 à 4 jours, 0 vie scientifique |
| 3 | RP-B2 | H1 | **Information.** Première mesure de bout en bout de la boucle longue, de la vie vécue jusqu'à l'inné. | RP-B1, levée, indices | 0,5 à 1 jour ; 2 300 à 6 000 vies ; moins d'une heure-CPU **(hypothèse)** |
| 4 | RP-C1 | H1 | **Information.** Première mesure de la référence hors F0. | DÉC-2 ; RP-B2 pour les génomes | 2 à 4 jours ; 100 à 300 vies **(hypothèse)** |
| 5 | RP-C2, première porte seulement (détection de changement) | H2 | **Information.** Première porte d'un mécanisme sans règle dans une famille nouvelle. | RP-A2, RP-B2, RP-C1 | 3 à 6 jours ; vies à chiffrer |
| 6 | RP-D1 | H1 | **Release.** Débloque R1 et R2. | #1331, #1339 | 3 à 8 jours **(hypothèse)** ; 0 vie scientifique |
| 7 | RP-B3 | H2 | **Information.** La thèse centrale à pleine échelle, sur des familles réservées. | RP-B2, RP-C1 | environ 10^8 pas **(hypothèse)** |

```text
RP-A1 ─────────► RP-A2 ───────────────┐
DÉC-3 ──► RP-B1 ──► RP-B2 ──┬────────────┼──► RP-C2 (porte 1)
DÉC-2 ───────────► RP-C1 ───┼────────────┘
                            └──► RP-B3
RP-D1 ──► RP-D2   (parallèle, sans lien avec les verdicts scientifiques)
```

**Total pour H0 et H1** **(hypothèse)** : 8,5 à 19 jours d'agent, aucun jour de relecteur obligatoire, au plus 6 300 vies environ, moins de deux heures-CPU. La contrainte n'est pas le calcul. Ce sont les deux levées à consigner par le propriétaire et les plages d'indices neuves.

### 5.2 Pistes parallélisables

- **Axe D en entier** (RP-D1 puis RP-D2). Il n'attend aucune décision scientifique.
- **RP-E1**, la conception du besoin social, dès DÉC-4. Aucune vie.
- **RP-F1, RP-F2 et RP-F3.** RP-F2 suit DÉC-1.
- **RP-B0**, facultatif, avant RP-B1.
- **RP-A3 et RP-A4**, conditionnels. Ils sont hors chemin par défaut.
- **RP-C3, RP-D2 et RP-E2**, après leurs prérequis.

Une chose ne se parallélise pas : créer des sources de vies pendant qu'une sélection ou une validation n'est pas scellée.

### 5.3 Hors chemin critique

- Toute nouvelle étude, garde ou analyse post-hoc de l'étape 2 (gel de la section 3.6).
- Les contrôleurs 2.2 et 2.3, tant qu'aucune source distincte n'a passé RP-A3.
- L'audit transversal de Competition.
- Les axes F et G.

## 6. Décisions à arbitrer par le propriétaire

### DÉC-1 — Sortir de l'étape 2 sans relecteur obligatoire

**Arbitrage déjà exprimé :** le propriétaire retire la dépendance à un relecteur pour RP-A1. Cette décision de méthode ne vaut ni acceptation globale de cette feuille de route proposée, ni autorisation expérimentale. Le gel et la transition de RP-A2 demeurent à consigner selon les autorités en vigueur.

| Option | Coût | Conséquence |
| --- | --- | --- |
| **A (retenue pour RP-A1).** Geler les nouvelles variantes de pensée, réutiliser l'audit C01 interne et produire une matrice contradictoire versionnée. Choisir entre `CLOSE_BOUNDED`, `DISTINCT_SOURCE_REQUIRED` et `HOLD_NO_VERDICT` sur preuves existantes, puis rédiger RP-A2 sans délai d'avis. | 1 à 2 jours d'agent au total, 0 relecteur, 0 vie | Une décision motivée existe sans attendre un tiers. À preuves inchangées, `HOLD_NO_VERDICT` suspend la question générale ; les négatifs E1/E3 restent bornés. |
| **B.** Publier immédiatement `HOLD_NO_VERDICT` à partir du C01 déjà versionné, sans refaire la matrice. | 0,5 à 1 jour d'agent, 0 vie | Raccourci documentaire possible mais moins explicite sur les critères et contre-arguments ; aucune validation indépendante invoquée. |
| **C.** Poursuivre sans nouvelle source la campagne interne sur les « erreurs personnelles passées ». | Non borné : 13 études en une journée au rythme du 12/11 | Risque de sélection post-hoc et de dérive ; à ne pas retenir. |

**Recommandation : A.** L'absence de relecteur ne transforme ni l'avis interne en preuve indépendante ni un diagnostic `HOLD_NO_VERDICT` en clôture scientifique. Les éventuels avis externes sont facultatifs pour cette étape documentaire. Les contrôles de puissance, de source et de permissions pour de futures études restent distincts.

### DÉC-2 — La suite peut-elle avancer sous `HOLD_NO_VERDICT` ?

| Option | Coût | Conséquence |
| --- | --- | --- |
| **A (recommandée).** Oui, par amendement explicite du plan. L'étape 0, la lignée courte et les contrats de mondes avancent tout de suite. Les portes des étapes 3 à 5 avancent avec le budget de pensée fixe hérité, sans aucune affirmation sur un budget adaptatif. | L'amendement : 0,5 jour | L'étape 2 cesse d'être un goulot et reste rouvrable. Si elle aboutit un jour, les portes passées à budget fixe seront à relire. |
| **B.** Oui pour l'étape 0 et la lignée courte seulement. | Aucun | Prudent. L'axe « mondes plus complexes » reste gelé sans échéance. |
| **C.** Non. Tout attend un verdict de l'étape 2. | Aucun aujourd'hui | Tout le programme attendrait une clôture générale non établie malgré une décision interne `HOLD_NO_VERDICT` disponible. |

**Recommandation : A.** L'analyse des dépendances la soutient. L'étape 3 s'appuyait sur l'étape 1, qui est close. L'étape 4 attend des « décisions de budget », et un budget fixe en est une. L'étape 5 planifie « dans le financement de l'étape 2 », qui est alors le budget hérité. L'étape 6 ne dépend pas de l'étape 2 ([DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md), tableau des étapes).

### DÉC-3 — Faut-il lancer la lignée courte, et sur quels gènes ?

| Option | Coût | Conséquence |
| --- | --- | --- |
| **A (recommandée).** L'autoriser sur P1.3 tel quel. `beta_u` est le critère principal. ω, `affiliation` et `reward_sensitivity` servent de témoins neutres. κ n'est pas testé. | 2,5 à 5 jours d'agent, 2 300 à 6 000 vies, moins d'une heure-CPU **(hypothèse)** ; une levée et une plage d'indices | Première mesure de la thèse centrale. Des génomes sélectionnés deviennent disponibles pour les portes suivantes. |
| **B.** Attendre une référence qui exprime ω et κ. | Un nouvel ADR qui rouvre l'étape 1, à l'encontre de l'ADR-0018 §5, puis un candidat et sa porte | La thèse centrale reste non exercée pour une durée indéterminée. |
| **C.** Garder l'ordre actuel du plan, avec l'étape 6 en dernier. | Aucun aujourd'hui | Les portes des étapes 3 à 5 se jouent sans savoir si la sélection agit. |

**Recommandation : A**, avec une réserve que le propriétaire doit connaître avant de décider. L'ADR-0018 recommandait de vérifier ω, κ et `beta_u`. Sur la référence actuelle, seul `beta_u` peut l'être. ω ne peut servir que de témoin, et κ n'existe pas.

### DÉC-4 — Quand concevoir le besoin social ?

| Option | Coût | Conséquence |
| --- | --- | --- |
| **A (recommandée).** Lancer maintenant la conception (RP-E1). L'implémentation reste hors périmètre. | 1 à 2 jours, 0 vie | Les trois points de vigilance de RP-E1 sont tranchés tôt, par le propriétaire. |
| **B.** Attendre le résultat de la lignée courte. | Aucun aujourd'hui | La conception profite d'un premier résultat sur les gènes, mais prend du retard. |
| **C.** Maintenir F6 hors périmètre, sans conception. | Aucun | L'écart avec l'intention reste entier. |

**Recommandation : A.** Le coût est faible, et la lecture de « gène qui évolue au cours de la vie » engage la règle d'héritage de l'ADR-0014. Mieux vaut la fixer avant tout code.

### DÉC-5 — Politique de partage (à préparer, sans calendrier)

| Option | Coût | Conséquence |
| --- | --- | --- |
| **A.** Garder l'ouverture actuelle, et ajouter une charte d'intégrité et une attestation de conformité des individus. | Non chiffré | Simple. Le suivi reste volontaire. |
| **B.** Garder le moteur ouvert, mais placer sous garde les individus nés et les futurs génomes sélectionnés. | Non chiffré | Sépare ce qui est déjà public de ce qui ne l'est pas encore. Demande une identité et une provenance vérifiables (axe D). |
| **C.** Restreindre les versions futures. | Non chiffré | À faire vérifier par un juriste. Les versions déjà publiées restent ouvertes. |

**Recommandation.** Je ne recommande pas d'option de fond sans avis juridique et éthique. Je recommande seulement un ordre : cette décision doit précéder la bascule R5 et toute collaboration externe portant sur des individus nés. Ma préférence provisoire va à B **(hypothèse)**.

## 7. Ce que cette feuille de route ne prétend pas

- **Ce n'est pas une revue indépendante.** C'est une analyse produite par un agent ; RP-A1 est désormais un arbitrage interne traçable, sans prétendre être une validation indépendante.
- **Ce n'est pas une autorisation.** Elle n'ouvre aucun World, ne crée aucune vie, n'attribue aucun indice et ne lève aucun moratoire.
- **Elle n'apporte aucun résultat nouveau** et ne réinterprète aucun résultat négatif ou nul. Un test vert ou une survie plausible ne vaut jamais un GO scientifique.
- **Sa lecture n'est pas exhaustive.** `STATUS.md` (2 195 lignes) n'a été lu qu'en tête. Les fils de commentaires des issues n'ont pas été lus, faute de quota d'API ; seul le début de leur corps l'a été. La CI n'a pas été interrogée par l'API.
- **L'expression des gènes est établie par lecture du code**, pas par un test dynamique. RP-B1 prévoit ce test.
- **Ses estimations sont des fourchettes.** Tout ce qui est marqué « hypothèse » reste à vérifier.
- **C'est un instantané** à `ff4cad2`. `main` a continué d'avancer pendant la rédaction (section 8).
- **Elle n'est pas une cinquième numérotation durable.** Les identifiants `RP-` s'effacent après arbitrage.

## 8. Handoff

Format demandé par [AGENTS.md](../../../AGENTS.md).

| Rubrique | Contenu |
| --- | --- |
| Génération | I3, proposition non enregistrée, référence de développement sous l'ADR-0020 |
| Tâche | Proposition de feuille de route, documentation seule |
| Base d'analyse | `ff4cad2d01011828518db5dda1221d9afc96a8d3` |
| Base de la branche | `24dadc509e3a96339def0ddb5f68c257feeabf08`, HEAD de `main` au moment du handoff (13 novembre 2026, 00:11 +01:00) |
| SHA du commit | Porté par la description de la PR et par le message de handoff. Un document ne peut pas contenir le SHA du commit qui le contient. |
| Fichiers modifiés | `src/i3/docs/ROADMAP_PROPOSAL_2026-11-12.md` (ajout). `src/i3/docs/README.md` : un paragraphe « Proposed » de six lignes. Ce lien est jugé nécessaire, parce que les documents de chemin critique du 12/11 sont introuvables depuis la surface d'entrée (section 1.4). |
| Invariants | Aucun fichier de `modules/`, `runtime/`, `lab/` ou `tests/`. Ni registre, ni `engine.json`, ni `ACTIVE_SURFACE.json`, ni ADR, ni protocole figé, ni original, ni archive. |
| Impact comportemental attendu | Aucun |
| Worlds, vies, runners scientifiques | 0, 0, aucun |
| Comportement observé | Sans objet : rien n'a été exécuté. |
| Statut scientifique | Inchangé. Étape 2 `NOT_ISSUED`, référence P1.3 funded-v2, I3 non enregistré, I1 actif. |

**Contrôles.**

| Contrôle | Statut | Résultat ou raison |
| --- | --- | --- |
| `python tools/check_repo_navigation.py --scope entrypoints` | PASS | 540 contrôles, 0 erreur, 0 avertissement, avant comme après la modification. Avec `--scope current` : PASS, 1 083 contrôles. |
| Test `test_i3_internal_markdown_links_resolve` de [test_active_surface.py](../../../tests/i3/test_active_surface.py), lancé seul | PASS | Liens Markdown internes à I3, ce document compris |
| Vérification locale de tous les liens relatifs de ce document | PASS | 83 liens relatifs, aucun lien rompu |
| `python tools/research_coordinator.py recommend` | exécuté, lecture seule | Écart consigné en section 1.3 |
| Suite logicielle I3 complète (1 284 tests) | NOT_RUN | Documentation seule. AGENTS.md déconseille la CI lourde pour un document. |
| CI GitHub sur le SHA exact | NOT_RUN | API hors quota. Une PR de documentation seule ne déclenche pas le workflow I3. |
| Runners scientifiques, cohortes, réserve P4 | NOT_RUN | Interdits par la mission |

**`main` pendant la rédaction.** Entre `ff4cad2` et `24dadc5`, deux commits ont ajouté quatre fichiers : une quatorzième étude d'étape 2, `FUTURE_PREQUENTIAL_CUSTODY`, de verdict technique `SOFTWARE_PREQUENTIAL_CUSTODY_READY_NO_EFFICACY_VERDICT` et de statut scientifique `NOT_ISSUED`. Depuis `8c7b9a4`, le total passe à 30 commits, 61 fichiers et 5 900 lignes. Cette étude n'a été lue que dans son en-tête. Elle ne change aucune conclusion de ce document et prolonge le constat de la section 3 : le compteur est passé de 24 à 28 puis à 30 commits pendant cette seule mission.

**Limites.** Celles de la section 7.

**Prochaine étape falsifiable.** Finaliser le dossier interne RP-A1, consigner RP-A2 sans relecteur, et traiter séparément les décisions de nouvelle source ou de cohorte. DÉC-3, puis RP-B1.

**Issues liées.** #1062 (étape 2), #1060 (étape 0), #1331 et #1339 (release). La PR draft qui porte ce document est référencée dans sa propre description.
