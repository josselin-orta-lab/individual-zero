# I3 G2 — Préinscription du premier test falsifiable

**Déposé le 5 novembre 2026, avant toute exécution des trois mondes de test.** Protocole `i3-g2-first-falsifier-v1`, code `src/i3/lab/first_falsifier.py`. Le SHA du commit qui contient ce fichier et l'exécuteur est la référence ; le résultat est publié dans un commit séparé, quel qu'il soit.

## Question

Le noyau I3, avec des génomes de génération 0 et sans évolution, sort-il de la paralysie et atteint-il l'eau dans les situations où I1 et I2 sont morts de soif lors du diagnostic du 5 novembre, sans aucune règle propre à ces situations ?

## Conditions figées

| Monde | Reproduit | Géométrie et ressources |
| --- | --- | --- |
| `g2-i1-foraging-like` | Preset I1 *foraging* (mort de soif au pas 106, eau à 2 cases) | 30 × 30, naissance (7,7) ; eau illimitée (+40) en (9,7) et (10,9) ; `berry_a` (+10 nourriture) en (8,7) ×4 et (7,9) ×3 ; `berry_b` (+5, −10 intégrité) en (11,8) ×3 ; corps 70/45/42/85, vigilance 100 |
| `g2-i2-native-A-like` | Monde natif I2 A du diagnostic (108 abstentions sur 128) | Couloir camp–passage–source ; eau au camp (+35, stock 2, +1 tous les 10 pas) ; nourriture au passage (+20, stock 1, +1 tous les 8 pas) ; corps 78/46/44/94, vigilance 100 |
| `g2-i2-native-B-like` | Monde natif I2 B (mort de soif figé au passage) | Couloir ; eau et nourriture à la source seulement (stocks 2, +1 tous les 8 pas) ; même corps |

**Génomes** : `generation_zero(1)` à `generation_zero(10)`, une vie par génome et par monde, graine de vie 1000 + n, horizon 300 pas. Le génome médian est rapporté à part, à titre descriptif.

**Différences assumées avec les conditions d'origine.** I3 perçoit le contenu des 4 cases voisines (comme I1, contrairement à I2). Il possède un canal de vigilance et paie sa cognition en énergie. Les mondes omettent bois, pierres et nuit. Ce test porte sur l'architecture de I3, pas sur une comparaison appariée avec I1 ou I2.

## Critères décidés avant exécution

1. **Comportemental (principal)** : dans **chacun** des trois mondes, au moins **8 vies sur 10** boivent au moins une fois avant la mort ou l'horizon.
2. **Technique** : les 30 vies, rejouées une seconde fois, produisent la même tête de journal ; temps moyen ≤ **1 ms par pas**.

## Verdicts

- `INVALID_EXPERIMENT` : un rejeu diverge.
- `G2_PASS_BEHAVIOURAL_AND_TECHNICAL` : les deux critères sont remplis. C'est une porte logicielle et un falsificateur comportemental passé, **pas** un résultat scientifique ni une preuve d'apprentissage.
- `G2_FAIL` : sinon. On revient à la conception de P1 avant toute lignée ; aucun réglage sur ces trois mondes n'est permis.

## Historique de développement déclaré

Le noyau a été mis au point uniquement sur `lab/dev_worlds.py` (champ ouvert 14 × 14, couloir de 6 cases), dont la géométrie et les nombres diffèrent des mondes de test. Les cinq corrections d'architecture qui en sont sorties sont listées dans [SPECIFICATION.md](SPECIFICATION.md). Aucun des trois mondes de test n'a été exécuté avant le dépôt de ce fichier.
