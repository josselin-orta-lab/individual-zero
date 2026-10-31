# I2 : revue Action Control conservée dans une transaction locale

**31 octobre 2026. Banc G2 de recherche, non moteur, non exécutable, sans naissance ni autorisation physique.**

Code : `src/i2/modules/action_control_custody_fixture.py` ; tests : `tests/i2/test_action_control_custody_fixture.py`. Réutilise la validation de l'avis Competition et la frontière `ActionControlBoundary` introduite par la PR #676. I1 reste le seul moteur actif.

## Problème et périmètre

`ActionControlBoundary` (#676) évite les rejouages dans **un processus**, mais ses ensembles de captures, frames et reçus sont perdus au redémarrage. Son `ledger.debit()` est un port externe, donc une erreur après débit peut laisser une facture sans revue publiée. Ce banc mesure ce qu'apporte une **transaction SQLite unique pour un compte UC entièrement synthétique et une revue Action Control**, avec résultat de sécurité et journal de contrôle.

**La transaction n'englobe pas** le débit du banc `CognitiveCycleFixture`, ni le vrai Scheduler. Ces deux prototypes ne doivent jamais être raccordés tels quels à une vie réelle en prétendant que leurs dépenses sont atomiques.

## Contrat implémenté et contrôlable

1. `create()` exige une base neuve, une identité de vie de test et deux ports techniques : `current_source.verify_current()` (capture courante, individu et avis déjà publiés) et `safety_source.check()` (verdict de veto). Les tests injectent des fournisseurs **synthétiques**. Ces ports doivent être **en lecture seule** : aucune transaction SQLite ne peut annuler leurs effets externes.
2. `_consistent_advice` refuse avant tout débit les candidats non canoniques, les avis non financés présentant un gagnant, les évaluations incomplètes et les valeurs non conformes. Le port « courant » doit répondre exactement `True` **avant** ouverture de la transaction.
3. Après `BEGIN IMMEDIATE`, le journal local entier est vérifié puis les étapes et captures déjà traitées sont rejetées. Une instance neuve et un processus redémarré consultent le **même** registre SQLite anti-rejeu.
4. `ActionControlBoundary` est appelé avec un reçu **créé par le registre UC synthétique local**, dont le débit et l'avis ont le **même COMMIT**. La réponse `UNFUNDED` n'interroge pas la sécurité ; `NO_ADVICE` n'impute aucune UC ; les avis payés peuvent être `VETOED` ou `REVIEWED_NOT_ADMITTED`.
5. Un deuxième contrôle du port « courant » est exigé avant publication pour constater une éventuelle obsolescence *pendant* la revue. Il ne verrouille **pas** le monde physique. Aucune action ne peut découler du résultat, même s'il était déclaré favorable.
6. Le `SafetyFinding` est lié au **reçu UC précis**, au candidat, à la vie, au frame et à la capture. Journal, réponse, débit et preuve déclarée sont conservés au même COMMIT. Le rejouage froid de l'audit reconstruit la revue via la politique pure, **sans appeler à nouveau** les autorités externes.
7. `lookup(capture_ref)` retrouve un résultat validé après perte de l'accusé de COMMIT. Il est en lecture seule, ne facture rien et ne constitue ni admission ni récupération M11.
8. Les fautes de test `after_control_debit`, `after_safety` et `before_commit` doivent annuler la publication et le débit **synthétique**. La faute `after_commit` signifie que le COMMIT a réussi et qu'aucun second calcul ne doit être tenté.

## Périmètre de preuve et limites

| Propriété | Banc logiciel | Non démontré |
|---|---|---|
| Anti-rejeu durable | Unicité et relecture sur **ce fichier SQLite** | Propriété d'un vrai individu et contrôles M11 après crash |
| Facturation | Une UC de contrôle de **test** si l'avis est éligible et le compte approvisionné | Budget/latence/coût réel du Scheduler |
| Veto | Contrôle strict de la forme et de la liaison d'un verdict fourni par un port | Vérité physique ou sécurité du corps, absence d'attaque de l'autorité externe |
| Intégrité | Journal SHA local, reprise déterministe, détection de corruptions partielles | Signature externe, protection contre la réécriture coordonnée de tous les événements et des hashes |
| Fraîcheur | Attestation externe répétée autour du COMMIT | Fraîcheur continue après COMMIT ou contrôle TOCTOU d'un véritable monde |
| Chaîne I2 complète | Une transaction de **revue séparée** | Atomicité *inter-bancs* intention, Competition, Action Control, WorldBody, mort |
| Exécution | **Aucune** commande, admission, naissance ou moteur ; `motor_authority=NONE` | Apprentissage autonome et survie mesurés |

**Interdiction explicite** : ne pas donner aux reçus `CustodyReviewReceipt` valeur de permis moteur, ne pas réutiliser la SQLite comme journal M11 ou le port synthétique comme preuve de vie. Ne pas promouvoir une sécurité « validée » parce que le booléen de test vaut `False`. Une protection contre le changement de capture après COMMIT exigerait de vérifier à nouveau dans un véritable propriétaire de monde **au moment d'une commande éventuelle**, étape encore interdite.

## Validation

`python -m unittest discover -s tests/i2 -p 'test_*.py' -v`

34 nouveaux tests de revue : base neuve, refus de vies étrangères et d'identités réutilisées, financement exact, absent ou insuffisant, veto, références inexactes, chronologie, réouverture, concurrence, corruption locale, contrôle avant COMMIT, confirmation perdue après COMMIT, absence d'exécution et indépendance des intentions. Le premier résultat local est **260 tests Python 3.13.5 PASS** pour la somme des tests reconstruits localement ; exiger la CI I2 officielle **3.11/3.12 au SHA exact** avant fusion.

**Portes :** G0 archive I1 encore non protégée ; G1 `REVIEW_REQUIRED` ; G2 prototype isolé ; G3 provenance, UC réels, chaîne complète M11, corps, mortalité et Action Control vivant `NOT_ESTABLISHED` ; G4-G6 non démarrées. I1 actif ; A1-C `NO_GO` ; L3 `NOT_ESTABLISHED` ; A2-R `NOT_EXECUTED (0/96)`.
