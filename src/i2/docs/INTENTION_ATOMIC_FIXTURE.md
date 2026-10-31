# I2 : contrat SQLite local d'atomicité pour les intentions (G2, recherche)

**31 octobre 2026. Logiciel de banc d'essai, non moteur vivant, non M11.**

Source : `src/i2/modules/intention_atomic_fixture.py` ; tests :
`tests/i2/test_intention_atomic_fixture.py`. Cette tranche ne modifie pas
`IntentionIngress`, ne publie aucun nouveau point d'entrée de naissance et ne
change pas le registre des générations. I1 demeure le comparateur actif.

## Problème exact

Le prototype précédent (`intention_ingress.py`) reçoit une décision externe
d'observation et un débit UC par **deux ports distincts**. Une panne après le
second mais avant l'actualisation du propriétaire d'intentions peut laisser
un débit externe sans état publié. SQLite ne peut pas rendre atomique un
débit réalisé dans un autre processus/ledger simplement parce que son reçu
est transmis comme argument.

Le présent banc propose **une seule frontière de transaction** réunissant
un budget UC **synthétique**, un état d'intention sémantique pur et un journal
répétable. Il ne raccorde ni ne remplace les ports externes du moteur futur.

## Contrat local implémenté

1. `AtomicIntentionFixture.create(path, life_ref, synthetic_uc, observation_authority)`
   crée exclusivement une base neuve (pas d'écrasement), dont l'identité est
   explicitement une **vie synthétique de test**. Un port externe en lecture
   seule doit déclarer la capture acceptable ; les tests utilisent une simple
   liste blanche et **ne prouvent aucun événement M11**.
2. Une opération `open` ou `observe` rejette d'abord les formats invalides,
   vies étrangères et preuves absentes. Une autorité de provenance injectée
   doit répondre exactement `True` à la liaison par digest SHA-256.
3. Après `BEGIN IMMEDIATE`, le lecteur vérifie le journal local et son
   rejeu ; les captures consommées, hors chronologie ou réutilisées sont
   interdites. Un budget synthétique insuffisant refuse l'opération.
4. Le **même** `COMMIT` réduit le compte synthétique d'une UC, applique
   `IntentionContinuity.open/observe`, inscrit le résultat (y compris
   `policy_rejected`) et conserve l'image complète du propriétaire. Un refus
   cognitif réellement payé n'autorise aucun remboursement ni nouveau calcul
   sur la même capture.
5. Les enregistrements incluent l'entrée subjective, l'opération, le reçu
   synthétique, l'état obtenu et une chaîne SHA-256 **non signée**. Un audit
   en lecture seule **rejoue** chaque transition avec le module pur avant de
   comparer compte, chronologie, état et chaîne. Une écriture malformée ou une
   corruption observée ferme l'accès ; un attaquant pouvant réécrire toute la
   base et recalculer les hashes n'est **pas** arrêté par cette chaîne.
6. `reopen` ouvre uniquement une base existante et l'audite sans instancier
   de vie. `lookup(capture_ref)` permet de résoudre une confirmation de COMMIT
   perdue sans recommencer l'opération ni facturer une seconde fois.
7. Injections de faute réservées aux tests : après débit, après calcul de
   l'intention, avant COMMIT (ROLLBACK SQLite) et après COMMIT (confirmation
   perdue). Aucun test ne prétend simuler une panne physique d'alimentation.

## Matrice de responsabilité

| Propriété | Ce que le code atteste | Ce qui reste ouvert |
| --- | --- | --- |
| Débit + intention + journal locaux | Une transaction SQLite ACID ; `synchronous=FULL` par connexion écrivain | Intégration au vrai Scheduler et au vrai budget UC, hors de cette base |
| Observation | Liaison canonique et vérification d'un **port injecté** | Production M11 de la capture signée par le bon propriétaire |
| Reprise | Relecture déterministe de données SQLite synthétiques | Récupération froide d'une génération vivante M11 |
| Corruption | Détection de changements locaux non cohérents, validation stricte et rejeu | Preuve externe authentifiée et résistance à la réécriture de tous les hashes |
| Décision | `open`, `observe`, `suspended`, `expired`, `policy_rejected` | Competition, veto, Action Control, WorldBody, sécurité physique |
| Mortalité | Aucune vie réelle instanciée | Décès irréversible, terminaison et interdiction de réveil postmortem |
| Science | Tests de logiciel et de panne | Apprentissage naturel, survie, effet causal et réplication confirmatoire |

## Règle de transfert obligatoire

Le futur runtime devra soit **partager la même transaction durable** entre
le vrai debit UC, les propriétaires et M11, soit apporter un protocole de
préparation/commit suffisamment vérifiable pour empêcher les débits perdus et
les publications orphelines. Il est **interdit** de remplacer un reçu du
Scheduler par `FixtureReceipt`, de désactiver une protection, de rejouer une
vie morte ou de rebaptiser cette base « M11 ».

Ne pas importer le moteur `i1lab`, recopier Q/mémoire d'I1 ou forcer une
commande alimentaire. Ni les 56 vies historiques I1 ni une expérience
nouvelle ne sont utilisées comme connaissance initiale.

## Exécution reproductible

`python -m unittest discover -s tests/i2 -p 'test_*.py' -v`

Les tests de cette tranche comprennent des positifs, des injections de panne,
des corruptions et des rejets de provenance. L'inclusion des modules sources
n'active toujours pas I2. Le contrôle externe
`tools/assess_engine_proposal.py --generation I2 --json` doit continuer à
retourner `BLOCKED` (Lab et runtime vivants absents). Une CI Python 3.11/3.12
sur le commit exact doit être inspectée avant toute fusion.

**G1 REVIEW_REQUIRED ; G2 banc logiciel ; G3 intégration UC/M11 NOT_ESTABLISHED ;
G4–G6 fermées ; A1-C NO_GO ; A2-R 0/96.**
