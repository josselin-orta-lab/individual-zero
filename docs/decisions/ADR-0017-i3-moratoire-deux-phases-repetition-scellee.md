# ADR-0017 - I3 : moratoire sur l'ouverture de mondes, exécution en deux phases et répétition générale scellée

## Context

Depuis la fermeture de 56/57, cinq pilotes de développement ont été ouverts puis
clos sur des défauts d'ingénierie, sans aucun verdict H1-H6 ni J1-J7.

| Pilote | Bras | Arrêt | Phase |
| --- | --- | --- | --- |
| 58/59 | P1.3, G, H | 3e vie : désaccord de statut de traitement | réduction |
| 60/61 | P1.3, H, I, I ω = 0 | 6e vie : travail cognitif au-delà du budget pendant l'apprentissage | génération |
| 62/63 | idem | 19e vie : reçu de règlement manquant | génération |
| 64/65 | idem | 36e vie terminée : statut de traitement contradictoire | réduction |
| 66/67 | idem | 11e vie archivée : reçu post-contact invalide | réduction |

Trois constats :

1. **Trois arrêts sur cinq surviennent après qu'une vie complète a été générée
   et archivée.** Génération et réduction sont entrelacées : un défaut du
   réducteur interrompt la génération du reste du panel, et la règle d'arrêt sans
   nouvel essai clôt deux indices.
2. **Les défauts apparaissent dans des états rares de vies longues.** Ce sont une
   sonde payée sans phase B, une restauration après une sonde non financée, et
   des reçus post-contact. Le prévol actuel, neuf petites vies déjà exposées de
   DEVELOPMENT-0, ne les atteint pas.
3. **Les indices 58 à 67 sont consommés.** La cohorte de développement P2 compte
   100 indices (graines 2000 à 2099). Il reste les indices 68 à 99.

Au sens de la règle d'`AGENTS.md`, c'est une dérive : complexité, preuves locales
et CI s'accumulent sans information scientifique de bout en bout.
**DRIFT DETECTED.**

Un précédent existe : la préinscription P5B admet qu'un vérificateur d'archive
soit corrigé indépendamment et relancé sans générer de nouvelle vie, si les
octets originaux restent identiques.

## Options considered

| Option | Verdict | Raison |
| --- | --- | --- |
| Continuer pilote par pilote, en réparant après chaque arrêt | Rejetée | Chaque défaut consomme deux indices ; la cohorte s'épuise sans verdict |
| Rejouer ou compléter un panel clos | Rejetée | Contamination ; la source a changé depuis ; contraire à la règle de non-réessai |
| Assouplir la règle d'arrêt pour tout échec | Rejetée | Un défaut du moteur pendant une vie invalide la vie elle-même |
| Répéter sur les panels déjà exposés (58 à 67) | Rejetée par défaut | Leurs originaux existent ; une cohorte dédiée évite toute question de contamination |
| **Moratoire, exécution en deux phases, répétition générale scellée** | **Acceptée** | Coûte du calcul, aucun monde ; aucun résultat ne circule |

## Experimental evidence or constraints

- Résultats des pilotes clos :
  [58/59](../../src/i3/docs/studies/stage1-candidate-h-development-58-59/RESULTS.md),
  [60/61](../../src/i3/docs/studies/stage1-candidate-i-development-60-61/RESULTS.md),
  [62/63](../../src/i3/docs/studies/stage1-candidate-i-development-62-63/RESULTS.md),
  [64/65](../../src/i3/docs/studies/stage1-candidate-i-development-64-65/RESULTS.md).
- 66/67 : reçu `failure.json` sur la branche
  `evidence/i3-stage1-candidate-i-66-67-9db49f8c3b52` (commit
  `18a7e27bd79de81280e171fdf682f8a5f4195830`),
  `ENGINEERING_FAILURE_NOT_A_DEATH` après 10 vies admises, levé par
  `src/i3/lab/stage0_revision.py`. Protocole :
  [66/67](../../src/i3/docs/studies/stage1-candidate-i-development-66-67/PROTOCOL.md).
- Précédent de réparation de vérificateur :
  [préinscription P5B](../../src/i3/docs/P5B_HELDOUT_PREREG.md).
- Règle de dérive : [AGENTS.md](../../AGENTS.md). Portes :
  [ADR-0015](ADR-0015-i3-portes-sous-selection.md). Cohortes :
  [`p2_ecologies.py`](../../src/i3/lab/p2_ecologies.py).

## Decision

### 1. Moratoire

À la fusion de cette ADR, **aucun nouvel indice de monde I3 n'est ouvert**, quelle
que soit la cohorte : développement, sélection, validation ou réserve.

Restent permis : le travail logiciel, l'analyse en lecture seule des originaux
archivés dans les limites déjà en vigueur, et les répétitions scellées de la
décision 3.

Le gate logiciel lifecycle-custody v3 déjà figé par #1208 reste permis : il
n'ouvre aucun monde et ne constitue pas une répétition scientifique.

Le moratoire est levé quand quatre conditions sont réunies :

1. l'exécution en deux phases (décision 2) est implémentée et testée ;
2. la cohorte `engineering` (décision 3) est déclarée ;
3. une répétition scellée passe sur le SHA exact du prochain transport ;
4. le propriétaire consigne la levée dans `STATUS.md`.

### 2. Exécution en deux phases

Elle s'applique à tout panel vivant I3 ouvert après le moratoire : pilotes de
développement et portes ADR-0015.

1. **Phase G, génération.** Toutes les vies prévues sont générées, dans l'ordre
   figé, avec la source figée. Chaque original est archivé dès sa fin (gzip,
   SHA-256). Pendant G, rien n'est réduit, agrégé ni évalué, et les journaux
   n'affichent que l'avancement et les empreintes.
2. **Échec de génération.** Une exception du moteur pendant une vie garde la
   règle actuelle : arrêt, archivage, `ENGINEERING_FAILURE_NOT_A_DEATH`, aucun
   nouvel essai, panel clos.
3. **Fin de G.** Le manifeste des originaux (fichiers, empreintes, SHA
   d'exécution) est scellé sur la branche de preuves.
4. **Phase R, réduction.** Elle lit seulement les originaux scellés et calcule
   une fois les règles figées.
5. **Échec de réduction.** Le statut est `REDUCTION_DEFECT_PENDING_REPAIR`. Le
   panel n'est pas clos ; aucun résultat partiel n'est publié ni lu.
6. **Réparation aveugle.**
    - Le réparateur voit seulement le type et le message de l'exception, le
      fichier et la fonction, et la structure du reçu fautif : route, phase,
      travail, statuts de financement et de traitement. Jamais les corps, les
      actions, les prises, les morts, les durées, les fréquences de route ni les
      entrées ou sorties des règles.
    - La correction est validée sur des reçus synthétiques et sur les reçus
      structurels de panels déjà clos, puis fusionnée avec ses tests avant toute
      relance.
    - La réduction est relancée une fois sur l'archive complète, empreintes
      revérifiées.
    - Au plus deux cycles de réparation par panel. Au-delà, le panel est clos
      comme `ENGINEERING_FAILURE_NOT_A_DEATH`.
7. **Jamais** : modifier un original, générer une vie de plus, changer une
   règle, un seuil, un bras ou une graine.
8. **Pas de rétroactivité.** 58/59 à 66/67 restent clos. Leur génération a été
   tronquée par l'ancien entrelacement, et les compléter exigerait de nouvelles
   vies, avec une source qui a changé.

### 3. Répétition générale scellée

Avant toute exposition de nouveaux indices :

1. **Même pipeline, même échelle.** Le SHA d'exécution exact du transport prévu
   exécute le panel complet : mêmes bras, même nombre de vies, même horizon,
   mêmes familles, phases G et R, même runner, même réducteur, même matrice
   Python.
2. **Cohorte dédiée.** Une cohorte `engineering` est ajoutée à
   `p2_ecologies.COHORTS`, disjointe des quatre autres, par exemple
   90 000 à 90 999. Ses mondes, génomes et graines de vie viennent d'un espace de
   noms propre. Ils ne sont jamais admissibles comme preuve et peuvent servir à
   plusieurs répétitions.
3. **Sorties scellées.** Sont seuls publiés : le statut par phase, le nombre de
   vies générées et réduites, les exceptions avec leur reçu structurel, les
   empreintes, les contrôles d'invariants de travail et le temps moyen par pas.
   Survie, morts, durées, prises, routes, ω, corps et valeurs des règles ne sont
   ni publiés ni lus. Les originaux de répétition ne sont pas versionnés.
4. **Critère.** PASS exige 100 % de vies générées et réduites, aucune exception
   et tous les invariants. Tout changement de code après un PASS exige une
   nouvelle répétition sur le nouveau SHA.
5. **Échec.** Une répétition échouée ne consomme aucun monde scientifique : on
   répare et on recommence, sans limite.

### 4. Ce qui ne change pas

Les règles scientifiques figées (H1-H6, J1-J7), l'ADR-0015, l'interdiction
d'arrêt favorable, la règle d'échec de génération, la fermeture des panels déjà
exposés, et l'exclusion de la survie comme critère de continuation des pilotes.

## Consequences

- Chaque exposition coûte environ un panel de calcul en plus, mais ne consomme
  plus d'indices scientifiques pour des défauts d'ingénierie.
- Il faut un runner capable des deux phases et du mode répétition, et la cohorte
  `engineering`. Ces changements touchent du code que les protocoles déclarent
  protégé ; ils sont fusionnés avant tout nouveau protocole figé.
- Risque résiduel : qu'un reçu structurel laisse filtrer un résultat. La liste
  fermée des champs visibles et la limite de deux cycles le bornent.
- Hors périmètre, décisions séparées :
    - un runner unique paramétré, et des reçus validés dans le moteur au moment
      de la décision plutôt que par le réducteur après coup ;
    - la cohérence du terme du concepteur dans Candidate-I : curiosité retirée
      avant le premier contact, rétablie après par le repli de Candidate-H.

## Individuals / axes concerned

I3. Méthode de recherche et custodie de l'exécution. Aucun axe cognitif :
aucune physique, aucun génome et aucune cognition ne sont modifiés.

## Date and status

9 novembre 2026 : **ACCEPTÉ par le propriétaire.** Le moratoire prend effet à
la fusion de cette ADR.

## Post-acceptance implementation and owner-approved lift (9 November 2026)

**LIFTED, limited to the exact Stage-2.1 transport and frozen DEVELOPMENT
80/81 pilot.** The original moratorium and rationale above remain part of
the decision history. The owner explicitly approved the final technical
evaluation and the two disclosed custody equivalences before this lift:

1. Two-phase generation (G) and read-only reduction (R) are implemented
   and tested, with original gzip/SHA-256 custody.
2. The disjoint, permanently non-evidentiary `engineering` cohort is
   declared beside the historically pinned `P2.COHORTS`; the owner
   accepted this equivalent boundary without modifying the immutable
   ecological generator.
3. The hardened transport fingerprint `dcada9e221f79b9450a4f05fecd20e60ac6595bb306aa871f29e45aefea0b6f1`
   passed full-size sealed rehearsals in both Python 3.11 and Python 3.12:
   36/36 generated and reduced, zero invariant failures. The owner accepted
   the verified byte-for-byte identity of all 42 transport/plan files
   across rehearsals and the squash-merged `main` source as satisfying
   exact-source custody despite changed Git commit IDs.
4. The owner authorized the exact lift line in the canonical
   [I3 status ledger](../../src/i3/docs/STATUS.md). The ledger, not this
   historical ADR appendix, is the machine-readable authorization source.

The earlier unhardened fingerprint `15136d13…` is superseded and is
**not** authorized. No source, cognitive rule, body law, genome,
scientific control, cost model, frozen plan or R0-R4 rule was changed.

The immediate authorization is a single prospective Stage-2.1
DEVELOPMENT 80/81 pilot, **not** activation of I3 and **not** a general
scientific GO. Validation, selection, reserve and other World indices
retain their own prospective prerequisites. Panels 58/59 through 68/69
remain closed. The ADR-0017 no-retry generation rule and bounded blind
reducer-repair procedure remain fully binding after the lift.
