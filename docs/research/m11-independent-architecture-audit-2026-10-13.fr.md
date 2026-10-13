# Audit technique indépendant de M11 : frontière transactionnelle, mortalité et coût du journal

**Date : 13 octobre 2026. Périmètre :** `josselin-orta-lab/individual-zero`, référence normative `docs/architecture/reference/en/mvp-specification-v1.3.1.md` §2, §4, §5, §7 et M-11/M-12. Code audité : chaîne expérimentale PR #139 → PR #140 → PR #141, tête initiale de l'audit `7c53760d79b9cddde7589ee974df2cc67c035571`. Correction isolée dans PR brouillon #142, empilée sur #141. La norme, `main`, `w_C=0` et les limites UC restent inchangées.

## Périmètre vérifié

Lecture du coordinateur `src/lab/m11_transactional_mortal.py`, de `src/lab/sqlite_life_store.py`, de `src/lab/sqlite_runtime_custody.py`, du journal `src/lab/journal.py`, de la normalisation canonique et du vérificateur indépendant. Revue des suites `tests/test_sqlite_life_store.py`, `test_sqlite_corrupt_storage.py`, `test_m11_verified_anchor_optimization.py`, `test_m11_coordinated_crash_matrix.py`, `test_m11_stage12_hard_crash.py`, de la reproductibilité des vies H120/H600 et des profils H30/H600 précédemment publiés.

La présente revue de code et les suites ciblées ne constituent **pas** un audit externe exhaustif, une preuve mathématique d'atomicité, une simulation de corruption disque arbitraire ou une validation opérateur.

## A-01 : désaccord sémantique entre deux frontières de vérification (corrigé)

**Gravité : moyenne pour l'audit des archives ; non observé comme voie de résurrection dans le runtime intégré.**

Le journal vivant `HashChainedJournal.append` et l'auditeur externe refusent un `experiment_stopped` qui prétend `physical_death=True` ou `world_rewound=True`. Le validateur d'événements de bas niveau `_TerminalSequence.accept` dans `SQLiteLifeLedger` exigeait l'émetteur, le temps et une raison, **mais ne contrôlait pas ces deux indicateurs**. Un acteur passant directement un événement correctement haché à `commit_generation` pouvait le déclarer arrêté avec un contenu terminal contredisant le contrat de mortalité, même si le producteur journal normal refuse cette entrée. Un SHA-256 valide ne démontre pas la vérité sémantique d'une occurrence.

**Correction commit `af14bc6f70866f8ab5aea7a0937b6d6a5c50bb4b` :** contrôles stricts `physical_death is False` et `world_rewound is False` au niveau SQL. Test de régression `tests/test_m11_ledger_operator_terminal_semantics.py` : fabrique **directement** quatre reçus correctement hachés, sans traverser le journal vivant, pour vérifier : fausse mort refusée, fausse restauration refusée, absence des deux indicateurs refusée, arrêt opérateur sain accepté mais non reprenable. La première version du test traversait incorrectement `Journal.append`, lequel intercepte déjà ces événements ; correction du banc commit `f3f77e90a9360f5a23feb312f34d074421e41149`.

**Preuve CI** : [workflow #38433635217](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38433635217), **SUCCESS** sous Python 3.11 et 3.12 avec suite d'anti-falsification, ancien `test_sqlite_life_store.py`, corruptions SQL, attestations transactionnelles et vrais crashs Stage12 `os._exit`. Aucun fichier de physique ni de cognition modifié.

## A-02 : complexité croissante des audits exhaustifs (ouvert, priorité haute)

Deux audits de `SQLiteLifeLedger.audit()` restent exécutés par génération dans OPT1 ; ils recalculent chaque ancien hash causal et normalisent les anciennes entrées du journal. La capture `capture_registered_current_state` relit aussi `journal.verify()`. Le `_copy_private_runtime` clone les entrées du journal intégral. Dans le H600 OPT1 réel, **58 639 événements** pour 600 pas, archives identiques inter-Python, SQLite final ~75,7 Mo ; **3 383s en Python 3.12 et 5 376s en Python 3.11**, sur runners distincts. Le coût cumulé croît fortement avec le journal, sans modifier les UC de l'individu. Pour ce motif, **M11 n'est pas opérationnellement soutenable à horizon long dans ce banc**.

**Contraintes d'une optimisation future :** conserver une représentation append-only exhaustive, une chaîne SHA-256 intégralement auditable, des frontières de confiance explicites, aucun état antérieur réactivable, et la détection de corruption historique avant publication lorsque nécessaire. L'idée d'attestations ou segments cryptographiques amortis ne constitue pas par elle-même une preuve de conservation de l'invariant de corruption arbitraire. Une campagne propre, avec injections ciblées et benchmark apparié, doit précéder tout changement d'algorithme d'audit.

## A-03 : résultat de performance OPT2 contradictoire (ouvert, priorité moyenne)

PR #141 (OPT2) conserve des octets de journal identiques dans les vies H30 et H120 et passe les matrices de crashs, mais la campagne H120 non profilée observe **209,18s/223,61s** pour Python 3.11/3.12, contre **141,98s/135,05s** avec OPT1. Cela ne permet pas d'isoler l'effet causal de l'optimisation car les runners GitHub ne sont pas appariés. Le **critère préenregistré** de gain H120 n'est pas rempli ; **OPT2 doit rester NO-GO performance** et PR #141 en brouillon.

## A-04 : revue des garanties transactionnelles positives (prouvées sur scénarios testés)

- Les intentions sont durables et enregistrées **avant** la copie et l'exécution privée ; le candidat ne devient public qu'après `COMMIT`, validation SQL intégrale et égalité d'empreintes.
- Un état avec intention non résolue refuse `cold_recover` au lieu de restaurer la précédente génération active ; `seal_uncertain` préserve la preuve et classe `technical_halt`.
- Les six frontières `os._exit` sur un pas de Stage12, deux fenêtres autour de l'activation réelle `h`, la mort physique terminale et la reprise froide de la génération **courante seulement** ont été testées sous les deux Python. Ces tests valident les fenêtres injectées, **pas toutes les interruptions possibles du matériel**.
- SQLite `journal_mode=WAL`, `synchronous=FULL`, un verrou de writer `flock` par chemin canonique, un état propriétaire typé, et les occurrences du journal dans **la même transaction**. Les dossiers exportés restent intégralement vérifiables par un auditeur distinct.
- Les tests de corruption historique et de modification `state_hash` échouent en sécurité ; le ledger est empoisonné après une erreur de transaction.

**Limite importante :** les chaînes SHA-256 donnent une preuve d'intégrité interne, pas une authentification contre un adversaire capable de remplacer toute la DB et ses ancrages cryptographiques. Une preuve externe d'ancrage ou un modèle de menace plus fort est une autre décision architecturale, non incluse dans MVP v1.3.1.

## A-05 : résultats scientifiques séparés (ouvert)

Le H600 OPT1 a clôturé **300 épisodes** et en a consolidé **297** ; backlog final 3, mais pente H400→H600 **−3** et H520→H600 **+1**. Le critère de stabilité locale double fenêtre préenregistré **n'est pas satisfait**. Ce défaut statistique ne doit pas être effacé par les preuves d'atomicité M11. L'absence de plusieurs graines distinctes et la charge de stockage longue limitent les conclusions.

## Verdict de cette revue

**Sûreté transactionnelle : conforme aux scénarios ciblés après correctif A-01.**
**Passage à l'échelle : NO-GO opérationnel pour les campagnes longues à coût acceptable.**
**Stabilité scientifique du backlog selon protocole H600 : NO-GO local.**
**Validation du MVP : IN_PROGRESS, réception opérateur non acquise.**

Décisions recommandées : (1) garder la PR #142 en brouillon avec le correctif A-01 ; (2) concevoir séparément une optimisation du coût asymptotique des audits, sans compromis sur les preuves de corruption historique ; (3) évaluer l'intérêt d'un modèle d'ancrage externe *sans déplacer* le journal ni changer la norme ; (4) ne fusionner aucune des PR #139, #140, #141 ou #142 et ne pas fermer #133 sans l'acceptation explicite de l'opérateur.
