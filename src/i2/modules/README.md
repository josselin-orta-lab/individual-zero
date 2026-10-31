# I2 : modules (candidats, non exécutables)

- `intention_continuity.py` : propriétaire pur d'intention sémantique, sans option ni commande.
- `intention_ingress.py` : contrat à deux ports (observation et débit UC externes), sans preuve actuelle d'atomicité inter-ledgers.
- `intention_atomic_fixture.py` : **banc SQLite local** : une seule transaction regroupe un budget de test, l'intention et le journal ; des injections vérifient rollback, COMMIT et rejeu. Il n'est pas le Scheduler, M11, ni une vie I2.

Ces modules ne constituent ni un moteur I2, ni Action Control, ni une preuve scientifique. Voir `../docs/INTENTION_ATOMIC_FIXTURE.md`, `../docs/INTENTION_INGRESS.md` et `../docs/INTENTION_CONTINUITY.md`.
