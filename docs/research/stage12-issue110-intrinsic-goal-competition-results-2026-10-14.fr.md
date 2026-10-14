# Stage12 issue #110 : résultats de sensibilité intrinsèque P-15, 14 octobre 2026

**Préenregistrement antérieur au code :** `54a7c25`. **Source exécutée :** `060339e33fc04e57b110613edbeb16f95e5a03bd`. [GitHub Actions #38559450457](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38559450457), **PASS Python 3.11 et 3.12**, 12 vies uniques × 36 transitions physiques = **432 pas uniques**. Même protocole et identités de naissance réexécutés sous deux versions, donc l'effectif ne double pas. Toutes les vies sont journalisées et passées par les audits locaux WAL, Action Control, objectifs, agence, paires et A2 sans erreur.

| P-15 (w_m) | Vies | Motifs active_goal | Commandes se_deplacer | Commandes dormir | Commandes attendre | Jugements self/world/unknown | Paires appliquées | Vies 2+2 évaluables |
|---|---:|---:|---:|---:|---:|---|---:|---:|
| 0.75 référence | 4 | 6 | 104 | 36 | 0 | 3 / 1 / 2 | 3 | 0 |
| 0.35 intermédiaire | 4 | 0 | 70 | 74 | 0 | 0 / 0 / 0 | 0 | 0 |
| 0.00 ablation | 4 | 0 | 0 | 96 | 48 | 0 / 0 / 0 | 0 | 0 |
| **Total externe** | **12** | **6** | **174** | **206** | **48** | **3 / 1 / 2** | **3** | **0** |

Tous ces totaux sont des résultats de 12 vies **indépendantes**, pas une fenêtre interne du détecteur Stage12. Aucun détecteur `attribution_bias` n'a pu être évalué dans une vie : même le bras témoin n'atteint pas 2 success + 2 failure dans 12 observations.

Par vie, le témoin 0.75 `restored_free` obtient 3 engagements, 2 self, 1 unknown et 1 couple appliqué ; `restored_a2` produit 3 engagements, 1 self, 1 world, 1 unknown et 2 couples appliqués. Les mondes sustained à 0.75 ont 0 engagement. Tous les mondes à 0.35 et 0.00 ont **0 engagement**. Le bras à 0.35 conserve des mouvements, mais dort beaucoup davantage ; à 0.00, les vies n'effectuent que `dormir` et `attendre`, sans exploration effective ni poursuite de but.

## Interprétation

**L'hypothèse selon laquelle réduire P-15 rétablirait la poursuite du but est réfutée dans cette campagne.** Les paramètres préenregistrés 0.35/0.00 ne restaurent aucun sous-objectif `sustained` et dégradent même le scénario alimentaire `restored` initialement fonctionnel. P-15 faible réduit l'exploration utile, avec davantage de sommeil/attente, sans accroître les attributions. Une politique simple de réduction du poids intrinsèque **n'est donc pas recommandable**.

Le rang géographique plus élevé au pas 2 est démontré dans la campagne précédente, mais cette nouvelle expérience montre que l'arbitrage sur une vie entière est plus complexe que remplacer une option exploratoire par une option alimentaire : enlever l'un des signaux peut diminuer l'activité, modifier le sommeil, et empêcher la visite d'une ressource que la perception n'a pas encore rencontrée. Cela ne prouve pas que toute adaptation de valeur intrinsèque échouerait, seulement que ces trois conditions prédéfinies ne fournissent pas une amélioration.

La quantité globale de paires appliquées ne démontre pas une meilleure causalité : attribution naïve réussite->self/échec->world et matrice de confusion doivent attendre des résultats contrastés vérifiés en nombres suffisants. La dérive binaire Stage8 entre Python 3.11/3.12 reste une limite distincte ; seules les métriques agrégées comportementales sont identiques sous les deux environnements.

## Suite architecturale

Conserver **P-15 = 0.75** dans le scénario de référence et **aucun nouveau changement de Competition ni de MVP normatif** dans ce pilote. La prochaine enquête pertinente doit porter sur une représentation commune de la valeur prospective et des valeurs intrinsèques, ainsi que la tension entre objectifs persistants, découverte des ressources et sommeil, avec des contrôles qui distinguent exploration instrumentale utile et exploration purement intrinsèque. Tout mécanisme d'engagement introduit devra être formulé indépendamment de l'étiquetage causal et ne pourra pas requalifier rétroactivement `cible_exploration` en `active_goal`.

**Verdict : PASS logiciel des 12 vies, FAIL de l'hypothèse « diminuer P-15 facilite les objectifs », PARTIAL scientifique pour Stage12, calibration NON ÉVALUABLE.** PR #155 brouillon, issue #110 ouverte, Stage12 non reçu.
