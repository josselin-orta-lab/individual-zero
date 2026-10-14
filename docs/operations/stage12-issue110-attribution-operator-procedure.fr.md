# Issue #110 — Reproduction opérateur du contrôle des preuves

**Périmètre : vérification technique d'absence de promotion injustifiée, pas réception du détecteur.**

La PR conserve `main` et toutes les spécifications normatives inchangées.

Sur un checkout propre du SHA exact de la PR, avec Python **3.11 puis 3.12** :

```bash
python -m pip install -e .
python -m unittest discover -s tests -p 'test_stage12_attribution_provenance.py' -v
python -m unittest discover -s tests -p 'test_stage12_goal_progress.py' -v
python -m unittest discover -s tests -p 'test_stage12_diagnostic_audit.py' -v
```

Pour la campagne exploratoire, utiliser un répertoire neuf et une identité nouvelle :

```bash
mkdir -p /tmp/i0-issue110
python scripts/run_stage12_operator_trial.py --output-dir /tmp/i0-issue110/trial --steps 600
```

Le manifeste `trial-manifest.json` contient `head_hash`, `occurrences`, versions, nombre de pas et statut de l'individu. Faire sortir ces deux ancres de l'archive dans le processus de réception. Ensuite :

```bash
python scripts/report_stage12_attribution_provenance.py /tmp/i0-issue110/trial/canonical-export.jsonl --expected-head <HEAD_HASH> --expected-count <OCCURRENCES>
python scripts/report_stage12_operator_packet.py /tmp/i0-issue110/trial/canonical-export.jsonl --expected-head <HEAD_HASH> --expected-count <OCCURRENCES> --expected-world-steps 600 --require-terminal-stop
```

La sortie JSON affiche séparément `verified_successes`, `verified_failures`, `unknown_results`, les trois catégories P-47, `admitted_pairs` et `unavailable_diagnostics`. **`admitted_pairs=0` signifie que le contrat de jugement indépendant est absent ; cela ne signifie pas qu'aucun résultat n'a été vécu.** Aucune classe positive ou négative de biais ne peut être déclarée à partir de cette seule campagne.

La campagne longue actuelle désactive volontairement le sommeil dans son fixture de développement. Elle ne couvre donc pas la consolidation, toutes les situations physiologiques ou la récupération M-11 SQLite. Les tests de crash, cold recovery, mortalité et sommeil restent des vérifications distinctes nécessaires lors de l'évolution normative.

Si les tests ou le runner échouent, conserver la trace brute, le SHA exact et le journal, ne jamais relancer la même identité après arrêt ou mort, et ne pas transformer une expérience négative en preuve positive.

**Décision attendue :** confirmer la frontière épistémique et autoriser, ou non, une modification normative de la sémantique subjective dans `docs/architecture/proposals/stage12-subjective-goal-agency-v1-issue110.fr.md`. Tant que non autorisé : issue #110 ouverte, Stage 12 non réceptionné.
