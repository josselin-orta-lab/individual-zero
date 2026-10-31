# I2 : modules expérimentaux inertes, non enregistrés

- `intention_continuity.py` : état sémantique, persistance/suspension sans commande.
- `intention_ingress.py` : contrats de source et débit externes, **sans** atomicité inter-ledger réelle.
- `intention_atomic_fixture.py` : budget synthétique + intention dans un seul COMMIT SQLite.
- `option_reconstruction.py` : candidats uniquement issus de la perception courante.
- `competition_preview.py` : évaluation consultative de **tous** les candidats, aucun pouvoir moteur.
- `uc_allocation_study.py` : comparaison expérimentale hors ligne des plafonds UC, aucun mode promu.
- `competition_transaction_fixture.py` : budget synthétique + avis dans un seul COMMIT SQLite.
- `cognitive_cycle_fixture.py` : **banc unifié**, intention + reconstruction + Competition + débits synthétiques + journal dans **une seule transaction de test**. Les deux fixtures antérieurs ne doivent pas être enchaînés pour simuler une atomicité globale.

**Pas de naissance I2, Scheduler réel, M11, Gatekeeper, Action Control, WorldBody, moteur actif, connaissance héritée ni preuve de bénéfice adaptatif.** Consultez `../docs/COGNITIVE_CYCLE_FIXTURE.md` et les protocoles historiques associés.
