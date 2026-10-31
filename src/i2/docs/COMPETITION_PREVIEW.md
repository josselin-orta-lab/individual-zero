# I2 : arbitrage Competition, prototype d'avis sans autorité motrice

**31 octobre 2026. G2 uniquement : composant source isolé, aucun moteur, aucune naissance et aucune preuve scientifique.**

Code : `src/i2/modules/competition_preview.py` ; tests : `tests/i2/test_competition_preview.py`. Ce composant reçoit uniquement des `CandidateFrame` produits depuis la perception courante par `option_reconstruction.py`. Il ne change ni `IntentionContinuity` ni le banc SQLite synthétique, et ne raccorde aucun WorldBody, Scheduler, M11 ou Action Control réel.

## Contrat du prototype

1. **Contexte canonique.** Un `CandidateFrame` doit contenir un identifiant de vie correspondant à la session, une capture physique nouvelle et des candidats canoniques, distincts, liés au digest de cette capture. Une capture ancienne, déjà évaluée ou provenant d'une autre vie est refusée. Le port indépendant `CandidateFrameAuthority.verify()` doit répondre exactement `True` **avant** tout débit. Son implémentation réelle et la signature des événements M11 sont absentes ; les tests utilisent un double volontairement permissif. Les autres contrôles portent seulement sur la forme et la cohérence.
2. **Budget indivisible par frame.** Un port *externe* `BatchUCLedger.debit_batch()` doit facturer, en un seul lot, **une UC proposée par candidat** et renvoyer un reçu distinct lié à la vie, au frame, au candidat et au digest. Si toutes les évaluations ne sont pas financées, le résultat est `UNFUNDED` et **aucun candidat n'est conseillé**. Les coûts sont des conventions de banc, non des UC du vrai Scheduler. Le port doit être réellement transactionnel avant toute intégration vivante.
3. **Évidence séparée.** Après validation de **tous** les reçus, un second port `SubjectiveEvidenceAuthority.evaluate_batch()` fournit une valeur entière bornée et une référence d'évidence pour chaque candidat payé. Une liste incomplète, réordonnée, mal attribuée ou mal typée est rejetée. Le module n'établit **pas** que cette évidence est réellement première personne : ce sera une obligation de son futur fournisseur.
4. **Arbitrage non moteur.** Une unique valeur strictement positive et supérieure à toutes les autres produit le statut `ADVISORY_ONLY` accompagné d'une simple référence de candidat. Une égalité au maximum produit `AMBIGUOUS`, des évaluations nulles ou négatives `NO_POSITIVE_EVIDENCE`, un frame vide `NO_CANDIDATES`. L'avis conserve les évaluations et leurs références de preuve pour permettre un réaudit, sans les transférer dans le frame physique suivant. Aucune règle `collecter → manger`, bonus d'intention, pseudo-Q ni avantage d'ordre lexical n'est ajouté. Le signe zéro et la borne de valeur sont des choix logiciels **à justifier avant calibration scientifique**.
5. **Sans privilège moteur.** `CompetitionAdvice` n'a ni commande, ni droit à l'action, ni score accumulé entre captures. `veto_preview()` peut masquer un avis, mais même lorsque son booléen simulé ne s'oppose pas à l'avis, le résultat est `NOT_ADMITTED` avec `motor_authority=NONE`. **Ceci n'est pas Action Control** ; seul un futur contrôle indépendant, qui réévalue le monde présent, peut admettre une action.
6. **Rejeu local borné.** Une session possède des ensembles de références vues et protège, par verrou local, une seule tentative par capture. Elle réserve la capture **avant** d'appeler le port UC : une panne ou un refus tardif ne crée pas de deuxième débit gratuit dans le même processus. **Ces ensembles ne survivent pas au crash** et ne peuvent remplacer un propriétaire M11 authentifié.

## Pourquoi cette hypothèse est falsifiable

L'obligation de traiter tous les concurrents supprime l'effet artificiel d'une option évaluée trois fois contre une autre une seule fois *dans ce prototype*. Mais un environnement UC faible avec de nombreuses possibilités peut produire beaucoup d'`UNFUNDED`, donc un **nouveau blocage comportemental**. Le mode tout-ou-rien est **une hypothèse architecturale**, pas une meilleure stratégie démontrée. Avant une vie I2, prévoir une comparaison contre un traitement partiel équitable sous budgets réalistes et vérifier les vrais producteurs de valeurs, les prix UC et les décisions d'Action Control. Le banc n'établit ni apprentissage efficace, ni autonomie, ni avantage sur I1.

## Sécurité des interfaces

- Un `CandidateFrame` et des reçus construits hors du système authentifié peuvent être **entièrement forgés**, malgré des hashes internes cohérents. Aucun lien M11 garanti.
- Le port `debit_batch()` peut échouer après une dépense réelle. L'état de non-rejeu n'étant pas durable, **ne pas brancher ce prototype à un vrai ledger** sans transaction, résolution des accusés perdus et reprise sûre.
- Le port d'évaluation est injecté et les tests utilisent une table synthétique de valeurs, non des Q appris. Il n'existe aucun oracle de toxicité ou de nutrition.
- Un booléen de veto de test n'est ni un véritable Gatekeeper, ni une admission d'Action Control. Aucune commande physique ou récompense ne sort du module.
- Une intention peut annoter un candidat, mais n'influence pas le score calculé par Competition ; tout futur apprentissage différé devra être attesté et testé séparément.

## Reproduction et portes

`python -m unittest discover -s tests/i2 -p 'test_*.py' -v`

La tranche ajoute **30 tests** au banc, avec évaluations complètes, budget insuffisant, abstention, égalités, plusieurs candidats et intentions, fausses preuves, double débit, concurrence et veto purement déclaratif. Exiger un résultat Python 3.11 et 3.12 sur **le SHA de PR**, avec `tools/assess_engine_proposal.py --generation I2 --json` toujours `BLOCKED` (Lab/runtime indépendants absents).

**G0 : archive source I1 créée mais non protégée. G1 : `REVIEW_REQUIRED`. G2 : prototype Competition isolé. G3 : vrai Scheduler/M11/Action Control non intégrés. G4–G6 : non commencées. I1 actif ; A1-C `NO_GO`, L3 `NOT_ESTABLISHED`, A2-R 0/96.**