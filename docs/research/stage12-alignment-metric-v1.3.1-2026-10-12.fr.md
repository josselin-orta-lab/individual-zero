# Stage 12 : mesure externe d'alignement buts/actions réellement exécutées

**Date :** 12 octobre 2026. **Statut :** développement logiciel, validation opérateur non prononcée.  
**Norme :** v1.3.1 (conservation des contrats v1.2.1 §19.5 et §20.3).

## Principe

La métrique externe lit **uniquement** le journal technique causal complet après une vérification indépendante. Elle ne fournit aucun signal à I0 et n'importe ni Oracle ni Bench. La publication Stage 12 `stage12_action_motive_attested` a lieu **avant** la transition physique et expose seulement la provenance intentionnelle réellement disponible au décideur à ce moment. Elle ne prouve ni la vérité de l'intention, ni la justesse de la décision.

L'algorithme compte exclusivement les pas `step_closed` avec résultat `normal` ou `dead` associés à un `command_experienced` physique unique. Un projet d'action, une simulation, un veto ou un blocage sans avance du monde ne compte pas. Le décès est compté une seule fois comme résultat physique ; aucune attribution cognitive nouvelle ne peut être écrite après la mort.

## Catégories observables

1. `goal_directed` : décision admise, témoin antérieur correspondant à la commande réellement envoyée et référence de but explicite égale au but actif vécu au moment de l'admission.
2. `legitimate_autonomous_intrinsic` : réflexe autorisé avec référence de déclenchement ; sommeil autorisé avec capture réduite ou pression validée ; exploration motivée avec preuve intrinsèque préalablement enregistrée. Les sous-types sont conservés via le champ `basis` : un réflexe ou du sommeil **n'est pas automatiquement une preuve de curiosité**.
3. `without_traceable_justification` : aucune des justifications précédentes n'est établie par les sources accessibles. **Cette catégorie mesure un défaut de traçabilité ; elle ne prouve pas une action irrationnelle, sans but ou dangereuse.** Les actions `fallback` sans preuve de motif détaillé y restent prudemment comptées.

La somme des catégories doit correspondre exactement au nombre de commandes réellement appliquées, y compris létales, sans pas fictif après mort.

## Exécution technique

Depuis un checkout propre au SHA de la PR (Python 3.11 ou 3.12) :

```bash
python -m pip install -e .
python -m unittest discover -s tests -p 'test_stage12_alignment.py' -v
python scripts/report_stage12_alignment.py /chemin/vers/export-canonique.jsonl --expected-head <sha256> --expected-count <entier>
```

Le fichier doit être un **export canonique sans saut de ligne terminal**, et non le fichier WAL brut comportant un délimiteur de fin de record. La vérification cryptographique du journal est obligatoire avant le calcul. Les deux arguments de confiance proviennent d'un témoin opérateur indépendant ; en leur absence, on prouve seulement la cohérence interne du fichier fourni et non sa complétude absolue.

Le rapport JSON publie la répartition et les observations individuellement traçables. Conserver également le SHA Git du logiciel, les graines, la configuration, le nombre réel de pas, les décès et les champs `unexamined_event_kinds` du vérificateur indépendant si nécessaire.

## Limitations et réceptions restantes

- L'intégration Stage 10/11/12, la console opérateur (PR #107) et l'état courant durable M-11 doivent être vérifiés séparément sur l'arbre final.
- Le test sur 600 transitions peut soutenir une hypothèse de développement, pas un verdict scientifique. La couverture de chaque catégorie doit être annoncée : **une catégorie non observée n'est pas validée**.
- Les données expérimentales n'impliquent pas de droit d'accès du runtime cognitif au journal technique ; la métrique reste hors cognition.
- Le Stage 12 reste `EN COURS` jusqu'à conformité de l'ensemble de son périmètre et décision explicite de l'opérateur.
