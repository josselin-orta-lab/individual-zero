# I3 — Architecture v1

Aucun import de I0, I1 ou I2 (ADR-0001). La transition corporelle est recopiée de I2 avec sa provenance (RAI : ADAPT).

| Fichier | Rôle |
| --- | --- |
| `modules/body.py` | Lois du corps (physique v4), canal de vigilance, monnaie vitale, capacités vulnérables |
| `modules/world.py` | Monde séparé : positions, stocks, effets cachés, changements programmés, capture locale |
| `modules/genome.py` | Génome fermé `i3-genome-v1`, génération 0, mutation bornée, contrôle d'admissibilité |
| `modules/mind.py` | Perception, modèle des effets, carte et croyances de présence, auto-projection, valeurs TD, modèle de soi, Competition, Action Control, apprentissage, rejeu de sommeil |
| `runtime/life.py` | Une vie déterministe, journal chaîné par hachage |
| `lab/dev_worlds.py` | Mondes de développement (jamais ceux d'un test préinscrit) |
| `lab/first_falsifier.py` | Porte G2 préinscrite |

Boucle d'un pas : `World.capture()` → `Mind.decide(capture, allowance)` → `World.step(action, travail cognitif)` → `Mind.observe_outcome()` → `Mind.prepare_learning()` → `World.pay_cognition()` → `Mind.learn_from_outcome()`. La physique v2 paie la décision avant l'action, puis prépaie l'apprentissage et les rejeux abordables dans le même pas. Aucun rejeu n'est reporté après le décès ou la fin d'observation. Voir [COGNITIVE_FUNDING.md](COGNITIVE_FUNDING.md) pour l'ordre causal et les limites du modèle.
