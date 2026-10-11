# Stage 11 : préservation de l'identité technique dans la projection autobiographique

**11 octobre 2026. Résultat logiciel local isolé, Python 3.13.5.** Ceci n'est ni un test d'intégration complet, ni une campagne Python 3.11, ni un Golden, ni une validation scientifique. **Stage 11 EN COURS, Stage 9 NO-GO scientifique.**

## Protocole préexistant et cause

Le protocole `stage11-autobiographical-event-id-custody-protocol.en.md` a été poussé **avant** toute correction distante, commit `cbefa418c71c16f337bc73c45484720d81431d68`.

Dans `AutobiographicalPolicy.project`, le dictionnaire projeté était initialisé avec l'authentique `JournalEntry.event_id`, puis toute clé autorisée était copiée depuis le payload causal. Une politique accidentellement configurée pour autoriser `event_id` permettait alors d'écraser l'identifiant technique par un identifiant produit dans le payload. Le journal conservait des hashes valides, mais l'identité affichée dans l'histoire autobiographique ne correspondait plus à l'occurrence technique.

Fixture synthétique locale : `JournalEntry.event_id = "1" * 64`, payload `event_id = "fabricated"`, politique autorisant `event_id`. Avant correction, la projection renvoyait `fabricated` ; `journal.verify()` restait vrai. Une nouvelle méthode `test_payload_event_id_cannot_spoof_autobiographical_provenance` a été exécutée **avant** correction : elle échouait avec `fabricated-source-id` au lieu du SHA de référence.

## Correction minimale

- `src/lab/journal_views.py` : ignorer le champ `event_id` lorsqu'il apparaît parmi les champs autorisés par la politique ; toujours conserver l'identifiant `JournalEntry.event_id` affecté au début de la projection.
- `tests/test_journal_views.py` : ajouter la fixture de tentative d'usurpation, vérifiant l'identifiant authentique, `t_monde`, l'absence d'`attempt_ref`, la présence du commit réellement ajouté et la validité du journal.
- Aucun changement des octets des événements techniques, de la sémantique des politiques standard ou de la spécification normative.

**Commits distants :** code `63bb7c82614074493b18bda09f6aab753a954cd8` ; test `12df1e698a0f0c550647145ab928f3d1c84475af`.

## Exécutions et frontières de preuve

Harnais isolé sous **Python 3.13.5**, avec reconstruction locale depuis le contenu GitHub des modules concernés et uniquement les primitives canoniques requises de `determinism.py`. Les blobs Git des sources/trois fichiers de tests d'origine ont été vérifiés directement : `journal.py=27fa48d00f5f50749db763d42cc530244c9bea85`, `journal_views.py=26d41166dbbe9f435c2376060320365bbd37738e` avant correction, `snapshots.py=a5cc98502bfff9eaa5192bd68e9bdfed3e7b6a10`, `test_causal_journal.py=bda0ff80b1a002c0c6d111131545c9119c7de34e`, `test_journal_views.py=e6d4598eae739d25fa818caf2c6c671fc9814c43` avant ajout du test. Les tests de snapshots ont été copiés manuellement.

- `test_causal_journal.py` : **17/17 PASS** dans ce harnais.
- `test_journal_views.py` : **8/8 PASS** avant ajout de la fixture ; fixture ajoutée **FAIL attendu 1/9** avant correction, puis **9/9 PASS** après correction locale équivalente.
- `test_snapshots.py` : **9/9 PASS** dans ce harnais.
- Combinaison des trois fichiers après correction : **35/35 PASS**, zéro échec et zéro exclusion ; compilation des modules isolés réussie.
- **Limitation** : ces exécutions ne portent pas sur un checkout complet du dépôt et n'ont pas été relancées sur les blobs distants *après* les commits. L'environnement isolé est en Python 3.13.5, non le runtime normatif 3.11. Aucune CI n'a été déclenchée.

Les suites intégrées `test_stage11_external_input_atomicity.py`, `test_stage11_scenario_payload_custody.py` et `test_stage11_hidden_hazard_budget_snapshots.py` sont **non exécutées** dans cette session, faute de checkout complet. De même, Python 3.12 complet, Python 3.11, Goldens historiques et expériences indépendantes sont **non exécutés** sur ce HEAD.

## Prochaine priorité

Exécuter les cinq groupes ciblés sur un checkout complet du HEAD publié, puis les régressions voisines ; vérifier la provenance physique et la restauration transactionnelle. Ensuite seulement étendre les diagnostics des impasses, dangers inconnus et UC limités sans extrapolation scientifique.

**PR #25 conservée ouverte, Draft, non fusionnée.**

## Reprise contrôlée de la CI sur le dépôt public (2026-10-11)

Le dépôt est désormais public. Un premier ajout du label `ci-unit` à la PR #25 n'a pas produit de nouvelle exécution, car le HEAD portait l'instruction `[skip ci]` dans le message de commit. Cette section enregistre la reprise du contrôle logiciel : un checkpoint documentaire sans instruction de saut permet de demander les vérifications Python 3.12 du workflow existant via l'événement `pull_request:labeled`. Ce checkpoint n'altère aucune source, aucun résultat antérieur, aucun protocole scientifique, ni aucun Golden. Les résultats CI et leurs SHA seront qualifiés séparément après exécution réelle ; aucune réussite n'est présumée ici.
