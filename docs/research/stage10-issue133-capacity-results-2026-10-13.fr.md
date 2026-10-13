# Issue #133 : résultats factoriels reproductibles, 3/6 passes × lots 3/6 (13 octobre 2026)

## Provenance et protocole

- Baseline `main` : `040f49832f6861edfbb606203b5446ffa633052d`; PR #139 restée expérimentale.
- Préenregistrement de la comparaison **avant implémentation** : `docs/research/stage10-issue133-capacity-ceiling-prereg-2026-10-13.fr.md`, commit `655638cbe4cf1c7c5a579d26a8748521c238e900`.
- Source des **huit exécutions** : `82eedf0117e4e4b9766cd91f21d5e5e3de32d62f`, quatre bras × Python 3.11 et 3.12. [Stage12 Actions 38356427207](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38356427207) SUCCESS et [CI rapide 38356427140](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38356427140) SUCCESS. Les artefacts `11793375610` (3.11) et `11793240676` (3.12) sont archivés.
- **Attention à la traçabilité** : le champ `preregistration` de `index.json` produit par le runner hérité pointe encore vers l'étude antérieure « 1 vs 3 passes ». Il s'agit d'une erreur de *métadonnée*, non d'une modification des conditions expérimentales. La véritable préinscription antérieure à l'implémentation est le commit et le chemin indiqués ci-dessus ; conserver les ZIP originaux tels quels et corriger explicitement cette métadonnée lors des prochaines exécutions.
- Même monde `reference_untrained`, eau 20, mêmes paramètres P-42 (100 UC par pas de sommeil, 600 par période, `episode_scan=1`), `w_C=0`, sélecteur incrémental déjà intégré, priorité inchangée, 240 commandes physiques maximales par vie. La politique d'état de veille/sommeil est numériquement identique entre bras ; seuls le plafond de passes/par pas et le nombre maximal d'épisodes par lot changent.
- Reproduction inter-Python **octet pour octet** des journaux `canonical.jsonl` et `life.wal`, par bras. Deux interpréteurs ne sont **pas** deux échantillons indépendants de trajectoires physiques : l'évaluation scientifique demeure exploratoire sur un monde fixe.

## Comptabilité validée hors du runtime

Un inspecteur indépendant, ne démarrant ni I0, ni l'Oracle ni le Bench, a vérifié les 8 chaînes causales événement par événement (NFC, sérialisation canonique, SHA-256 de chaque maillon, identifiants uniques et tail), l'égalité WAL/export, les cut préalables aux épisodes publiés, l'absence de duplication, **six checkpoints ordonnés par chaque h**, au plus un h par pas physique et les reçus P-42 de chaque pas. Pas d'incohérence détectée, ni dépassement des budgets 100 UC/pas ou 600 UC/période.

| Indicateur par vie de 240 pas | P3-B3 | P6-B3 | P3-B6 | P6-B6 |
| --- | ---: | ---: | ---: | ---: |
| Épisodes fermés / éligibles en fin de vie | 119 | 119 | 119 | 119 |
| Épisodes publiés dans h | 47 | 77 | 86 | **116** |
| Épisodes éligibles en attente | 72 | 42 | 33 | **3** |
| Publications atomiques h | 16 | 26 | 15 | 25 |
| Checkpoints sémantiques validés | 99 | 156 | 90 | 150 |
| Passes maximales réellement vues par pas | 3 | 6 | 3 | 6 |
| UC P-42 totales payées | 1 967 | 3 011 | 2 311 | 3 416 |
| UC de scan (épisodes rescanés, payés) | 1 032 | 1 551 | 914 | 1 452 |
| UC sémantiques et autres opérations | 935 | 1 460 | 1 397 | 1 964 |
| UC par épisode publié | 41,85 | 39,10 | **26,87** | 29,45 |
| Pas avec UC P-42 > 0 | 41 | 41 | 41 | 41 |
| Maximum UC/pas et UC/période observé | 100/100 | 100/100 | 100/100 | 100/100 |
| Reports facturés ou refus explicites | 9 | 16 | 12 | 17 |
| Âge moyen du backlog, en pas | 73 | 43 | 34 | **4** |
| P90 de l'âge du backlog, en pas | 129,8 | 75,8 | 59,6 | **5,6** |
| `dormir` / `se_deplacer` appliqués | 96 / 144 | 96 / 144 | 96 / 144 | 96 / 144 |

### Trajectoire par fenêtre de 80 pas

| Bras | Épisodes consolidés pas 1–80 | 81–160 | 161–240 | Δ backlog 161–240 |
| --- | ---: | ---: | ---: | ---: |
| P3-B3 | 14 | 15 | 18 | +22 |
| P6-B3 | 32 | 18 | 27 | +13 |
| P3-B6 | 26 | 18 | 42 | −2 |
| P6-B6 | 34 | 30 | **52** | **−12** |

Chaque fenêtre crée respectivement 39, 40 et 40 épisodes. Les deux configurations avec lots de 6 traitent davantage d'épisodes que les lots de 3. P6-B6 atteint **116/119 = 97,5 %** des épisodes créés après 240 pas, avec un backlog de 3 ; il absorbe davantage d'épisodes qu'il n'en reçoit sur la dernière fenêtre (52 contre 40). P3-B6 a également une pente finale légèrement négative (−2), sans encore résorber son stock de 33.

La consommation totale augmente avec la capacité, mais P3-B6 est le bras le plus efficace en UC par épisode consolidé **sur cette trajectoire**. P6-B6 est le meilleur en résorption de backlog et âge d'attente. Le choix relève de l'objectif scientifique explicite, et non du seul maximum de consolidations.

## Invariants, classification et limites

**Conforme dans les scénarios testés** : production physique identique, pas de veille supplémentaire affamée dans ce monde, h atomique vérifié à six checkpoints, budgets appliqués, reports explicites, journal et WAL intègres, reproduction 3.11/3.12 exacte, `w_C=0`.

**Limitation conceptuelle persistante** : le coût des scans du registre complet reste O(N) par sélection, y compris épisodes déjà publiés. À plus de 240 pas, ce coût pourrait dépasser le gain de capacité : une pente négative sur les derniers 80 pas **n'est pas une preuve de stabilité à long terme**.

**Preuves non fournies** : mondes held-out, comportement sous besoins vitaux urgents/équipement différent, vie >240 pas, qualité cognitive de h, restauration crash-atomicité M11 Stage12, conditions à budget P-42 abaissé ou changement de politique de sommeil. Aucun changement normatif du MVP v1.3.1 ni activation générale de P6-B6 n'est justifié par ces seules données.

**Décision** : **VALIDÉ TECHNIQUEMENT POUR CETTE CAMPAGNE, HYPOTHÈSE SCIENTIFIQUE LOCALE SOUTENUE, SOUTENABILITÉ DURABLE EN ATTENTE**. #133 doit rester ouverte avant une campagne de vieillissement préenregistrée, analyses supplémentaires et validation opérateur.
