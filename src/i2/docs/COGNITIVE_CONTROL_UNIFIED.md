# I2 : transaction unique cognition + revue Action Control (banc G2)

**31 octobre 2026 · PROPOSAL_ONLY, sans vie, commande ni admission motrice.**

Source : `src/i2/modules/cognitive_cycle_fixture.py`. Tests nouveaux :
`tests/i2/test_unified_control_cycle.py`. La transaction SQLite de ce banc est
**synthétique** et **n'est pas** le WAL M11 ni le Scheduler UC d'un individu.

## Décision de conception

Plutôt que de créer un troisième stockage ou de relier deux bases indépendantes,
le banc `CognitiveCycleFixture` accepte désormais **deux ports de test
supplémentaires** : `current_source.verify_current()` et
`safety_source.check()`. Ces ports sont obligatoires ensemble ; s'ils sont
absents, le banc historique garde exactement son mode cognitif v1. Deux schémas
SQLite sont distingués (`...-v1` et `...-v2`) et `reopen` refuse de changer de
mode silencieusement. Aucune migration ou promotion d'un journal v1 en v2
n'est implicite.

En mode v2, sous **un seul** `BEGIN IMMEDIATE` et `COMMIT` :

1. Rejouer et contrôler les événements, le compte UC et l'état intentionnel
   d'une **vie synthétique de test**. Refuser capture étrangère, périmée ou
   déjà consommée.
2. Vérifier la source subjective via un port externe *simulé*, puis débiter
   l'unique compte SQLite pour la consultation d'intention (1 UC de test).
3. Reconstruire exclusivement les candidats visibles de la capture ; évaluer
   tous les candidats et facturer leur lot synthétique, ou abstention.
4. En présence d'une suggestion Competition unique, demander une nouvelle
   attestation *simulée* du contexte courant, débiter **le même compte SQLite**
   pour la revue Action Control (1 UC de test) et recueillir le veto depuis un
   **port de sécurité distinct**. Ne pas inventer de commande ni de permis.
   Sans conseil ou sans solde, la revue reste `NO_ADVICE` ou `UNFUNDED`, sans
   charge de sécurité et sans passage de veto.
5. Vérifier une seconde fois le contexte *avant publication*, puis inscrire
   ensemble l'état d'intention, l'avis Competition, les deux reçus de revue,
   le verdict de sécurité, tous les coûts et le chaînage local de l'événement.
   Le `COMMIT` rend l'ensemble visible, jamais un état partiel.

Les fautes injectées après chaque débit et après le veto provoquent un rollback
intégral **local**. Si la confirmation de `COMMIT` est perdue, `lookup` en
lecture seule restitue l'enregistrement sans nouveau débit, et deux sessions
concurrentes ne peuvent pas consommer deux fois la même capture. L'audit
rejoue les politiques depuis le journal, contrôle les coûts et l'état ; il ne
reconsulte **pas** des sources externes pour réécrire l'histoire.

## Convention de sortie non motrice

`CycleReceipt.suggested_candidate_ref` demeure exclusivement la proposition
Competition, même lorsque la revue renvoie un veto. Le champ distinct
`control_suggested_candidate_ref` est `None` si le veto s'applique, si le
conseil est absent ou si la revue n'est pas financée.

**Tous** les reçus, même `REVIEWED_NOT_ADMITTED`, portent
`motor_authority=NONE`. Aucun API de commande, token de permission, Action
Control vivant, accès au WorldBody ou admission physique n'est installé.
La seconde vérification de fraîcheur ne suffit pas à bloquer le monde réel
*après* `COMMIT` ; seul un futur propriétaire moteur atomiquement responsable
pourra éventuellement admettre une action.

## Limites de preuve

| Propriété | Dans ce banc | Non démontrée |
| --- | --- | --- |
| Compte UC partagé | Un solde **synthétique** pour intention, Competition et revue | Prix UC du véritable Scheduler et facturation vécue |
| Atomicité | Transaction SQLite unique, journal, rejeu et pannes | COMMIT complet du propriétaire M11/WorldBody |
| Identité / sécurité | Ports obligatoires et liaison des références et reçus de test | Provenance M11 signée, vie non terminale, authentification matérielle |
| Décision | Avis et veto sans privilège | Admission physique, sûreté après COMMIT, mortalité |
| Valeurs | Tableau de valeurs synthétiques fournies par un port | Apprentissage TD/Q issu du vécu et crédit différé |
| Chaîne d'audit | Hachages non signés et rejeu des règles, détection partielle | Résistance à la réécriture de toute la base / racine extérieure attestée |

Les résultats du banc ne prouvent ni apprentissage naturel, ni autonomie,
ni avantage sur I1, ni sortie de G3. Les évaluations complètes peuvent encore
rester `UNFUNDED` sous budget faible ; aucune allocation alternative de
l'étude #673 n'est devenue normative.

## Vérification

`python -m unittest discover -s tests/i2 -p 'test_*.py' -v`

Les tests nouveaux comprennent financement exact et insuffisant, veto,
préservation du mode v1, identités étrangères, tentative de reprise dans le
mauvais mode, péremption, double traitement concurrent, pertes avant/après
COMMIT, corruption d'un reçu ou d'un solde et audit sans rappel externe.
La CI ciblée Python 3.11/3.12 sur le SHA de la PR est nécessaire avant fusion.

**G0 archive I1 : PARTIAL ; G1 : REVIEW_REQUIRED ; G2 : banc amélioré ;
G3 vrai M11/Scheduler/WorldBody : NOT_ESTABLISHED ; G4-G6 : NOT_STARTED.**
I1 actif, I2 non enregistré et non exécutable ; A1-C NO_GO et L3 NOT_ESTABLISHED.
