# I3 G2 — Résultat du premier test falsifiable

**Verdict : `G2_PASS_BEHAVIOURAL_AND_TECHNICAL`.** Exécution unique le 5 novembre 2026, sur le code de la préinscription (commit `e25bf63`, [protocole](../../G2_FIRST_FALSIFIER_PREREG.md)). Données complètes : [result.json](result.json). C'est une porte logicielle et un falsificateur comportemental passé, **pas** un résultat scientifique ni une preuve d'apprentissage.

## Critères préinscrits

| Monde | Ont bu (requis 8/10) | Vivants à 300 pas | Morts | 1re gorgée (médiane, min–max) | Gorgées / repas (médianes) | Part de sommeil (médiane) |
| --- | --- | --- | --- | --- | --- | --- |
| `g2-i1-foraging-like` | **10/10** | 9 | 1 (soif) | pas 7 (3–13) | 23,5 / 7 | 29 % |
| `g2-i2-native-A-like` | **10/10** | 10 | 0 | pas 5 (1–9) | 30 / 17 | 27 % |
| `g2-i2-native-B-like` | **10/10** | 10 | 0 | pas 3 (3–6) | 37,5 / 17 | 26 % |

Technique : 30/30 rejeux identiques ; **0,40 ms par pas** en moyenne (budget 1 ms) ; 7,6 s pour les 66 vies.

Repères non appariés, issus du diagnostic du 5 novembre : la vie I1 *foraging* (graine 7) est morte de soif au pas 106 en dormant 82 % du temps ; la vie I2 « B » est morte de soif au pas 111, figée au passage.

## Constats secondaires (descriptifs, sans réglage)

**Le génome médian, rapporté à part, meurt de soif au pas 106 sans avoir bu dans `foraging`.** Au premier pas, explorer vers l'est (vers l'eau, invisible) et vers le nord sont à égalité ; le tirage choisit le nord. L'exploration « frontière la plus proche » longe ensuite les bords et s'éloigne de l'eau jusqu'à l'épuisement. C'est un échec légitime sous ignorance, mais il montre que cette stratégie d'exploration ne couvre pas l'espace efficacement.

**Le génome 8 meurt de soif au pas 267 après avoir bu deux fois.** Une fois désaltéré, il s'éloigne d'une vingtaine de cases de l'eau connue ; il n'entame le retour qu'avec 10,8 d'eau et 22 d'énergie, trop tard. Hypothèse : la projection innée garde l'énergie à son niveau de fin de trajet, donc un long retour qui finit à basse énergie paraît coûteux pour toujours, et il est repoussé jusqu'à ce que la soif domine.

## Limites

Dix génomes de génération 0 et trois mondes figés ne mesurent qu'une capacité d'architecture : sortir de la paralysie et atteindre l'eau. Aucune comparaison appariée avec I1 ou I2 : I3 perçoit le contenu des cases voisines (contrairement à I2), paie sa cognition et n'a ni nuit ni objets inertes. Aucun apprentissage n'est démontré ici.

## Suite

1. **P1.1** — Corriger les deux défauts ci-dessus (projection de l'énergie et de la vigilance vers leur restauration par le sommeil ; exploration qui couvre l'espace), en développement sur `lab/dev_worlds.py` uniquement, puis les tester sur de **nouveaux** mondes réservés. Ces trois mondes ne servent plus à régler quoi que ce soit.
2. **P2** — Générateur de familles de mondes et sonde de faisabilité, puis porte G3 (familles gelées avant toute évolution).
