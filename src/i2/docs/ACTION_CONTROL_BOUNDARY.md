# I2 : frontière indépendante Action Control, sans admission motrice

**31 octobre 2026. Prototype G2, source-only, non enregistré et non exécutable.**

Source : `src/i2/modules/action_control_boundary.py`. Tests :
`tests/i2/test_action_control_boundary.py`. Contrats d'entrée existants :
`option_reconstruction.CandidateFrame` et `competition_preview.CompetitionAdvice`.
L'intégration à un individu et toute interface physique sont **INTERDITES** sans revue G1,
M11 authentifié, débit UC réel, propriétaire de la sécurité et contrat de mortalité.

## Rôle exact

`ActionControlBoundary.review(frame, advice)` est une **revue non motrice**.
Elle peut produire seulement `NO_ADVICE`, `UNFUNDED`, `VETOED` ou
`REVIEWED_NOT_ADMITTED`. Dans **tous** les cas, le résultat porte
`motor_authority="NONE"`. Aucun point d'entrée de commande, exécution, naissance,
création d'option motrice ou permission de contourner un veto n'existe. Même
`REVIEWED_NOT_ADMITTED` n'est **pas** une admission et ne doit jamais être accepté
comme un jeton d'Action Control par un exécuteur futur.

La fonction commence par vérifier la **cohérence de forme** de l'avis : frame,
capture et pas exacts ; ensemble complet de candidats évalués ; références de
reçus distinctes ; une valeur bornée reliée à chaque candidat et son reçu ;
justification de `ADVISORY_ONLY` par un **maximum strictement positif unique**.
Les statuts `NO_CANDIDATES` / `UNFUNDED` n'ont ni évaluation ni suggestion ;
les avis ambigus ou sans preuve positive ne déclenchent pas de contrôle payant.
Ces vérifications ne sont **pas** une authentification scientifique ou M11 des
valeurs et reçus externes.

## Séparation des propriétaires exigée

1. `CurrentCaptureAuthority.verify_current()` doit attester indépendamment que
   la vie n'est pas morte, que la capture est la **capture physique courante** et
   que les producteurs originels ont bien engagé leurs preuves, débits UC et
   résultats avant cette revue. Son retour doit être *exactement* `True`.
   **Ce port n'a pas encore de fournisseur réel I2.** Le digest SHA-256 d'une
   capture, même cohérent, n'est pas une signature M11.
2. Avant le veto, `ControlUCLedger.debit()` doit réaliser **un vrai débit** et
   livrer un `ControlReceipt` lié à la vie, au frame, à la capture, au digest, au
   candidat et à l'opération `i2_action_control_review`. L'unité UC proposée
   ici est une convention de test, **pas le tarif du Scheduler**. `None` donne
   `UNFUNDED`, sans consulter le service de sécurité.
3. `IndependentSafetyAuthority.check()` doit examiner le monde corporel
   **actuel**, les contraintes physiques et la sécurité et rendre un
   `SafetyFinding` avec veto booléen et provenance, relié également **au reçu UC
   exact**. Un veto `True` masque l'avis. Un veto `False` signifie seulement
   `REVIEWED_NOT_ADMITTED`, jamais une permission.

Tous les ports sont injectés et n'ont pas d'implémentation par défaut. Dans les
**tests seulement**, ils sont remplacés par des doubles synthétiques. Le module
n'a aucun chemin de secours vers `i1lab` ou un oracle du Lab.

## Pannes et rejouage

Un verrou réserve le pas, la capture et le frame **avant** le débit externe :
un refus tardif ou une confirmation incertaine n'autorise pas de seconde
consultation locale. Les reçus de contrôle déjà vus ne peuvent être réutilisés.
Mais **ces ensembles sont en mémoire et disparaissent au redémarrage**. De plus,
la vérification de fraîcheur, le débit et le veto ne sont **pas atomiques** entre
ports externes. Ils ne protègent donc ni contre une double dépense après crash,
ni contre un changement physique entre la vérification et une future admission.
Le modèle de reprise sûre reste à concevoir avec un journal M11 authentifié et
une frontière de commit unique. Aucune récupération d'une vie morte n'est permise.

## Vérifications falsifiables

`python -m unittest discover -s tests/i2 -p 'test_*.py' -v`

29 nouveaux tests testent l'absence de port moteur, l'avis valide mais non admis,
les vetos, le refus de financer un contrôle, les captures étrangères ou
périmées, les avis falsifiés, les valeurs/recus incomplets, le résultat de
sécurité délié du reçu payé, les pannes après dépense, le rejeu, deux appels
concurrents et l'absence de biais d'intention. Les tests isolés ne démontrent
pas de sécurité physique, d'apprentissage naturel ou de survie.

## Portes

- G0 I1 : archive source existante, branche encore non protégée.
- G1 : revue scientifique/architecturale `REVIEW_REQUIRED`.
- G2 : **frontière logicielle non motrice seulement**.
- G3 : Scheduler UC réel, authentification M11, veto physique indépendant,
  Action Control vivant, mortalité et reprise **NOT_ESTABLISHED**.
- G4-G6 : aucune nouvelle vie, protocole confirmatoire ni promotion.

**I1 seul actif ; I2 `PROPOSAL_ONLY`.** A1-C `NO_GO`, L3 `NOT_ESTABLISHED`,
A2-R `NOT_EXECUTED (0/96)`.
