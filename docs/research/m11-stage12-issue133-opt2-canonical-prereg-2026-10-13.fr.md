# M11 OPT2 : réduire le coût de la sérialisation causale, sans changer le journal

**Préenregistrement, 13 octobre 2026.** Nouvelle branche expérimentale `exp/m11-opt2-fast-canonical-audit-20261013`, créée depuis PR #140 commit `fb850a6c7efd7525ad1da681de491e4a8f6f1bd2`, empilée sur les PR #140 et #139. La norme MVP v1.3.1, `main`, le moteur physique, le sommeil, l'index P6-B6, `w_C=0` et les prix/limites P-42/P-43 restent intacts.

## Problème mesuré avant OPT2

Le H600 M11 OPT1 sous un seul scénario a produit **600 pas, 300 épisodes clos, 297 consolidés, 3 en attente, 58 639 événements**, et une génération durable 601 après reprise. Audits externes de l'archive Python 3.11 (`11825560855`) et Python 3.12 (`11822258434`) : tête SHA-256 **`68d0acb8c299d9436024917c774c0c112686947cc9ecd5ad498e6425926bf18f`** identique, `PRAGMA integrity_check=ok`, journal SQL/JSONL cohérent et sans doublon. Les temps observés H600 sont **5 375,61s (3.11)** et **3 383,34s (3.12)** sur des machines GitHub non contrôlées. Le backlog baisse de 3 épisodes dans la fenêtre H400→H600 mais augmente de 1 dans H520→H600 : le GO scientifique strict de stabilité locale reste refusé.

H30 avec cProfile OPT1 : `canonical_causal_bytes` **548 646 appels**, `_normalize` **8 196 237 appels**, `deepcopy` **7 483 300 appels**, `HashChainedJournal.verify` 120 appels / 30 pas (sur Python 3.12). Le temps CPU est dominé par normalisation du journal et copies de vues. Changer la fréquence des audits intégraux sans nouvelle preuve cryptographique est interdit.

## Hypothèse OPT2 préenregistrée

Deux **optimisations purement représentationnelles**, sans suppression de contrôle :
1. Dans `lab.determinism._normalize`, reconnaître prioritairement les vrais objets `dict`, `list`, `tuple`, `str`, `bool`, `int` et `float` Python via tests de type précis pour éviter le coût d'ABC `Mapping` et des formes génériques dans le chemin dominant. Garder inchangés l'encodage UTF-8/JSON, l'ordre, la normalisation NFC, le marquage `$f64`, la validation `NaN/inf`, les collisions Unicode et le traitement des sous-classes/fallback Mapping. Les données canoniques **doivent rester byte-identiques**.
2. Pour la vue interne immuable `_DetachedCausalEvent`, `JournalEntry.as_dict()` construit un **seul instantané détaché** du payload, au lieu de plusieurs deepcopies par itération de Mapping. Retourner des objets profondément détachés : aucune mutation de l'export ne doit altérer les entrées du journal. Les lectures publiques `__getitem__` restent défensives et le journal SHA est vérifié intégralement comme avant.

**Pas de cache cryptographique, pas de contrôle incremental seulement, pas d'utilisation de `PRAGMA data_version` comme substitut d'audit, pas de raccourci silencieux dans SQLiteLifeLedger.audit(), pas d'export supprimé.**

## Campagnes et critères de décision

- Avant d'interpréter un benchmark, tests unitaires d'équivalence : toutes primitives, floats +0/−0/non-finies, Unicode NFC, collisions de clés, Maps non-dict, listes/tuples, sous-classes, données malformées et mutation des exports profonds. Comparaison byte pour byte avec l'implémentation originale sur des corpus déterministes. SHA de chaîne et canonical JSONL identiques avant/après.
- Suite de tests journaux immuables et de corruption SQL, Stage12 WAL sans M11, M11 SQLite cold recovery, H30 P6-B6, 16 crashs `os._exit` et morts irréversibles, Python 3.11 et 3.12. Ne pas considérer un job PASS si le processus a changé de comportement.
- Benchmark **une première vie réelle de 30 pas sous cProfile** OPT2 sur chaque Python, depuis le même script H30 et même seed, puis comparaison avec OPT1 (30 pas, 3 570 événements, même hash `96d0dd8db2ec6b989e709d75b751aa5aea959d7b70468b71bd2c2dc0be2735b0`). **Ne pas relancer H600** avant la preuve H30 ; H120 à prévoir si les résultats sont prometteurs et les régressions passées.
- Mesurer temps hôte profilé, appels et cumul `_normalize`/`deepcopy`/`canonical_causal_bytes`, volume SQL, hashes d'état, pas, UC et taille de DB. Distinguer mesures uniques de gains statistiques.
- GO expérimental OPT2 seulement si aucune divergence causale ni perte d’intégrité/crash, et gain de temps observé sur les deux interpréteurs. Sinon NO-GO et conserver les rapports de FAIL. Toute modification de sécurité doit être testée au niveau de la reprise historique et du journal complet. La qualité scientifique du backlog H600 reste une issue séparée ; son critère H520→H600 n'est pas validé.

PR #140 reste brouillon, PR #139 ouverte, #133 ouverte ; ne fusionner aucune PR dans `main` sans validation opérateur.
