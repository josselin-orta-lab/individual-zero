# I2 : composants logiciels candidats, sans naissance

- `intention_continuity.py` : intention sémantique révisable, sans droit moteur.
- `intention_ingress.py` : interfaces déclarées de provenance et de débit UC, non authentifiées par I2.
- `intention_atomic_fixture.py` : budget SQLite **synthétique**, pas M11.
- `option_reconstruction.py` : candidats éphémères reconstruits seulement à partir de la capture courante.
- `competition_preview.py` : avis Competition, évaluation du lot entier ou abstention, sans admission.
- `uc_allocation_study.py` : comparaison synthétique de politiques UC, sans modifier Competition.
- `competition_transaction_fixture.py` : transaction SQLite synthétique de Competition.
- `cognitive_cycle_fixture.py` : intention et Competition dans **un** COMMIT SQLite de test, pas une vie.
- `action_control_boundary.py` : vérification indépendante de forme/fraîcheur, débit UC de **revue**, provenance de veto et résultat **`motor_authority=NONE`**. Même lorsque le veto est levé, **aucun droit à l'action** n'est produit. Les autorités de test ne sont ni Scheduler ni M11.

Ces modules restent une proposition de recherche, et non un moteur, une preuve
physique ou une validation L3. Voir `../docs/ACTION_CONTROL_BOUNDARY.md`.
