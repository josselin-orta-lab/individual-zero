# Issue #133 : défaillances in-process aux trois frontières h/index

Date : 13 octobre 2026. Code source testé : `b7138b87db21a95c44ebb7497d5c45c148edec45`.
[GitHub Actions #38382246256](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38382246256) : **SUCCESS**, six jobs verts sous Python 3.11 et 3.12, dont la matrice `os._exit`, les tests de validité du WAL externe et trois exceptions du runtime Stage10 par interpréteur. `w_C = 0`, budgets P-42 100/600, six passes et mode indexé opt-in inchangés.

## Matrice ciblée

| Injection après paiement index | Reçu de maintenance | h durable | Reçu de retrait | Résultat |
| --- | --- | --- | --- | --- |
| Exception avant publish | Présent | Absent | Absent | TECHNICAL_HALT |
| Exception avant acknowledge_published | Présent | Présent | Absent | TECHNICAL_HALT |
| Exception après écriture index_retired | Présent | Présent | Présent | TECHNICAL_HALT |

Les trois tests de `tests/test_stage10_index_soft_faults.py` utilisent réellement `Stage10Runtime` en mode mortel indexé et passent sous les deux Python. Ils vérifient avant et après : WorldBody inchangé à la frontière fautive, absence de nouvelle transition, journal SHA-256 interne cohérent, séquence de maintenance attendue, refus de `run_step()` suivant, et immutabilité du journal/WorldBody après ce refus. Les six tests `os._exit` distincts réexécutent les frontières durables en processus séparés avec WAL fsyncé et refus de reprise par l'auditeur.

**Portée** : preuve de non-continuation après erreur logicielle (et intégrité des préfixes WAL après crash) sur ces scénarios. La conservation du dernier état courant *atomiquement récupérable* après un crash reste NON VALIDÉE. SQLite M11 permet un commit d'une génération cohérente pour Stage10/11, mais `M11TransactionalMortal.birth` et `cold_recover` refusent explicitement `Stage12Runtime`. Brancher Stage12 tel quel constituerait un contournement des garanties. Le même audit documentaire indique que seul un état propriétaire complet journal + h + index + WorldBody + Scheduler, engagé en une génération durable commune, pourrait satisfaire M11.

**Aucune modification normative ni fusion** : #133 et PR #139 restent ouvertes pour validation opérateur après une campagne de reprise transactionnelle Stage12 réellement intégrée et preuves de la qualité de consolidation. La stabilité du backlog à 600 pas demeure une hypothèse locale, étayée par les expériences antérieures.
