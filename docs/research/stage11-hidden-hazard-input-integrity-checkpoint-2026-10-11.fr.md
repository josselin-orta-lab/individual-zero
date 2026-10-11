# Stage 11 : contrôles de dangers cachés, budgets contraints et intégrité des interventions

**Date :** 11 octobre 2026. **Statut :** travaux implémentés, nouveau HEAD non validé par tests.  
**Autorité normative immuable :** `docs/architecture/reference/en/mvp-specification-v1.2.1.md`.  
**Stage 11 : EN COURS. Stage 9 : NO-GO scientifique. PR #25 : Draft, non fusionnée.**

## Source du contrôle et frontière de preuve

- **Dernier commit effectivement validé :** `2680283940c10c555238d55814146cb7a3c6129e`, [CI #38124468816](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38124468816) : **861/861 tests Python 3.12 PASS** et bootstrap smoke réussi. Cette réussite vérifie le rejet atomique d'un lot d'interventions externes et l'arrêt contrôlé du pas dans les cas testés. Elle **ne valide pas** les commits postérieurs.
- **`821ebff64a4bbc0ffeb0ca47b08648616fc0389c` :** [CI #38124663847](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38124663847) marquée failure en environ 3 secondes, avec `runner_id=0`, **aucune étape**, `steps=[]` et journaux de job indisponibles (`BlobNotFound`). Ce résultat n'exécute pas les tests. La cause exacte (budget, runner, plateforme ou politique) reste **non établie**.
- **Implémentations supplémentaires depuis :** correctif de test `f4f9e3c`, tests danger/budget `89bd71e`, vérification de marqueur `e25edb4` + test `2949d61`, validation canonique `f1d70d3` + test `525371f`, typage physique strict `0f67cab` + test `c226aa5`. Toutes sont **en attente de validation**.
- Aucune campagne Python 3.11 de référence, Golden ou held-out scientifique n'a été exécutée durant cette reprise. La visibilité du dépôt, les droits et protections de branches sont inchangés.

## Mécanismes implémentés, sans preuve d'exécution sur le HEAD actuel

1. `tests/test_stage11_scenario_payload_custody.py` vérifie désormais la position imposée **dans la capture Perception** du pas, et non après une éventuelle commande autonome du même pas. Cela sépare correctement intervention physique extérieure et action.
2. `tests/test_stage11_hidden_hazard_budget_snapshots.py` ajoute une comparaison monde contrôle / danger réellement caché à `t=3` sous trois profils UC versionnés : `(Planning,Exploration)=(0,0),(1,4),(4,4)`. La capture et les choix avant l'expérience sont comparés ; la vérité cachée du monde n'est utilisée que par Lab ; les refus de budget ne produisent aucune nouvelle sécurité prétendument prouvée. Deux profils incluent snapshot complet après `t=3`, exécution ultérieure et restauration de tous les états propriétaires. Un rejeu indépendant est exigé.
3. `InjectedScenario.restore_causal_state` vérifie que `rejected_event` et `next_index` pointent vers le même lot d'inputs rejeté : le curseur doit viser la **première entrée programmée** de ce `t_monde`. Un marqueur incompatible est rejeté avant toute mutation. Un test vérifie le refus de plusieurs combinaisons corrompues et le round-trip du marqueur authentique.
4. `InjectedScenario.__init__` refuse dès l'enregistrement un programme qu'il serait impossible de journaliser canoniquement : pas simulé strictement positif et entier, séquence entière non négative, opération non vide, payload mapping dont la représentation complète satisfait `canonical_causal_bytes`. Les NaN, infinis, ensembles, clés causales invalides et types non pris en charge sont rejetés **avant** `Scheduler.open_step`. Les opérations et positions *canoniquement encodables mais sémantiquement invalides* restent traitées au moment de l'application par le protocole de rejet externe, afin de tracer leur réception et leur refus.
5. `WorldBody.apply_scenario_event` refuse les positions dont `x,y` ne sont pas exactement des entiers, ainsi que les indicateurs `active` de zones dangereuses/létales qui ne sont pas littéralement booléens. En particulier `"false"` ne doit plus être interprété comme activation `True`. Un test vérifie les refus sans mutation du monde, les suppressions réellement demandées par `False`, et le fail-stop du runtime pour un input canonique mais mal typé.

## Protocoles consignés avant leurs correctifs/tests

- `docs/research/stage11-external-scenario-payload-custody-protocol.en.md` : admission canonique et propriété des payloads.
- `docs/research/stage11-external-input-atomic-step-open-protocol.en.md` : cohérence du marqueur et curseur de branche arrêtée.
- `docs/research/stage11-hidden-hazard-low-budget-snapshots-protocol.en.md` : danger physiquement caché, faible budget, snapshots, positions et drapeaux strictement typés.

Ces contrôles sont des **unit fixtures publiques**. Ils n'établissent aucune capacité de prévision d'un danger inconnu, aucune sécurité universelle ni aucune promotion scientifique du Stage 9.

## Exécution minimale recommandée dès qu'un environnement est disponible

Depuis le clone du SHA exact actuellement en tête de PR, avec les dépendances du dépôt installées et Python 3.12, lancer localement :

```bash
python -m unittest discover -s tests -p 'test_stage11_scenario_payload_custody.py' -v
python -m unittest discover -s tests -p 'test_stage11_external_input_atomicity.py' -v
python -m unittest discover -s tests -p 'test_stage11_scenario_snapshot_schedule.py' -v
python -m unittest discover -s tests -p 'test_stage11_hidden_hazard_budget_snapshots.py' -v
python -m unittest discover -s tests -p 'test_stage11_stale_route_safety.py' -v
python -m unittest discover -s tests -p 'test_stage11_strict_budget_and_snapshot.py' -v
python -m unittest discover -s tests -p 'test_stage2_runtime.py' -v
python -m unittest discover -s tests -p 'test_world_physics.py' -v
```

Si ces vérifications passent, examiner l'effet réel de ces modifications sur la suite unitaire complète, puis envisager **une seule** CI légère rattachée au SHA correct après confirmation de la disponibilité des minutes et des runners. Ne pas déclencher des runs à l'aveugle pour résoudre le problème d'absence de runner. Conserver l'échec #38124663847 comme trace, sans l'étiqueter « tests rouges ».

## Prochain verrou de recherche et limites

1. Étudier les changements danger présent → danger absent pendant plusieurs pas, puis l'interaction avec les modèles appris : une modification de vérité cachée ne signifie jamais automatiquement modification de connaissance de l'individu.
2. Approfondir les impasses sur plusieurs pas et les enveloppes UC nulles avec transition d'environnement, sans oracle caché ni attribution de mouvement externe à l'individu.
3. Traiter distinctement la conformité de rejeu dans l'environnement normatif **Python 3.11**, les Goldens, puis toute campagne scientifique nouvelle lorsque son protocole sera fixé.

**Ne pas clôturer Stage 11 sur la seule base de ces ajouts. Stage 9 reste NO-GO scientifique.**

## Addendum : danger activé puis retiré et deux snapshots (11 octobre 2026)

**SHA du dernier code modifié (non validé) :** `2ba0a347b665d307b184c2f04c81c7045cda55a5`. **Cette section est uniquement un état de développement, pas un résultat d'exécution.**

Le protocole `stage11-hidden-hazard-low-budget-snapshots-protocol.en.md` a été enrichi **avant le nouveau test**. `tests/test_stage11_hidden_hazard_budget_snapshots.py` inclut à présent `test_danger_appears_then_disappears_without_fabricated_knowledge` avec :

- deux interventions techniques du monde à `(3,2)`, activation d'une zone dangereuse au pas 3, désactivation au pas 5 ;
- un témoin recevant les mêmes dates d'intervention avec `active=False` pour les deux événements ;
- deux configurations à budget cognitif versionné : `(Planning UC, Exploration UC)=(0,0)` et `(4,4)` ;
- comparaison des décisions et captures **avant l'activation**, sans imposer l'identité des choix une fois les conséquences physiques possiblement divergentes ;
- vérification au pas 4 que seul le monde exposé possède encore la zone dangereuse, puis au pas 5 que les deux mondes en sont dépourvus ;
- deux snapshots périodiques complets sur le monde exposé, aux frontières des pas 4 et 5, restauration des états de **tous les propriétaires causaux** (y compris l'état du programme externe), journal append-only et hachages vérifiés ;
- réexécution indépendante des six pas avec **exactement le même calendrier de snapshots** : les prises de snapshots sont elles-mêmes des événements techniques, de sorte que les omettre dans une réexécution empêcherait toute comparaison honnête des octets du journal.

Le test ne prétend jamais que le retrait d'un danger du monde produit spontanément une connaissance sûre chez l'individu. Toute observation de ses conséquences doit rester ancrée dans la Perception et le comportement réellement exécuté.

**À exécuter dès qu'un environnement local compatible est disponible :**

```bash
python -m unittest discover -s tests -p 'test_stage11_hidden_hazard_budget_snapshots.py' -v
python -m unittest discover -s tests -p 'test_stage11_multistep_unknown_danger_budget.py' -v
python -m unittest discover -s tests -p 'test_stage11_scenario_payload_custody.py' -v
python -m unittest discover -s tests -p 'test_stage11_external_input_atomicity.py' -v
python -m unittest discover -s tests -p 'test_stage11_scenario_snapshot_schedule.py' -v
```

**Limitation de validation inchangée :** le dépôt privé n'est pas accessible au clone Git depuis l'environnement local de cette session (résolution réseau indisponible), et GitHub Actions a précédemment retourné un échec de démarrage sans runner ni étape de test (exécution #38124663847). Aucun résultat de la suite indiquée ci-dessus ne doit être supposé. **Dernier PASS vérifié : 861/861 sur `2680283940c10c555238d55814146cb7a3c6129e` exclusivement.**

**Stage 11 EN COURS ; Stage 9 NO-GO scientifique ; PR #25 Draft, non fusionnée.**
