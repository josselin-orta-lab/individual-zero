# I3 — Plan de test

| Niveau | Contenu | État |
| --- | --- | --- |
| Contrat logiciel | `tests/i3/test_core.py` : génome fermé, physique v4, monnaie vitale, capacités, capture locale, mort irréversible, nouveau-né vierge, rejeu exact, invariance par renommage, pas d'abstention par défaut, `attendre` non privilégié, budget de temps | Implémenté |
| Porte G2 | Falsificateur comportemental préinscrit + rejeu + ≤ 1 ms/pas | Passée ; sert de régression plancher |
| Portes sous sélection | `lab/selection_gate.py` (ADR-0015) ; G2d : P1.3 adopté | Implémenté |
| Croyances révisables | `P13Tests` : révision au rythme hérité, gène tiré en dernier | Implémenté |
| P2 | Générateur et sondes faits ; reste : famille d'évolution E, test d'invariance dynamique sur mondes générés, porte G3 | En cours |
| P3 | Lignée, registre, test de non-transmission entre générations | À faire |
| P4 | Plan 2 × 2 et ablations d'enjeu, préinscrits à la porte G4 | À faire |
