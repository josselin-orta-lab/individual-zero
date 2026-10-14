# Réception technique A2 / Issue #110, 14 octobre 2026

Source de l'audit adversarial : `2fa1bfae64ce9b42c46454c28687e61269e9a327`.
Préenregistrement prospectif de la campagne : `9de2aeb`.
Campagne autonome précédente : `f036467b`, [CI #38526909703](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38526909703).

## Enchaînement causal et audit

Les événements environnementaux admissibles sont programmés avant naissance, sans lecture de la décision d'I0. Le moteur publie `command_experienced` uniquement après admission, puis `external_input_received` et `external_input_applied` à la phase `after_admission`, avant `world_transition_experienced`. L'action de l'individu ne détermine ni la date, ni la cellule, ni le type d'événement. La capture suivante peut montrer une passabilité passée de `True` à `False`. L'individu forme alors son jugement via Action Control, avec UC, sans lire le calendrier externe. L'évaluateur inspecte séparément les reçus.

L'auditeur read-only `src/lab/stage12_a2_causal_audit.py` contraint l'ordre physique, les références d'admission, les pas, coordonnées et directions, le changement observable, la préinscription d'objectif et le couple `(failure,world)` avec vérification par les auditeurs existants de source cognitive et de jointure. Il accepte un calendrier attendu `expected_interventions` fixé hors du journal. Les tests adversariaux recalculent toute la chaîne de hachage après falsification du temps, de la géométrie, de la phase ou suppression des reçus. L'audit complet doit les refuser. Ces garanties sont des assertions sur la provenance journalisée, **pas une preuve métaphysique de causalité**.

M11: les tests `tests/test_stage12_a2_m11_crash.py` provoquent un vrai `os._exit(73)` au pas 2, avant et après le COMMIT SQL. Avant COMMIT, l'intention n'est pas restaurable et aucun événement d'intervention n'est dans la génération validée; après COMMIT, exactement une intervention figure dans le journal durable, l'identité et la génération se conservent et la reprise à froid peut avancer sans rejouer le pas 2. Les tests M11 antérieurs restent exécutés.

## Résultats physiques déjà reproduits

Quatre vies de 50 pas, soit 200 transitions. `self=2`, `world=1`, `unknown=1`, `unavailable=0`; trois couples admis et deux appliqués, dont `(failure,world)` pour la vie Food/A2. Empreintes JSONL binaires-identiques sous Python 3.11 et Python 3.12. Une seule expérience positive `world` est un **signal scientifique exploratoire**, pas une généralisation. Deux vies Water n'ont aucune intention spatiale : elles ne constituent pas des vrais négatifs.

Le détecteur `attribution_bias` reste non évaluable (`null`) parce qu'il n'a pas encore au moins deux issues distinctes de chaque classe dans sa fenêtre de 12 pas. Aucune modification opportuniste du seuil n'a été apportée. Une matrice de confusion inter-situations ni un taux de faux `world` statistiquement robuste ne peuvent encore être établis. Le principal critère d'acceptation scientifique intégrée de l'issue #110 reste non démontré; ne pas remplacer la calibration requise par des fixtures.

## Décision

- **Composant physique A2 et jugement autonome world : implémentés et exploratoirement étayés** dans un cas.
- **Audit de falsifications et crash M11 A2 : couverture technique ajoutée**, à rattacher aux workflows verts du SHA courant dans le compte rendu opérateur.
- **Calibrage du détecteur / sensibilité / transfert d'autres situations : NON DÉMONTRÉS**.
- **MVP normatif v1.3.1 inchangé**, amendement v1.3.2 toujours candidat.
- **Verdict Issue #110 / Stage 12 : PARTIAL**, pas `READY FOR OPERATOR VALIDATION` et pas de validation opérateur implicite.

Ce rapport termine la tranche de durcissement A2 mais n'autorise ni la clôture de l'issue, ni la fusion anticipée de PR #155, ni l'annonce de réception complète du Stage12. Stage9 reste NO-GO.
