# I2 : état de développement, 31 octobre 2026

**PROPOSAL ONLY / NOT REGISTERED / NOT EXECUTABLE / SCIENTIFIC GO NOT ESTABLISHED.**

- G0 I1 : source ancrée au commit `1e19f02db14b64a35f8bb014d69cc061f311002c` ; archive Git non protégée et M11 externes non attestées publiquement.
- G1 : contrat scientifique et continuité documentés, revue indépendante encore `REVIEW_REQUIRED` (issue #662).
- G2 : scaffold isolé (#667), propriétaire d'intention pur (#668), frontières de vérification d'une source et d'un débit externe (#669), et **banc SQLite transactionnel local** (`modules/intention_atomic_fixture.py`). Chaque mécanisme reste privé du code source, sans naissance.
- G3 : le nouveau banc vérifie un budget **synthétique** et l'état d'intention publiés dans une seule transaction SQLite, avec rejeu et fautes injectées. **Ce n'est pas une preuve de comptabilité du vrai Scheduler ou de récupération M11** ; la frontière entre ledgers indépendants, WorldBody, contrôle moteur et mortalité est encore inconnue. Voir [INTENTION_ATOMIC_FIXTURE.md](INTENTION_ATOMIC_FIXTURE.md), [INTENTION_INGRESS.md](INTENTION_INGRESS.md), [INTENTION_CONTINUITY.md](INTENTION_CONTINUITY.md).
- G4–G6 : aucune cohorte I2, aucun préenregistrement confirmatoire final, aucune comparaison à I1, aucun bénéfice d'apprentissage naturel démontré.

I1 reste seul actif dans `config/engine-registry.json`. Aucun état cognitif, vécu, Q, a priori alimentaire, option motrice ou privilège de sécurité n'est transmis à I2.
