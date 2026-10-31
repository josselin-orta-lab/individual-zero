# I2 : cycle cognitif unifié, banc transactionnel synthétique (G2)

**31 octobre 2026. Source-only, non exécutable, non enregistré, aucun individu né et aucun GO scientifique.**

**Complément :** un mode v2 opt-in réunit aussi la revue Action Control dans
la **même** transaction de test. Voir [COGNITIVE_CONTROL_UNIFIED.md](COGNITIVE_CONTROL_UNIFIED.md).
Le présent document conserve la description normative du mode cognitif v1.

Source : `src/i2/modules/cognitive_cycle_fixture.py`. Vérifications : `tests/i2/test_cognitive_cycle_fixture.py`.

## Problème scientifique et technique

Les anciens bancs SQLite autonomes d'intention, Competition et Action Control ont été **supprimés**. Le seul banc transactionnel courant est `cognitive_cycle_fixture.py` v4 ; les fonctions nécessaires de sérialisation et de rejeu lui appartiennent. Il regroupe leurs calculs **synthétiques** dans une unique transaction locale, sans être le propriétaire d'une vie physique réelle.

## Contrat effectivement testé

1. Le fournisseur injecté `ObservationSource` doit attester une capture subjective déclarée, attachée à une seule identité **synthétique**, avant toute dépense. Le SHA-256 du contenu n'est ni signature ni attestation M11.
2. Sous `BEGIN IMMEDIATE`, le journal intégral est rejoué puis contrôlé contre les comptes, la chronologie et l'intention. Une capture périmée, étrangère, répétée ou sans origine subjective valable est rejetée. La même capture n'est pas consultée deux fois.
3. Si au moins une UC synthétique reste disponible, l'intention est consultée et **une UC de test** est débitée. Une demande cognitive valide mais impossible (`policy_rejected`) consomme cette UC et ne publie pas de frame.
4. Si la consultation réussit, les candidats sont reconstruits **uniquement** depuis la capture courante, sans cadeau d'une intention ni suppression des concurrents. Competition consulte un fournisseur distinct de valeurs de test et facture **tous les candidats du frame ou aucun**. Lorsque les UC restantes ne couvrent pas tout le frame, l'intention et son prix peuvent être publiés, mais Competition rend `UNFUNDED`, sans évaluation partielle ni conseil moteur. C'est une **hypothèse de politique**, pas une solution biologique calibrée.
5. Le même `COMMIT` écrit les deux dépenses synthétiques, le nouvel état du propriétaire, le frame temporaire, l'avis Competition et un événement canonique chaîné. Un abandon avant COMMIT annule **tout** le cycle dans cette base ; une confirmation perdue après COMMIT est résolue par `lookup(capture_ref)`, en lecture seule, sans refaire un calcul ni débiter une seconde fois.
6. `audit()` rejoue la politique d'intention, reconstruit les candidats, recalcule Competition à partir **des valeurs enregistrées** et rapproche tous les débits/états/références. Deux sessions concurrentes partagent la même transaction SQLite verrouillée ; les références répétées sont refusées.
7. La seule sortie est une **trace de conseil** `CycleReceipt` à `motor_authority=NONE`. Elle n'a aucun point d'entrée de commande, aucune autorisation d'Action Control et ne connaît ni le corps, ni un monde, ni la mortalité.

## Matrice de preuves et limites

| Propriété | Établie uniquement en banc | Encore non établie |
| --- | --- | --- |
| Atomicité | **Une même** transaction SQLite : débit UC synthétique, intention, frame, Competition et publication | Transaction du Scheduler réel / M11 / WorldBody |
| Rejouabilité | Journal local déterministe et haché, contrôles de cohérence et lecture après COMMIT | Chaîne M11 scellée à l'extérieur, résistance à la réécriture totale par un attaquant |
| Authenticité subjective | Port de vérification **injecté**, doublé dans les tests | Propriétaire Perception vivant et validation M11 indépendante |
| Coût cognitif | Coût d'interface fixe : 1 UC pour intention, 1 UC par candidat si lot entier payé | Débit réel du Scheduler, calibration des prix et refus de cycles insuffisamment financés |
| Valeurs | Source synthétique bornée et enregistrement avec références | TD/Q issus de l'expérience réellement vécue, crédit causal différé |
| Admission d'action | `motor_authority=NONE` même pour une suggestion positive | Competition réelle, Gatekeeper et Action Control indépendant, veto, monde physique |
| Autonomie | Aucun individu créé ou exécuté | Naissance, mortalité, sûreté de récupération, généralisation et preuve L3 |

**Précisions importantes :** `reopen()` inspecte une base de test ; ce n'est **pas une reprise d'une vie I2**. Le fournisseur de valeurs est supposé en lecture seule : un appel externe qui dépenserait irréversiblement des UC hors de la base ne deviendrait pas atomique par magie. La chaîne SHA-256 n'a pas de racine signée et un journal intégralement réécrit avec des hachages recalculés peut tromper le banc. Le rejeu ne réauthentifie pas les observations auprès d'un tiers, seulement leur cohérence avec les valeurs sauvées. Le coût O(N) du rejeu à chaque transaction est acceptable pour un **fixture**, pas nécessairement pour une vie.

Les anciens bancs séparés restent des références de test et **ne doivent pas être assemblés directement** pour construire un runtime I2. La revue Action Control existe maintenant aussi en **mode de recherche non moteur**,
avec la variante v2 transactionnelle documentée séparément. La prochaine étape
reste de produire un propriétaire de transaction M11 unique, rattaché à une
naissance indépendante et au vrai Scheduler. Le banc v2 n'est pas ce propriétaire.

## Vérifications et portes

Commande ciblée : `python -m unittest discover -s tests/i2 -p 'test_*.py' -v`.

G0 conservation I1 : **PARTIAL** (branche d'archive toujours non protégée et exposition durable des M11 originaux non attestée). G1 : **REVIEW_REQUIRED**. G2 : contrat transactionnel logiciel unifié en fixture. G3 : Scheduler/M11/mortalité/Action Control réels **NOT_ESTABLISHED**. G4-G6 : non commencées. I1 reste actif, I2 non enregistré. A1-C `NO_GO`, L3 `NOT_ESTABLISHED`, A2-R `NOT_EXECUTED (0/96)`.
