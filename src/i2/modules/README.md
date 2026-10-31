# I2 : composants logiciels expérimentaux, sans vie ni moteur enregistré

- `intention_continuity.py` : registre d'intention purement sémantique.
- `intention_ingress.py` : ports de provenance déclarée et d'UC externe ; aucune authentification réelle.
- `intention_atomic_fixture.py` : transaction SQLite pour débit d'intention synthétique.
- `option_reconstruction.py` : candidats éphémères de la perception courante, sans privilège.
- `competition_preview.py` : avis Competition non moteur ; tout le frame évalué ou abstention.
- `uc_allocation_study.py` : comparaison synthétique d'allocations UC ; aucune stratégie promue.
- `competition_transaction_fixture.py` : banc transactionnel de Competition et son UC de test.
- `cognitive_cycle_fixture.py` : intention, candidats et Competition dans **un** COMMIT de test.
- `action_control_boundary.py` : revue indépendante des avis, de la fraîcheur, du reçu UC et du veto, toujours `motor_authority=NONE`.
- `action_control_custody_fixture.py` : **revue** et débit UC de test dans un second fichier SQLite transactionnel, avec rejeu froid. Ce banc **n'est pas** atomique avec `cognitive_cycle_fixture.py` et **n'accorde jamais de permis moteur**.

Ces fichiers ne sont ni un individu né, ni un vrai Scheduler/M11, ni un WorldBody, ni une preuve d'apprentissage. Voir `../docs/ACTION_CONTROL_CUSTODY_FIXTURE.md`, `../docs/ACTION_CONTROL_BOUNDARY.md` et `../docs/COGNITIVE_CYCLE_FIXTURE.md`.
