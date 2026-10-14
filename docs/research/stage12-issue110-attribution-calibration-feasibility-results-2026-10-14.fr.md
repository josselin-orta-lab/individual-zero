# Calibration Stage 12 / Issue 110 : premier pilote de faisabilité, 14 octobre 2026

**Préenregistrement antérieur au code:** `729a119`. **SHA source pilote:** `d5cd640f7ecad6875111930440475f3d4193de14`. **Exécution**: [GitHub Actions #38530260912](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38530260912), Python 3.11 et 3.12, archives WAL/JSONL conservées.

Quatre vies préprogrammées avant naissance, 16 transitions chacune (64 transitions). Les seuils `window=12`, `bias_min_outcomes_each=2`, `threshold=0.75` n'ont pas changé. **Données observées dans les logs Python 3.12** :

| Vie | Pas | self | world | unknown | Paires consommées | Audit |
|---|---:|---:|---:|---:|---:|---|
| Libre | 16 | 2 | 0 | 1 | 1 | OK |
| Obstacle permanent A2 | 16 | 0 | 1 | 0 | 1 | OK |
| Obstacle retiré à t3 | 16 | 2 | 0 | 2 | 1 | OK |
| Obstacle retiré à t4 | 16 | non certifié | non certifié | non certifié | non certifié | FAIL : capture perceptive non vérifiable |

Le quatrième cas retourne `ValueError: first-person assessment lacks independently recorded perception`; le runner conserve son WAL, son JSONL et son erreur exacte. **Le workflow échoue**, même si trois vies sont auditables. Il serait incorrect de comptabiliser les observations de la quatrième vie comme scientifiquement validées.

Sur les quatre vies, **zéro n'atteint** deux succès et deux échecs vérifiés dans la **même fenêtre cognitive**. Aucun verdict `attribution_bias` ne peut être démontré. Le regroupement inter-vies est réservé aux métriques scientifiques externes et ne peut pas injecter des paires entre sujets dans la mémoire du détecteur d'I0.

La vie avec obstacle fixe conserve un `world` autonome sans moteur causal caché visible à I0. Le contraste retrait-t3 confirme une absence de `world` dans la série pilotée malgré l'échec potentiellement ambigu, mais cette interprétation reste exploratoire. Il faut comprendre l'absence de nouveaux engagements et l'erreur de la vie retrait-t4 avant d'allonger des campagnes, puis vérifier un corpus autonome hors échantillon.

**Statut:** expérience scientifique de faisabilité **PARTIAL**, exécution CI **FAIL** pour le quatrième audit, calibration du détecteur **NON ÉVALUABLE**. Ni le Stage 12 ni l'issue #110 ne sont reçus. Aucune norme modifiée, aucune PR fusionnée.
