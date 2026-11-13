# I3 — modèle nul de dérive pour l'étape 6 légère : résultats (13 novembre 2026)

**Verdict technique : `DRIFT_NULL_SIZING_COMPLETE`, avec le signalement `COMPOSITE_NULL_ASYMMETRY`. Verdict scientifique : `NOT_ISSUED`.** Ce rapport applique une fois le [préflight](STAGE6_LIGHT_DRIFT_NULL_PREFLIGHT_2026-11-13.md) (commit `d1437b301793858170cfc5a3e989ca44e5c79d33`). C'est une aide au dimensionnement. Il ne crée aucun World ni aucune vie, ne teste pas P3 après coup et ne dit pas si la sélection déplace un gène.

## 1. Exécution et contrôles

| Élément | Résultat |
| --- | --- |
| Code | [stage6_light_drift_null.py](../../../lab/stage6_light_drift_null.py), commit `f05a444d6bf57d75c7eff60993498ca8f3c7c73c`, commité avant l'exécution de la grille |
| Grille | 32 configurations, 4 000 populations simulées chacune, 53 secondes en Python 3.12.3 |
| Empreinte du rapport canonique | `21555983160ef21159062557723ee4d25a32cb8bc443d7f3cc9b0456d9a586e5` |
| S1, ordre de grandeur | **PASS.** Pour 6 génomes et 3 générations, l'écart-type du contraste de `z` vaut 0,226 (`fresh`) et 0,227 (`heritable`). Les deux marqueurs neutres de P3 donnaient 0,224 et 0,330. |
| S2, symétrie pour `z` | **PASS** dans les 32 configurations |
| S3, déterminisme | **PASS** sur la grille réduite des tests ; la grille complète n'a été exécutée qu'une fois |
| Symétrie pour `beta_u_eff` | **Écart signalé** dans 2 configurations sur 32 (section 4) |
| Worlds ouverts, vies créées | 0, 0 |

Le rapport complet est [STAGE6_LIGHT_DRIFT_NULL_REPORT_2026-11-13.json](STAGE6_LIGHT_DRIFT_NULL_REPORT_2026-11-13.json).

## 2. Ce que la dérive seule produit

Les tableaux donnent l'écart-type du contraste entre bras quand la quantité n'a **aucun** effet sur la persistance. Plus il est grand, moins un déplacement réel est visible.

**Régime `heritable`.** `beta_u_eff`, puis `z` entre parenthèses.

| Génomes `N` | `G` = 3 | `G` = 4 | `G` = 6 | `G` = 8 |
| --- | --- | --- | --- | --- |
| 6 | 0,535 (0,227) | 0,637 (0,275) | 0,753 (0,324) | 0,782 (0,344) |
| 12 | 0,409 (0,177) | 0,509 (0,227) | 0,670 (0,281) | 0,710 (0,303) |
| 24 | 0,299 (0,131) | 0,401 (0,169) | 0,545 (0,239) | 0,635 (0,273) |
| 48 | 0,224 (0,096) | 0,292 (0,128) | 0,450 (0,197) | 0,551 (0,243) |

**Régime `fresh`.** `beta_u_eff`, puis `z` entre parenthèses.

| Génomes `N` | `G` = 3 | `G` = 4 | `G` = 6 | `G` = 8 |
| --- | --- | --- | --- | --- |
| 6 | 0,519 (0,226) | 0,595 (0,260) | 0,702 (0,300) | 0,766 (0,325) |
| 12 | 0,385 (0,169) | 0,458 (0,200) | 0,554 (0,245) | 0,621 (0,274) |
| 24 | 0,287 (0,124) | 0,339 (0,148) | 0,419 (0,184) | 0,469 (0,208) |
| 48 | 0,209 (0,091) | 0,251 (0,108) | 0,312 (0,134) | 0,349 (0,155) |

**Fondateurs encore représentés à la dernière génération**, régime `heritable`, bras `selected` puis `random_parent`.

| Génomes `N` | `G` = 3 | `G` = 4 | `G` = 6 | `G` = 8 |
| --- | --- | --- | --- | --- |
| 6 | 2,6 et 3,1 | 1,9 et 2,5 | 1,3 et 1,9 | 1,1 et 1,6 |
| 12 | 4,7 et 5,9 | 3,2 et 4,8 | 1,7 et 3,5 | 1,2 et 2,8 |
| 24 | 8,9 et 11,5 | 5,9 et 9,3 | 2,7 et 6,7 | 1,4 et 5,4 |
| 48 | 17,4 et 22,8 | 11,4 et 18,2 | 4,7 et 13,2 | 2,1 et 10,4 |

Deux lectures directes de ces tableaux :

- **Le bruit de dérive augmente avec le nombre de générations.** Avec la règle de parents de P3 et sans recombinaison, les lignées se réduisent vite à quelques fondateurs. À 48 génomes et 8 générations, le bras `selected` n'en garde que 2,1 en moyenne dans le régime `heritable`.
- **Agrandir la population réduit ce bruit**, à peu près comme l'inverse de la racine de `N`.

## 3. Critère de signe et plus petit déplacement détectable

| Populations | Seuil de signes concordants | Probabilité bilatérale exacte | Rapport au bruit pour 80 % de puissance |
| --- | --- | --- | --- |
| 8 | 8 sur 8 | 0,0078 | 1,919 |
| 12 | 10 sur 12 | 0,0386 | 1,123 |
| 16 | 13 sur 16 | 0,0213 | 1,049 |

Plus petit déplacement détectable de `beta_u_eff`, régime `heritable`, 3 générations. Le coût en vies est entre parenthèses.

| Génomes `N` | 8 populations | 12 populations | 16 populations |
| --- | --- | --- | --- |
| 6 | 1,026 (1 728) | 0,601 (2 592) | 0,561 (3 456) |
| 12 | 0,785 (3 456) | 0,459 (5 184) | 0,429 (6 912) |
| 24 | 0,575 (6 912) | 0,336 (10 368) | **0,314 (13 824)** |
| 48 | 0,430 (13 824) | 0,251 (20 736) | 0,235 (27 648) |

L'écart-type de `beta_u_eff` entre génomes fondateurs vaut 0,667. Le seuil déclaré d'une moitié est donc 0,333.

## 4. Signalement : asymétrie de la quantité composée

Pour `beta_u_eff`, la part des contrastes positifs s'écarte de 0,5 de plus de quatre erreurs types dans deux configurations du régime `heritable` : 0,466 pour 24 génomes et 8 générations, 0,468 pour 48 génomes et 8 générations. La moyenne du contraste y reste nulle.

Explication proposée **(hypothèse)** : `beta_u_eff` est un produit de deux gènes, dont la loi est étirée vers les grandes valeurs. Quand le bras `selected` se réduit à un ou deux fondateurs, sa moyenne se comporte comme un tirage unique de cette loi, plus souvent sous la moyenne qu'au-dessus.

Conséquence pour le protocole : un test de signe sur `beta_u_eff` n'est correctement calibré que si les lignées gardent plusieurs fondateurs. Aux configurations à 3 générations, aucun écart n'est détecté (part positive de 0,503 pour 24 génomes dans le régime `heritable`).

## 5. Recommandation selon la règle déclarée

- **Seuil d'une moitié (0,333) : 16 populations, 24 génomes par population, 3 générations.** Le seuil de signe est 13 sur 16. Le plus petit déplacement détectable est 0,314 pour `beta_u_eff` et 0,138 pour un gène normalisé. Le coût est de 13 824 vies, soit au plus 5 529 600 pas.
- **Seuil d'un quart (0,167) : aucune configuration de la grille.** La meilleure, 16 populations de 48 génomes sur 3 générations, détecte 0,235 pour 27 648 vies.

La configuration à 12 populations de 24 génomes manque le seuil d'une moitié de très peu (0,336 pour 10 368 vies). Le choix entre les deux revient au propriétaire.

## 6. Ce que ce résultat change

1. **Le dimensionnement avancé dans la proposition de feuille de route était trop faible.** Elle évoquait 8 à 12 populations de 6 génomes sur 4 à 6 générations, soit 2 304 à 5 184 vies. Avec 12 populations de 6 génomes sur 6 générations, le plus petit déplacement détectable serait 0,846, soit 1,27 fois l'écart-type des fondateurs. Un tel essai n'aurait presque rien pu voir.
2. **Peu de générations, des populations plus grandes.** Avec cette règle de parents, allonger la lignée ajoute du bruit, et rien ne garantit que le signal croisse plus vite. Trois générations et 24 génomes sont le point de départ proposé.
3. **Seize populations plutôt que huit.** À coût égal (13 824 vies), 8 populations de 48 génomes détectent 0,430, contre 0,314 pour 16 populations de 24 génomes.
4. **La recombinaison prévue pour l'étape 6 complète prend un sens précis** : elle ralentirait la perte de fondateurs. Ce point n'est pas modélisé ici.

## 7. Limites

- Le modèle ne dit rien de la réponse réelle à la sélection. Un essai dimensionné ainsi peut rendre « non observé » si le déplacement réel est inférieur à 0,31.
- Le seuil d'une moitié est un choix de conception **(hypothèse)**.
- Le plus petit déplacement détectable repose sur une approximation normale du contraste par population.
- Le régime `heritable` est une borne de travail. L'héritabilité réelle de la persistance n'est pas mesurée.
- Le modèle suppose la règle de parents de P3 généralisée à `N` et la mutation de `genome.mutate`. Tout autre choix demande un nouveau calcul.

## 8. Handoff

| Rubrique | Contenu |
| --- | --- |
| Génération | I3, proposition non enregistrée |
| Commits | préflight `d1437b301793858170cfc5a3e989ca44e5c79d33` ; code et tests `f05a444d6bf57d75c7eff60993498ca8f3c7c73c` ; ce rapport dans le commit suivant |
| Invariants | le module n'importe aucun module `i3` ; aucun fichier de `modules/` ou de `runtime/` ; ni registre, ni `engine.json`, ni `ACTIVE_SURFACE.json`, ni ADR |
| Tests | `tests/i3/test_stage6_light_drift_null.py` : PASS en Python 3.12.3, en local. Python 3.11 : NOT_RUN, interpréteur absent. CI GitHub : NOT_RUN. |
| Statut scientifique | Inchangé. Aucune vie, aucun verdict. |
| Prochaine étape falsifiable | Brouillon de protocole de l'étape 6 légère, puis transport et répétition scellée sur la cohorte `engineering` |
