# I3 G2b — Préinscription : P1.1 contre P1 sur mondes réservés

**Déposé le 5 novembre 2026, avant toute exécution des mondes H1 à H3.** Protocole `i3-g2b-p11-heldout-v1`, code `src/i3/lab/heldout_p11.py` (mondes, exécuteur et calcul du verdict). Une seule exécution par version ; résultat publié dans un commit séparé, quel qu'il soit.

## Question

La correction P1.1 (le sommeil connu restaure énergie et vigilance dans l'auto-projection) est-elle au moins aussi bonne que P1 sur des mondes jamais vus, et ne réintroduit-elle pas le défaut « eau connue mais retour trop tard » ?

## Conditions

- **Versions** : P1 = commit `1068935` ; P1.1 = commit de cette préinscription.
- **Génomes** : `generation_zero(201)` à `(230)`, une vie par génome et par monde, graine de vie 2000 + n, horizon 400 pas. Mêmes génomes et graines pour les deux versions (comparaison appariée).
- **Mondes réservés**, écrits après l'arrêt du développement de P1.1 :

| Monde | Situation |
| --- | --- |
| `g2b-h1-hidden-spring` | 16 × 16, eau à 4 cases au nord, hors de vue ; nourriture proche |
| `g2b-h2-round-trip` | Eau au point de départ, nourriture à 10 cases : il faut aller manger et revenir boire |
| `g2b-h3-dried-spring` | Source A adjacente, finie (4 gorgées) ; source B à 14 cases, hors de vue ; nourriture près des deux |

## Critères (tous requis pour adopter P1.1)

1. **Non-infériorité** dans chaque monde : survivants à 400 pas de P1.1 ≥ survivants de P1 − 3 (sur 30).
2. **Défaut ciblé** (H2) : morts de soif après avoir bu au moins une fois, P1.1 ≤ P1.
3. **Régression G2** (usage déclaré des trois mondes G2, sans réglage) : P1.1 repasse le critère d'origine, au moins 8/10 vies qui boivent dans chacun.
4. **Technique** : rejeux identiques pour toutes les vies P1.1 ; ≤ 1 ms par pas en moyenne.

Décision : `ADOPT_P1_1` si tout est rempli, sinon `REJECT_P1_1_KEEP_P1` (retour au code de P1).

Descriptif, sans critère : usage de la source lointaine dans H3 (révision de stratégie).
