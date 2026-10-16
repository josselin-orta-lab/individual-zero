# A2.30-P : préenregistrement d'un modèle hors I0 de trajectoires à conséquences multiples et danger différé

**15 octobre 2026 ; préenregistré AVANT code P, exécutions ou lecture des résultats P.** Cette campagne poursuit A2.30-N/O à partir de la PR #188 (SHA `bfb830cbbd453f9d7b64d98e3c55edb7214c0899`, CI N/O vertes), sous une branche et une PR empilées distinctes. Autorisation de l'opérateur : poursuivre la campagne et évaluer le prédicteur **hors du runtime I0**, pas adopter un nouveau `EquipmentModel` ni changer la spécification normative `mvp-specification-v1.3.1.md`. A2.30 PARTIELLE, Stage12 PARTIAL, #110 OPEN.

## Question falsifiable

L'expérience N a établi un gain d'enveloppes empiriques de deltas sur 28 situations ordinaires, mais 20 violations d'intervalles numériques et 12 terminalités manquées dans des contextes cachés. Le candidat P conserve plutôt un **ensemble empirique de trajectoires conjointes** : pour chaque séquence de commandes candidate, l'ensemble des suites physiquement **déjà observées** de deltas corporels/position/inventaire, avec la **première étape terminale** (s'il y en a une). Contrairement à des bornes indépendantes par champ, une branche relie le delta de chaque variable, l'action temporelle et sa terminalité **dans la même exécution physique**. P ne produit **jamais** un état futur unique, une politique, une action, une probabilité calibrée ou une certification de sûreté.

- **P1 :** sur les familles de commandes et préconditions visibles déjà couvertes mais sur de nouvelles positions et nourritures, les traces physiques retenues correspondent à au moins une branche observée, pour leurs **11 deltas cumulés à chaque pas, la longueur réellement exécutée et la première terminalité**. Les éventuels échecs ID doivent être publiés.
- **P2 :** lorsqu'une issue terminale n'apparaît qu'au **troisième** pas derrière des préfixes non létaux, P conserve cette branche et son pas terminal. Un diagnostic fondé uniquement sur le **premier pas** ne peut attester cette temporalité. Cela ne prouve ni la causalité subjective ni la réalisation future de la branche.
- **P3 :** les variantes physiques cachées jamais entraînées (nouvelle intensité de dommage, mortalité à un autre pas, baisse corporelle intermédiaire) produisent des **branches non reconnues** même pour une clé visible connue. P doit les compter, conserver `unknown_hidden_risk` ou `observed_terminal_possible` selon ses seules données d'entraînement, et ne jamais déclarer `safe`.
- **P4 :** séquence de commande inconnue ou obstacle visible hors contexte prénatal = **abstention**. Aucune vérité issue du futur, de l'Oracle ou de Bench ne doit entrer dans les prédictions d'I0.

## Préconditions observables et contrat du modèle

Une **clé initiale** est dérivée uniquement de `SimulationState` accessible AVANT la séquence et des commandes FIXÉES : `is_night`, primitive + paramètres exacts du **premier** acte, information locale observable correspondante (passabilité + créature pour se déplacer ; ressource visible + outil pour collecter ; nourriture détenue pour manger ; eau sous les pieds pour boire ; abri connu pour attendre/dormir), **et la séquence des commandes exactes fixée ex ante**. Les coordonnées et valeurs numériques corporelles ne sont pas des clés; les deltas partent bien de ces valeurs vécues pour permettre une évaluation. Le modèle ne consulte aucun `WorldBody`, `Oracle`, `Stage6Runtime`, `ActionControl` ou vrai danger latent pour prédire.

Pour chaque groupe connu, sortir uniquement `supported_branches` composées d'une suite d'états de **variation** (position, 4 variables corporelles, 5 inventaires), du pas terminal 1/2/3 ou `none`, et de l'effectif des **mondes physiques distincts** sous-jacents. Émettre `observed_terminal_possible` si et seulement si **au moins une branche terminale** a été physiquement constatée dans le groupe (le pas de première terminalité est conservé), `observed_harm_possible` pour dommage d'intégrité sans terminal dans le groupe, sinon `unknown_hidden_risk`. Ne jamais émettre `safe`; la répétition de mondes déterministes ne crée aucune calibration statistique.

Le modèle est fixé **après entraînement et avant création de tout monde de test**, ne s'ajuste pas, ne refuse pas a posteriori des cas gênants et **ne fait pas de rollout** sur une conséquence prédite. Le comparateur de premier pas est une observation empirique des sorties des **mêmes mondes d'entraînement**, mais ignore les suites (terminalité au premier pas seulement). Le contrôle trivial s'abstient toujours.

## Matrice de physique pure préenregistrée, 352 pas de laboratoire prévus

Utiliser `physical_fixture_config()` de A2.30-L comme base `WorldPhysicsConfig` (32×32, physique de mortalité inchangée). Initialiser le corps avec nourriture `30` ou `40`, intégrité `100`, eau `20`. Déclarer un coût de déplacement et de repos non nul, `food_decay_per_step=0.5`, `water_decay_per_step=0.2`, et neutraliser la récupération d'intégrité pendant le repos pour isoler les hazards. Chaque monde naît indépendant, exécute des commandes `PrimitiveCommand` via **`WorldBody.apply` effectivement appelée par `EquipmentCorpusRecorder.record_transition`**, et **cesse définitivement la séquence à la première transition terminale**. Un test physique de laboratoire n'est **pas** une nouvelle naissance I0.

Trois familles de **préfixes fixés avant chaque monde** :

1. **MOV** : `se_deplacer(east)`, `attendre`, `attendre`. Quatre mondes latents : `clear` (3 pas), zone létale cachée à l'est (terminal au pas 1), zone dangereuse à l'est avec dommage d'intégrité `40` à chaque pas (terminal au pas 3), et la même zone avec dommage `20` (3 pas non terminaux).
2. **EAT** : `collecter(berry_a)`, `manger(berry_a)`, `attendre` sur la case de la ressource. Quatre mondes latents : effet `berry_a` bénin (3 pas), effet caché d'intégrité `-7` (3 pas), effet caché `-100` (terminal au pas 2), et effet alimentaire caché de **gain 0** au lieu de 10 (3 pas). Espèce visible identique, effet caché différent.
3. **WAIT** : `attendre` × 3. Quatre mondes latents : physique de base (3 pas), décroissance de nourriture cachée `2.5` contre 0.5 (3 pas), décroissance d'eau cachée `2.2` contre 0.2 (3 pas), et danger de zone cachée **sur la case initiale** avec dommage d'intégrité `40` par pas (terminal au pas 3).

**Entraînement :** 3 familles ×4 mondes latents × nourriture {30,40} × positions {(2,2),(4,4)} = **48 mondes physiques distincts**, **132 pas réellement exécutés** (MOV 40, EAT 44, WAIT 48). Chaque exécution complète jusqu'à son éventuelle fin physique fournit UNE trace avec son état initial accessible, la séquence prédéclarée, les deltas cumulés de chaque état perçu après pas et le premier pas terminal.

**Test ID indépendant :** mêmes trois familles et quatre variantes, nourriture **{35,45}** et positions **{(5,5),(7,7)}**, soit **48 nouveaux mondes et 132 pas**. Ne pas utiliser ces cellules lors de l'apprentissage. Le groupe contextuel reste observable et identique par famille, mais positions/nourritures diffèrent.

**Test latent inédit (OOD) :** mêmes nourriture {35,45} et positions {(5,5),(7,7)}, mais **deux nouvelles variantes jamais dans le train** par famille :
- MOV : zone dangereuse dommage `30` (3 pas non terminaux) ou dommage `55` (terminal au pas 2) : **8 mondes, 20 pas**.
- EAT : `berry_a.integrity_delta=-30` (3 pas) ou gain alimentaire caché **25** au lieu de 10 (3 pas) : **8 mondes, 24 pas**.
- WAIT : décroissance alimentaire cachée `1.5` (3 pas) ou zone dangereuse initiale dommage `55` (terminal au pas 2) : **8 mondes, 20 pas**.
= **24 mondes OOD, 64 pas**.

**Test d'abstention :** nourriture {35,45} × positions {(5,5),(7,7)} ; MOV avec obstacle visible sur case est suivi de 2 attentes (4 mondes, 12 pas), ou séquence `se_deplacer(west)`, attendre, attendre jamais démontrée à l'entraînement (4 mondes, 12 pas). Total **8 mondes, 24 pas**.

**Totaux prévus : 48 mondes /132 pas d'entraînement + 80 mondes /220 pas de test = 128 mondes de laboratoire /352 transitions appliquées**, si la mortalité intervient exactement aux pas fixés. NORME : aucun pas postterminal. Si un autre nombre réel de transitions survient, ne pas réarranger les scénarios : l'exposer et marquer la campagne FAIL de conformité.

## Métriques et invalidations

Par famille/strate, compter : clés de contexte connues, nombre de branches distinctes, **couverture conjointe exacte** des deltas cumulés 11D et du pas terminal, échecs de branche malgré un groupe connu, faux **certificats** (doivent rester zéro), propositions `observed_terminal_possible` fondées sur les exemples d'entraînement, variation de pas terminal non vue, délai jusqu'au terminal, premier pas identifié comme non létal par le contrôle monoétape malgré terminal au pas 2/3, et abstentions des préfixes inconnus. Préserver **toutes** les traces d'entraînement/test avec SHA et identifiants de monde disjoints. Comparer les deux CI Python 3.11/3.12 mais ne pas compter ces duplications comme des naissances supplémentaires.

**Invalidation technique :** sélection de branches fondée sur la vérité du test, état latent dans clé observable, suite après mortalité, préenregistrement ignoré, même identifiant de monde pour train et test, fausse certification de sûreté, mauvais compte d'étapes, protocole modifié post hoc, ou import d'I0/Oracle/Bench dans le prédicteur. Le contrôle négatif doit falsifier un hash/terminal et montrer que l'audit le rejette.

**Limite obligatoire :** un ensemble d'issues déjà vues **n'est pas l'ensemble exhaustif des issues physiquement possibles**. Un danger caché qui n'a pas encore été observé est structurellement indécidable pour des observations aliasées. Le score de couverture conjointe ID n'est pas une garantie de sécurité; la politique conservatrice continue de ne jamais déclarer « sûr ». Une branche `observed_terminal_possible` n'est pas un jugement vécu d'I0. Tous les essais restent **strictement externes à I0**.

**Décision prévisionnelle :** PASS technique si la campagne et les contre-exemples sont reproductibles; P1/P2 soutenues uniquement à portée bornée si elles passent leurs témoins; P3 conservée même si le modèle peut flagger une possibilité terminale; **NO-GO d'intégration cognitive dans tous les cas** tant que causes cachées et faux négatifs ne sont pas mesurés sur données indépendantes adaptées, et tant qu'une décision opérateur normative n'a pas été demandée. Stage12 PARTIAL, #110 OPEN, PR de recherche DRAFT.
