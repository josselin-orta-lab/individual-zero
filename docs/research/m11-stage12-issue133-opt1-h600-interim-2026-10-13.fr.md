# Issue #133 : audit indépendant H600 OPT1, première archive Python 3.12

**13 octobre 2026. Rapport intermédiaire, non conclusif tant que Python 3.11 n'a pas terminé.** Protocole préenregistré `docs/research/m11-stage12-issue133-opt1-h600-prereg-2026-10-13.fr.md`, code figé `fff436ab175c1bf1e3229d9f0e779570a47bda14`. [Actions #38405486588](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38405486588), job Python 3.12 SUCCESS, archive brute `11822258434` (ZIP 23 999 915 octets). Aucun nouveau code runtime n'a été utilisé pour l'audit ; un script standard Python a lu l'export canonique et SQLite en lecture seule.

## Mesures de la vie H600 (Python 3.12 uniquement)

| Monde | Pas | Épisodes clos | Références h publiées | Backlog | Temps hôte cumulé (s) | Taille SQLite (octets) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Stage12 mortal | 120 | 60 | 57 | 3 | 140,09 | 17 956 864 |
| | 240 | 120 | 116 | 4 | 571,66 | 33 239 040 |
| | 360 | 180 | 174 | 6 | 1 219,66 | 47 042 560 |
| | 480 | 240 | 234 | 6 | 2 152,15 | 65 249 280 |
| | 600 | 300 | 297 | **3** | **3 383,34** | **75 726 848** |

Le journal contient **58 639 événements au checkpoint H600**, hash `68d0acb8c299d9436024917c774c0c112686947cc9ecd5ad498e6425926bf18f` ; SHA-256 de l'export JSONL sans newline final `1a8d3f0a25463bd74c1c2020729ea4d4197a527ae0acc1363ecc8e8cd976419b`. L'export est exactement le préfixe des **58 656** occurrences SQL de la génération **601** après une véritable reprise froide. La base satisfait `PRAGMA integrity_check=ok`, le hash SHA-256 de `state_bytes`, `journal_count`, `journal_head` et `pending_intent=0`. Vie active, pas de retour à une génération historique.

Le recalcul indépendant SHA-256 a vérifié **chaque** événement et son précédent ; toutes les occurrences SQL du préfixe sont identiques octet par octet à l'export. Les 600 `step_closed` couvrent exactement 1 à 600. On observe 73 activations `h`, **438 checkpoints de passes** (6 par activation), 73 charges `index_maintenance` antérieures à l'activation, 73 retraits postérieurs, 297 références uniques consolidées et aucune publication de référence avant la fin de l'épisode ou après la coupure interdite. Pas de divergence dans les contrôles de publication ou de chaîne.

## Limite scientifique explicitement constatée

Les backlog calculés sur les bornes exactes sont : **pas 400 : 6**, **pas 520 : 2**, **pas 600 : 3**. La pente H400→H600 est **−3**, mais H520→H600 est **+1**. Le protocole préenregistré exigeait les **deux pentes non positives** pour déclarer la stabilité locale ; **ce critère n'est donc pas satisfait**, même si la file finale reste petite. La décision de stabilité est **NO-GO selon ce critère strict**, non une preuve d'un bug ou d'une divergence causale. Le backlog peut fluctuer par la granularité des lots et des épisodes ; cette explication doit être évaluée plutôt que présumée.

Le temps hôte par tranche de 120 pas augmente approximativement de **140 s**, puis **432 s**, **648 s**, **932 s**, et **1 231 s**. La croissance correspond à la répétition d'audits exhaustifs d'un journal append-only ; OPT1 réduit la constante, **pas l'ordre asymptotique**. H600 atteint ~56 minutes pour une seule vie sur ce runner. Ce coût peut être incompatible avec des campagnes massives ; aucune réduction de la preuve historique n'est autorisée sans nouvelle campagne de crash/corruption et préenregistrement.

Les valeurs `w_C=0`, 100 UC/pas, 600 UC/période et l'absence d'Oracle sont rapportées par `summary.json` ; les charges d'index sont vérifiées dans le journal. Une vérification exhaustive de **toutes** les lignes de comptabilité UC par période reste à produire, distincte des contrôles de facturation de `h`.

## Décision intermédiaire

**Intégrité causale et SQLite Python 3.12 : GO technique ciblé. Stabilité locale de backlog selon les deux fenêtres : NO-GO. Soutenabilité hôte H600 : coût croissant préoccupant.** La reproductibilité inter-Python et la décision finale attendent l'archive Python 3.11. Ne pas déclarer le MVP validé, fermer #133, fusionner #139/#140, modifier les budgets, le sommeil, la mortalité ou `w_C`.
