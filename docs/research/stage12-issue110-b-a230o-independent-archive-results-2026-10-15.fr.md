# A2.30-O : vérification indépendante des scores N sur archives figées

**15 octobre 2026.** Protocole O préenregistré **après connaissance des résultats N mais avant le code de vérification**, commit `931af6960c4f69bba145746541e20b6b184a005b`. Code `13c4fd9a029789d5077118f7b2d6f3139e91a1ac`, tests adversariaux `22d2933b8e246ebdc90185f10d63d0a2baf63490`. [CI GitHub Actions #38727340539](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38727340539) : **SUCCESS Python 3.11 et Python 3.12**, résultats identiques.

## Provenance sans nouveau monde

L'auditeur télécharge **deux artefacts originaux A2.30-N** (`a230n-py3.11` et `a230n-py3.12`) du run #38726664498, code figé `d62a92d7f0a773a411de2e65ce2c2467be9efb48`. Les trois JSON sont rigoureusement **identiques octet à octet** entre les deux versions et leurs empreintes SHA-256 intégrales vérifiées :

- `a230n-training-manifest.json` : `948dc97de8ff6fc447ea5047699d99691892e3299108ee4a21c0cdd5f6232af1`.
- `a230n-heldout-physical-results.json` : `2c40322e5b4810ccdd088ec104172a07dc2bd53d32544055d1a84a58942c8947`.
- `a230n-summary.json` : `719978de013674e3370d9fd39f9f35726888469dfd62d41575b06570d1bd0c21`.

Sans importer le prédicteur original ni son runner, `audit_stage12_issue110_b_a230o_independent_scoring.py` reconstruit depuis les exemples archivés, avec une autre implémentation des fonctions, les 42 clés exactes et sept contextes abstraits, les deltas des 11 variables, les bornes de chaque groupe, les risques observés, les 62 résultats hors entraînement et toutes les métriques de chaque strate. Il refuse les identifiants de monde dupliqués, les collisions de vérité contradictoire dans l'entraînement, les nouvelles commandes fictivement connues, les SHA altérés, les intervalles fabriqués, les changements de terminalité et tout certificat de sûreté. Le test adversarial vérifie également une tentative de contamination entraînement/test.

| Compteur recalculé indépendant | Résultat |
|---|---:|
| Cas physiques archivés vérifiés | **62/62** |
| Intervalles disponibles | **54** |
| Table exacte disponible | **18** |
| Intervalles défaillants | **20** |
| Terminalités hors ensemble | **12** |
| Faux positifs du *proxy externe* « match exact = sûreté » | **18** |
| Certificats de sûreté émis par le prototype | **0** |
| Naissances ou pas physiques additionnels exécutés par O | **0** |

**Limite importante :** l'auditeur O valide la **cohérence interne et l'intégrité des traces enregistrées**, pas indépendamment la vérité de l'application historique de `WorldBody.apply` depuis des archives seules. L'exécution physique est celle du runner N, contrôlée par ses tests et par le code auditable. L'accord entre 3.11/3.12 ne fournit pas de graines physiques statistiquement nouvelles. Aucune preuve d'exactitude de conséquences cachées n'est inventée.

## Décision

**A2.30-N/O : PASS de reproductibilité technique, NO-GO pour intégration cognitive.** N1 (couverture empirique sur la strate ID) soutenue à portée étroite; N2 (abstention de certifier une sécurité non connue) préservée; N3 (vulnérabilité sous dangers cachés et dérive des effets) confirmée. Aucune comparaison de plans alimentaires vécus n'est ici effectuée. **A2.30 PARTIELLE ; Stage12 PARTIAL ; issue #110 OPEN, PR #188 DRAFT, pas de fusion.**
