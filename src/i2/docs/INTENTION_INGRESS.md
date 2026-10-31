# I2 : frontière de provenance et de débit UC pour les intentions

**31 octobre 2026. PROTOTYPE G2 / G3 logiciel partiel, non exécutable.**

Implémentation : `src/i2/modules/intention_ingress.py`. Tests :
`tests/i2/test_intention_ingress.py`. Contrat d'intention existant :
`src/i2/modules/intention_continuity.py`. Le registre conserve I1 actif.

## Ce qui est réellement assuré par ce code

L'entrée `IntentionIngress` exige deux autorités techniques injectées, sans
implantation par défaut :

- `ObservationAuthority.verify(life_ref, claim, digest)` vérifie **en amont**
  une projection subjective et les identifiants d'événements vécus. Le contrat
  traite son résultat uniquement s'il est exactement `True` ; sinon il refuse
  avant de consulter le propriétaire d'intention ou de demander des UC.
- `UCLedgerAuthority.debit(...)` doit réserver **effectivement** une UC à
  l'opération versionnée `i2_intention_consider` et fournir un `UCReceipt`
  unique, attaché à la vie, à la capture, au contenu canonique et au coût.
  Une preuve de dépense absente, dépareillée ou réutilisée interdit la
  consultation cognitive. Le plafond d'une UC est une proposition de coût
  technique, non une calibration scientifique.

Le SHA-256 calculé par `ObservationClaim.digest()` **lie des données** mais
n'est ni une signature ni une preuve de provenance. Les preuves subjectives
contenues dans la capture sont encore déclarées par l'appelant ; la validation
des sources réellement signées M11 reste à réaliser. Les doubles utilisés
par les tests ne sont pas des autorités M11 ou UC de production.

Après acceptation des deux attestations **externes**, la seule conséquence
logicielle est un appel à `IntentionContinuity.open` ou `.observe` : ouvrir,
conserver, suspendre, reprendre ou abandonner une intention. Aucune option
motrice, aucun accumulateur, gagnant, veto ou ordre physique n'est émis. Le
composant refuse les vies étrangères, captures anciennes ou déjà consommées,
contenus mal typés, preuves absentes de la déclaration subjective et reçus UC
réutilisés. Le débit, une fois accepté par l'autorité externe, n'est pas
annulé si la politique cognitive refuse ensuite l'intention : une consultation
cognitive payée peut échouer. La capture correspondante ne peut pas être
réessayée gratuitement dans ce propriétaire.

## Ce qui n'est PAS démontré

- Aucune autorité M11 I2 n'existe pour vérifier l'origine réelle de la capture,
  son propriétaire ou l'authenticité de la chaîne ; l'appelant doit les
  garantir avant d'utiliser l'interface dans un individu vivant.
- Aucune dépense UC du Scheduler d'une vraie vie I2 n'a été effectuée : le
  protocole `debit()` est un **port**, les tests utilisent un budget synthétique.
- Le passage atomique entre authentification, débit UC, mutation de
  l'intention et transaction durable n'est pas implémenté. Une panne après
  débit mais avant mutation sera à traiter par un futur contrat de commit
  et de reprise sûre, pas par remboursement ou résurrection.
- Pas de Lab I2 autonome, de M11, de commande, de corps, de Competition,
  d'Action Control, de naissance ou de comparaison I1/I2.
- Les décisions de succès de ce module ne prouvent aucune amélioration de
  survie ou apprentissage naturel.

## Vérifications

`python -m unittest discover -s tests/i2 -p 'test_*.py' -v`

Les tests ciblés incluent absence d'autorités, authenticité simulée positive
et négative, paiement simulé épuisé, mauvaise vie, provenance de l'évidence,
liaison par hash, usurpation du reçu, duplications, non-répétition après échec
cognitif payé, continuité/suspension/reprise et absence de pouvoir moteur.
Exiger une CI GitHub 3.11 + 3.12 **sur le SHA exact** avant fusion.

**Portes** : G1 `REVIEW_REQUIRED` ; G2 interface locale en progrès ; G3
provenance réelle/UC réelle/M11/vie `NOT_ESTABLISHED` ; G4-G6 fermées.
## Garde d'incertitude UC (G2, 31/10/2026)

L'entree reserve maintenant la capture dans un verrou de session **avant** d'appeler le port de debit externe. Si le debit leve une exception, retourne un recu malforme ou perd son accuse, la meme capture ne peut pas declencher un second debit dans cette instance. Les appels concurrents sont serialises jusque dans la consultation et la mutation de l'intention. L'inspection locale est egalement protegee contre une mutation concurrente. Tests cibles : timeout apres depense declaree, recu etranger apres depense, et deux threads tentant la meme capture.

Cette reservation en memoire n'est PAS une intention durable, un paiement M11 ni un protocole de resolution apres crash. Une erreur peut laisser une capture inutilisable alors que le debit reel n'a pas eu lieu : **fail-closed volontaire**, sans remboursement ni reexecution automatique. Une nouvelle instance perd l'historique de reservation ; le futur Scheduler/M11 devra apporter une idempotence persistante, un registre des tentatives et une consultation sure des recus. Aucune preuve G3 et aucun droit moteur.
