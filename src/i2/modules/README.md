# I2 : composants logiciels expérimentaux isolés, sans naissance

- `intention_continuity.py` : propriétaire d'intentions sémantiques, sans action.
- `intention_ingress.py` : interface à deux ports pour provenance et débit UC ; aucune autorité réelle I2 n'est encore installée.
- `intention_atomic_fixture.py` : SQLite local, budget synthétique et journal de test, **pas M11**.
- `option_reconstruction.py` : possibilités sémantiques présentes et éphémères ; intention seulement en métadonnée.
- `competition_preview.py` : prototype d'avis Competition avec évaluation **de tous** les candidats en un lot UC externe, refus si incomplet, et `veto_preview` sans admission. Les ports injectés des tests sont synthétiques, sans vraie facturation ou valeur vécue.

Ce code n'est ni un moteur vivant, ni un Scheduler, ni un Action Control, ni une preuve scientifique. Voir `../docs/COMPETITION_PREVIEW.md`, `../docs/OPTION_RECONSTRUCTION.md`, `../docs/INTENTION_ATOMIC_FIXTURE.md`, `../docs/INTENTION_INGRESS.md` et `../docs/INTENTION_CONTINUITY.md`.