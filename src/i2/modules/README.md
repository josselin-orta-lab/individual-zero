# I2 : modules expérimentaux isolés, sans naissance ni autorité motrice

- `intention_continuity.py` : propriétaire d'une intention sémantique ; conserve/suspend/invalide sans action.
- `intention_ingress.py` : admission par deux ports externes d'observation et de débit UC, non authentifiés par I2.
- `intention_atomic_fixture.py` : banc SQLite local qui regroupe débit **synthétique**, intention et journal dans un COMMIT ; ni Scheduler réel ni M11.
- `option_reconstruction.py` : fonction pure de candidats sémantiques **uniquement visibles dans la capture courante**. L'intention apporte au plus une référence de contexte ; aucun score, ordre de commande, accumulateur ou veto n'est transmis. Tous les candidats doivent être réévalués ultérieurement.

Ces modules ne sont ni un moteur I2 vivant, ni une implémentation de Competition/Action Control, ni une preuve d'apprentissage. Documentation : `../docs/OPTION_RECONSTRUCTION.md`, `../docs/INTENTION_ATOMIC_FIXTURE.md`, `../docs/INTENTION_INGRESS.md` et `../docs/INTENTION_CONTINUITY.md`.
