# Stage 12 / issue #110 : A2.22, garde perceptive durable après crash brutal

**Préenregistrement du 14 octobre 2026, avant tout code A2.22.** Référence de départ : `main c45ed803f551188666577a430c04b97d9b9c769f`, A2.21 intégré, MVP v1.3.1 inchangé, Stage12 **PARTIAL** et issue #110 **OPEN**. Campagne technique externalisée, non promue dans la cognition.

## Question et découpage

A2.21 a montré qu'une garde des captures indépendante du candidat détecte des falsifications rechaînées **tant que la garde elle-même reste fiable**. A2.22 teste une garde dans un processus distinct, avec sa **propre base SQLite WAL / synchronous=FULL** et des redémarrages réels après `os._exit`. Le registre de révision reste un autre fichier, distinct de la base. Il s'agit d'un **banc de garde externe**, **pas du WAL M-11 d'I0** : le vrai système a déjà son coordinateur SQLite transactionnel, un propriétaire du journal et une clôture irréversible de l'individu. Aucun deuxième propriétaire d'I0 ne sera créé.

Une garde peut vérifier la continuité des captures et les conserver durablement sans certifier la cause physique. Une empreinte SHA n'est ni une signature d'origine ni une vérité épistémique. SQLite FULL protège certains cas de crash de processus, non une panne de support de stockage ou un adversaire ayant les droits d'écriture sur tous les fichiers.

## Matrice fixée avant instrumentation

**Quatre seeds 131–134, 2 causalités initiales, 2 suites physiques, 6 frontières de crash**, soit **96 mondes `WorldBody` distincts et 192 vraies transitions `WorldBody.apply`**. Deux commandes réellement appliquées par monde : déplacement east vers l'eau, puis `attendre`. Causalité initiale normale ou commande inhibée suivie d'un `set_position` extérieur confondant ; seconde attente immobile ou suivie d'un déplacement externe perceptible. `GoalAgencyService` réel émet `self` au premier jugement dans les deux causes appariées ; le dossier transmis au gardien contient **uniquement** un identifiant opaque de vie, les trois captures de première personne, et le jugement authentique. Les effets physiques restent **seulement** du côté de l'auditeur externe. Les variantes 3.11/3.12 répliquent les mêmes graines et ne doublent pas les observations.

L'observateur prépare d'abord une base vierge pour chaque vie. Un **nouveau processus** distinct ouvre la base de garde et exécute une intention durable, puis une transaction distincte de scellement. Après son exit brutal, un **autre processus froid** relit la base et vérifie le reçu, sans reconstruire d'état cognitif ni rejouer de commande physique. La copie candidate peut être écrite uniquement après le commit du scellement, sauf une injection expressément **incorrecte** visant à vérifier le refus de publication prématurée.

Six points, 16 essais physiques chacun :
- `pre_intent` : crash avant insertion de l'intention, état de naissance vierge, aucune preuve publiée.
- `after_intent` : intention durable sans scellement ; état incertain et refus.
- `after_premature_candidate` : écrit et fsync un candidat **à tort**, puis crash avec intention pendante ; tout lecteur doit refuser ce candidat malgré sa présence.
- `before_seal_commit` : interruption brutale dans une transaction SQLite portant le reçu, avant COMMIT ; intention durable, aucun scellement valide.
- `after_seal_commit` : reçu durable committé, sans accusé de fin ni fichier candidat ; l'auditeur peut vérifier le reçu, mais ne doit pas fabriquer de publication candidate.
- `after_ack` : reçu durable et candidat publié après commit ; acceptation seulement après audit froid des sources et des références.

**Attendus stricts :** 16 vies `fresh`, 48 `pending`, 32 `sealed` ; **16** candidats authentiquement recevables (`after_ack`) ; **16** candidats prématurés présents **mais refusés** ; aucun reçu `sealed` lorsque le crash intervient avant COMMIT ; 0 vie cognitive autonome, aucune reprise de l'ancien état d'I0. La corruption/rechaînage d'un candidat légitime après crash est refusée par la garde sans modifier sa source.

## Contrôle épistémique négatif

En dehors des 96 cas physiques, **4 expériences supplémentaires de remise au gardien d'un dossier falsifié *avant* le scellement** sont exécutées en réutilisant 4 captures physiques déjà générées (pas de nouveau monde, pas de nouvelle transition physique). Les modifications synthétiques du t3 et leurs hachages peuvent être acceptées par le gardien, qui n'a pas de canal de provenance perceptive authentifié. **Critère attendu : 4/4 acceptées par le gardien, 4/4 reconnues mensongères seulement par l'audit externe détenant les véritables captures**. Il s'agit d'une mise en évidence préenregistrée de la limite de confiance, non d'un succès de sécurité.

## Critères de validation T1–T7

T1 : comptage réel des mondes/transitions, égalité des trois captures entre causalités appariées, authentique premier `self`; les étiquettes `normal/confounded` ne sont pas transmises au processus gardien.

T2 : véritables interruptions `os._exit` dans 96 processus enfants, codes et frontières vérifiés ; audit froid effectué depuis 96 nouveaux processus et fichiers persistés, pas depuis les objets vivants. SQLite doit être en WAL et synchronous=FULL sur le writer ; lecture audit `mode=ro`.

T3 : états et candidats exactement comme attendus par point ; présence d'une intention pendante = fail closed, interdiction de prendre le plus ancien reçu comme autorisation de continuer I0.

T4 : comparaison de la source scellée avec le candidat sur identité, origine du jugement, captures et pas. Attaque par candidat entièrement rechaîné et modifié après ACK refusée, avec gardien inchangé.

T5 : contrôle d'input forgé pré-scellement 4/4 **accepté**, signalant qu'il manque encore une attestation authentique de Perception au moment de l'ingestion.

T6 : exécution sous Python 3.11 / 3.12 avec artefacts individualisés et résumé SHA du code ; ne pas adapter les critères à posteriori pour obtenir PASS.

T7 : ne modifier ni le contrat normatif v1.3.1, ni I0, ni Stage9/DC-05, ni M-11, ni le journal exhaustif, ni les UC, ni la mortalité, ni les seuils `2+2/12` du détecteur. Les résultats laboratoires ne créent **aucune** paire GA-06.

## Décision

Même en cas de T1–T7 conformes, **A2.22 est une épreuve adjacente d'atomicité de garde**, non une preuve que les preuves sont persistées dans la *même transaction* que les transitions causales et la mort dans M-11. Il faut encore spécifier comment la source des captures est attestée à la frontière originale et comment le propriétaire M-11 l'inscrirait atomiquement, sans double WAL ou source externe accessible à I0. La séparation **agence proximale de l'action / responsabilité distale de l'objectif** reste soumise à arbitrage explicite de l'opérateur avant toute modification du service de jugement. Statuts Stage12 PARTIAL, issue #110 OPEN, réception opérateur absente.
