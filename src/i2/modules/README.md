# I2 : composants isolés, sans naissance ni autorité motrice

- `intention_continuity.py` : intention sémantique persistante, sans commande.
- `intention_ingress.py` : contrats de ports source et débit UC externes.
- `intention_atomic_fixture.py` : budget synthétique et intention dans une transaction SQLite, pas M11.
- `option_reconstruction.py` : candidats issus exclusivement de la perception courante.
- `competition_preview.py` : avis après lot complet d'évaluations déclarées payées, sans admission.
- `uc_allocation_study.py` : étude hors ligne de politiques UC à budget plafonné ; aucune politique sélectionnée.
- `competition_transaction_fixture.py` : **second banc** SQLite, dédié à la publication atomique du débit UC synthétique et de l'avis Competition, avec audit/rejeu et confirmations perdues. Les deux bancs ne partagent pas de transaction commune.

Ces composants ne constituent ni un vrai Scheduler, ni un runtime M11, ni Action Control. L'identité first-person et les preuves d'apprentissage demeurent des obligations d'intégration non satisfaites. Voir `../docs/COMPETITION_TRANSACTION_FIXTURE.md` et `../docs/STATUS.md`.
