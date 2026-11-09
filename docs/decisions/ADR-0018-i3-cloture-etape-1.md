# ADR-0018 - I3 : dernier candidat de l'étape 1, règle d'arrêt et arbitrage de clôture

## Context

L'étape 1 doit dire si une évaluation dans l'unité des enjeux de l'individu, la
détresse prédite, peut remplacer la curiosité, la pertinence et la prudence que
P1.3 ajoute à ses scores. Depuis le 7 novembre, quatre candidats se sont
succédé sans y répondre :

- **Candidate-F** a été rejeté par sa porte ADR-0015 (0/240), effondré sous le
  coût de sa pensée.
- **Candidate-G** n'a survécu dans aucune vie de 56/57. Sans soutien, explorer
  ne valait rien ; avec soutien, la pensée coûtait autant que chez
  Candidate-F.
- **Candidate-H et Candidate-I** n'ont produit aucun verdict vécu : cinq
  pilotes ont été clos sur des défauts d'ingénierie, ce qui a conduit au
  moratoire de l'ADR-0017. Candidate-I ne retire d'ailleurs la curiosité
  qu'avant le premier contact ; après, il passe par le repli P1.3 de
  Candidate-H, qui la rétablit.

Aucune règle ne dit quand l'étape 1 s'arrête : chaque échec produit un nouveau
candidat. Le plan admet pourtant qu'une étape se clôt par un résultat explicite
et une décision de référence, pas nécessairement par un succès.

Des calculs préalables en bac à sable, détaillés en annexe du
[protocole Candidate-J](../../src/i3/docs/STAGE1_CANDIDATE_J.md), éclairent le
blocage. Ce ne sont pas des résultats :

- **Sous une projection précise, l'ignorance symétrique est aversive.** Sans
  espoir hérité (ω = 0), essayer une action inconnue vaut moins qu'attendre,
  d'autant plus que le corps est en manque. La détresse convexe et la mort
  absorbante l'imposent : les enjeux seuls ne peuvent pas amorcer le premier
  contact.
- **La projection de P1.3 inverse le signe de ces comparaisons près de la mort.**
  Une partie du bruit des résultats précédents sur le premier contact en vient.
- **Avec une échelle relative à la capacité du corps, l'espoir hérité devient
  sensible au besoin.** Il pousse à essayer et à explorer quand un manque
  approche, et s'éteint quand le corps est rassasié.

## Options considered

| Option | Verdict | Raison |
| --- | --- | --- |
| Clore l'étape 1 tout de suite, négativement | Rejetée | Aucun candidat cohérent n'a été testé : sans terme du concepteur partout, en une seule phase, avec une projection précise |
| Poursuivre Candidate-I | Rejetée comme dernier candidat | Hybride (curiosité rétablie après le contact), architecture à sonde fragile, échelle de l'a priori inadaptée |
| Laisser la série de candidats ouverte | Rejetée | Pas de règle d'arrêt : dérive |
| **Un dernier candidat, J, une règle d'arrêt et des issues fixées d'avance** | **Acceptée** | Teste enfin la question de l'étape 1, puis la ferme quoi qu'il arrive |

## Experimental evidence or constraints

- [Plan de développement](../../src/i3/docs/DEVELOPMENT_PLAN.md), étape 1 et
  discipline des portes.
- [Audit 56/57](../../src/i3/docs/studies/stage1-candidate-g-development-56-57/POSTHOC_FIRST_CONTACT_AUDIT.md)
  et [capacité de l'a priori partagé](../../src/i3/docs/studies/stage1-shared-first-contact-prior/RESULTS.md).
- [ADR-0014](ADR-0014-i3-lignee-enjeu-de-soi.md),
  [ADR-0015](ADR-0015-i3-portes-sous-selection.md),
  [ADR-0016](ADR-0016-i3-generalization-without-imposed-rules.md),
  [ADR-0017](ADR-0017-i3-moratoire-deux-phases-repetition-scellee.md).
- Famille R : [R-depletion-v1](../../src/i3/docs/STAGE0_REVISION.md).

## Decision

1. **Candidate-J est le dernier candidat de l'étape 1.** Son mécanisme est fixé
   par son [protocole](../../src/i3/docs/STAGE1_CANDIDATE_J.md) :
    - aucun terme du concepteur, dans aucune route ;
    - une seule phase de décision ;
    - un projecteur précis pour toutes les options ;
    - un a priori de premier contact partagé par l'essai imaginé et l'essai
      perçu, de la forme `(ω ± 1) × s` avec `s = κ × capacité`. ω est inchangé ;
      κ est un nouveau gène générique, sélectionné par la seule persistance.
2. **Parcours**, sous l'ADR-0017 :
    1. un falsificateur logiciel, exécuté une fois ;
    2. après la levée du moratoire, un pilote de développement 68/69 à trois
       bras : P1.3, Candidate-J, Candidate-J avec ω := 0 ;
    3. la porte de l'étape 1 sur la famille R-depletion-v1, selon l'ADR-0015,
       avec au moins huit populations indépendantes et des indices de
       validation ≥ 120 jamais ouverts.
3. **Critère de la porte.**
    - Critère principal : non-infériorité de la survie face à P1.3, avec une
      marge figée avant exposition.
    - Critères secondaires : latence de révision, coût cognitif par pas vécu,
      distribution des ω et κ sélectionnés.
    - Cet ordre amende le plan, qui demandait aussi une latence meilleure :
      remplacer le terme du concepteur sans perdre en survie est la question qui
      tranche l'étape 1.
4. **Règle d'arrêt.** L'étape 1 se clôt au premier des événements suivants :
    - le verdict de la porte ;
    - un verdict logiciel autre que `CANDIDATE_J_CAPACITY_SHOWN` ;
    - un pilote 68/69 qui n'aboutit pas après deux exécutions validées par
      répétition scellée ;
    - le **15 décembre 2026**.
5. **Issues et décisions de référence, fixées d'avance.**
    - **Si Candidate-J est non inférieur**, l'étape 1 est close **positive**.
      J devient la référence, et curiosité, pertinence et prudence sont
      retirées.
    - **Dans tous les autres cas**, l'étape 1 est close **négative**. P1.3 reste
      la référence. On consigne que les enjeux seuls n'amorcent pas le premier
      contact, et ce que l'espoir hérité a montré ou non. La curiosité de P1.3
      est reconnue comme une disposition innée : sa forme vient du concepteur,
      son poids (`beta_u`) est héritable. C'est l'option B de la note de
      premier contact.
    - **Aucun nouveau candidat d'étape 1** n'est ouvert ensuite.
6. **Ce qui ne change pas :** les ADR-0014 à 0017, les panels clos, et
   l'interdiction de régler quoi que ce soit sur des mondes exposés.

## Consequences

- **L'étape 2 est débloquée dans tous les cas**, sur la référence retenue. Sa
  première question est de savoir quand un calcul précis vaut son prix, par
  exemple ne payer la projection précise que lorsque les meilleures options sont
  plus proches que son erreur attendue. La courbe prix-survie du coût de la
  pensée y trouve naturellement sa place.
- **L'étape 6 mérite d'être avancée** sous une forme légère. Une courte lignée
  sur la référence retenue montrerait si la sélection déplace ω, κ ou `beta_u`,
  et ce qui se passe à leurs bornes. C'est la thèse centrale de l'ADR-0014, et
  elle n'a pas encore été exercée. C'est une recommandation, pas une décision.
- **Les étapes 3 à 5 restent différées**, mais l'a priori de J les prépare :
    - attributs perçus pour l'étape 3 ;
    - dommages différés pour l'étape 4 ;
    - distance et taux de découverte pour l'étape 5.
- **La famille F6 (autres individus) reste hors périmètre.** Un besoin social y
  suivrait le même schéma : inné, générique, de force héritable, évalué dans la
  détresse prédite.
- **Sur le plan de l'ingénierie**, la phase unique de J supprime la classe de
  reçus de sonde et de retour arrière qui a fermé plusieurs pilotes.
- **Risques :**
    - J peut échouer là où l'eau est loin ;
    - son projecteur doit être validé contre l'oracle canonique ;
    - son coût attendu est d'environ deux fois celui de P1.3 par décision.

## Individuals / axes concerned

I3. Axes : AXIS-ARCH, AXIS-ACTION. Méthode de recherche.

## Date and status

9 novembre 2026 : **ACCEPTÉ par le propriétaire.** Candidate-J devient le
dernier candidat autorisé de l'étape 1 à la fusion de cette ADR.
