# #133 M11 Stage12 : protocole de profilage de la persistance (préenregistré)

Date 2026-10-13. Constat H120 précédent : `docs/research/m11-stage12-issue133-h120-results-2026-10-13.fr.md` (commit `21b6127`), 120 vrais pas, 14 397 événements, 224,60s/338,38s et 17 956 864 octets SQLite, résultats identiques inter-Python. Les chiffres ne prouvent pas à eux seuls une complexité asymptotique.

**Mission** : isoler le coût réel sans modifier l'implémentation, les budgets, la physique ou le stockage. Le profiler externe `cProfile` observe une vie mortelle Stage12 sous M11 SQLite/indice P6-B6 pour **30 véritables pas au maximum** ; mêmes conditions/graines et coûts que H120, `w_C=0`, Python 3.11 et 3.12. Aucun nouveau cycle cognitif pour le profiler.

**Mesures avant exécution** : temps mural total et individuel par pas, taille SQLite à la fin, nombre de journal occurrences, état vital, nombre de h, journal SHA. Par `cProfile`, cumulated time et nombre d'appels des fonctions `SQLiteLifeLedger.audit`, `M11TransactionalMortal.run_step`, `_copy_private_runtime`, `capture_registered_current_state`, `_runtime_image`, `SQLiteLifeLedger.commit_generation`, `canonical_causal_bytes`, et `deepcopy`. Conserver trace brute `.prof` et JSON lisible, avec SHA source.

**Critères** : comparer entre Python sans changer l'état causal; ne jamais traiter le temps du profiler comme équivalent au temps non profilé; ne pas revendiquer de gain avec une seule mesure. Une optimisation n'est autorisée qu'après localisation des coûts et preuve de non-régression. La vérification exhaustive du journal, SQLite synchronous=FULL, WAL et interdiction de rejouer le passé restent obligatoires. Aucun H600 déclenché sans décision justifiée, et aucune validation opérateur présumée.
