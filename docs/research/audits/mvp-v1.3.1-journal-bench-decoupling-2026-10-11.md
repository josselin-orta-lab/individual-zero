# Audit préalable MVP v1.3.1 : journal exhaustif et indépendance de l'évaluation

**Base inspectée :** main `ab8573cf01ca310e49b178e506b47caa5954bc43` (11 octobre 2026).  
**État :** cartographie statique réelle, **pas** de validation de conformité ni de vérité physique.  
**Norme cible :** MVP v1.3.1 EN (FR traduction). Stage 9 reste SCIENTIFIC NO-GO.  
**PR existante :** #46 (livraison mémoire bornée) doit être réévaluée avant fusion : son intention initiale de *remplacer* la source technique complète contredit la nouvelle décision.

## Graphe actuel observé

```text
Stage 10 / Stage 11 -> Stage9 -> ... -> Stage4 -> Stage3
                                            |
                                     ScriptedStage2Runtime
                                            |
           +---------------------+----------+------------+
           |                     |                       |
      WorldBody              HashChainedJournal     create_oracle(world)
           |                     |                       |
       cognition          JournalViews              EvaluationBench
           |                /      \                    |
       Epi Memory       AutoSegmentCommit         EvaluationTrace
       SlowHistory       Stage10 PostCut              (external)
```

**Le sens de dépendance obligatoire est erroné au niveau du constructeur Stage2** : `src/lab/stage2_runtime.py` importe et instancie `create_oracle` et `EvaluationBench` sans option. `src/lab/safety_protocol.py` importe également `EvaluationBench`, ce qui impose son chargement via Stage2. Un appel au banc externe figure dans l'exécution d'une mort v1.3. Les autres Stages héritent du constructeur Stage2.

## Résultats classés

| Gravité | Chemin | Observé / action |
| --- | --- | --- |
| **P0** | `src/lab/stage2_runtime.py` import + constructeur | L'oracle et le banc sont créés systématiquement, même dans le mode mortel ; ajouter un chemin autonome sans leurs imports, sans leurs constructeurs et sans supprimer le journal. |
| **P0** | `src/lab/safety_protocol.py` | Dépendance Python directe à `EvaluationBench` dans un composant chargé par I0 ; passer à une interface technique minimale ou une importation de type uniquement. |
| **P0** | `stage2_runtime.py::_send_mortal_command` | `self.bench.count_lethal_transition` peut devenir une condition de clôture du pas ; déplacer toute mesure de mort externe hors de la transaction physique et interne du journal. |
| **P0** | v1.3.0 §5 et les PR de « mémoire bornée » | Décision de retrait du journal contraire au choix opérateur : la v1.3.1 annule cette obligation. Ne pas fusionner la PR #46 telle quelle. |
| **P1** | `src/lab/journal.py` | Déjà indépendant de l'oracle, mais seul `verify()` interne vérifie les événements vivants ; ajouter export/audit externe indépendant et tests de fraude. |
| **P1** | `src/lab/journal_views.py` | Les engagements autobiographiques sont des projections du journal réel par une allowlist versionnée ; préserver ces règles et contrôler les références hors exécution. |
| **P1** | `src/i0/modules/memory.py`, `src/lab/stage7_runtime.py` | La mémoire lit les événements autobiographiques filtrés, pas le ground truth. Ne pas remplacer le journal complet par une queue destructrice. |
| **P1** | `src/lab/consolidation_postcut_journal.py`, `consolidation_lived_evidence.py` | Stage 10 ancre cut et mises à jour post-coupure aux indices et empreintes du journal complet ; **conserver ces garanties** lors du découplage. |
| **P1** | `src/lab/consolidation_publication.py` | `SlowHistory` consolidé est distinct du journal technique ; attention aux fonctions restore après échec, à auditer séparément pour la mortalité. |
| **P1** | `src/lab/stage11_runtime.py` | Projections d'exploration et de causalité réelles ; préserver tous les événements vécus, et interdire les informations de `Oracle`. |
| **P1** | `src/lab/stage9_canonical_journal_audit.py` | Un audit historique existe mais importe Stage2 et donc Oracle/Bench ; construire une nouvelle voie stricte autonome sans ces imports. |
| **P1** | `src/lab/oracle.py` | Oracle n'importe pas de module cognitif : il lit `WorldBody.ground_truth()` avec `OracleCapability` ; protéger la lecture seule de toute fuite vers I0. |
| **P1** | `src/lab/bench.py` et `journal_views.EvaluationTrace` | Métriques et `oracle_read` déjà hors journal interne ; conserver indépendance et vérifier que l'absence du banc ne modifie ni état causal ni octets du journal. |
| **P2** | `src/lab/compact_life_custody.py`, anciens README | Les commentaires parlent de remplacer le journal complet ; requalifier en caches **optionnels**, sans purge de la source. |
| **P2** | Index des documents | Publier v1.3.1 comme cible et conserver v1.3.0 et v1.2.1 historiques. |

## Tests et preuves attendus

1. Processus autonome : bloquer `lab.oracle` et `lab.bench` dans les imports pendant l'exécution de l'I0 mortel ; preuve que journal et cognition vivent encore.
2. Comparaison de trajets autonomes et observés à commandes/graines fixes : mêmes décisions, états causaux et export canonique du journal interne.
3. Export canonique indépendant vérifié hors process ; falsification, omission, duplication, désordre, provenance impossible et cognition après mort rejetés.
4. Stage 10 : cut/rebase et postcut journal complets, intégration dans `SlowHistory`, sans perte du journal technique.
5. Stage 11 : transitions et attribution causale toujours auditées, sans ground truth importé dans la cognition.
6. Décès : conserver la transition mortelle, consigner une seule clôture terminale technique, refuser des cycles posthumes et ne jamais restaurer une vie.
7. Développement : campagne de 600 pas physiques réels avec export intégral vérifiable, seulement hypothèse de fonctionnement.
8. Exécuter tests ciblés puis CI Python 3.11 et 3.12, sans modifier le verdict scientifique Stage 9.

**Frontière de preuve :** les empreintes vérifient un historique *déclaré*. Sans source extérieure indépendante, elles ne prouvent pas la vérité physique de ces déclarations.

**Externalisation du journal :** explicitement hors périmètre. Toute migration future nécessite coût mesuré, sécurité, absence de perte et approbation opérateur.
