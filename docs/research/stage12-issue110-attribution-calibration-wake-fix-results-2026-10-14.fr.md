# Issue #110 : correction des perceptions au réveil et seconde calibration exploratoire

Date : 14 octobre 2026. Référence source vérifiée : `5ff6cde7db3ed6a3229e760d15299c60094e37b9`. CI : [GitHub Actions #38531111379](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38531111379), **PASS Python 3.11 et Python 3.12**. Quatre vies indépendantes, 16 pas chacune, donc **64 transitions physiques**, non 128 (deux interpréteurs réexécutent les mêmes cas).

## Défaut et correctif

Le Stage10 sérialisait manuellement la perception lors du premier pas réveillé, alors que le Stage3 ajoutait `agency_capture_schema`, `agency_visible_inventory` et `agency_visible_adjacent` lorsqu'Action Control avait un producteur de jugement subjectif actif. Lors du scénario `clear_at_4`, Action Control pouvait consommer la vraie capture du réveil mais le journal ne permettait pas à l'auditeur read-only de l'authentifier. Ce désaccord était un **défaut de reçu de perception**, et non une permission de supprimer le contrôle épistémique.

Correctifs : `src/lab/stage3_runtime.py` expose un sérialiseur commun `_perceptual_capture_receipt`; `src/lab/stage10_runtime.py` l'utilise pour le réveil. Il n'y a ni seconde observation, ni information Oracle, ni état caché supplémentaire, ni relâchement de l'auditeur. Les reçus historiques sans agence conservent leurs anciens champs.

## Résultats réels (auditeurs concordants, SHA identiques sous Python 3.11 et 3.12)

| Condition préprogrammé avant naissance | Pas | self | world | unknown | Couples admis | Couples consommés | Erreur d'audit |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| libre | 16 | 2 | 0 | 1 | 2 | 1 | aucune |
| obstacle fixe dès t2 après admission | 16 | 0 | 1 | 0 | 1 | 1 | aucune |
| obstacle t2 retiré à t3 | 16 | 2 | 0 | 2 | 2 | 1 | aucune |
| obstacle t2 retiré à t4 | 16 | 1 | 1 | 1 | 2 | 1 | aucune |
| **Total externe, uniquement descriptif** | **64** | **5** | **2** | **4** | **7** | **4** | **aucune** |

Les paires ne peuvent **pas** être mises en commun au sein d'une seule fenêtre du détecteur I0 : chacune appartient à une naissance indépendante. Une seule paire consommée par vie n'atteint ni 2 succès ni 2 échecs dans une fenêtre de 12 captures. **0/4 vies évaluables ; `attribution_bias` indisponible.**

Cette campagne vérifie que le rejet de capture disparu provient bien de la sérialisation au réveil. Elle **ne prouve pas** qu'I0 corrige systématiquement ses attributions : le retrait à t3 et celui à t4 ne sont pas des répliques indépendantes d'une même intervention. Un `self_serving_pattern` détecté avec données suffisantes ne serait en outre qu'une association descriptive entre résultat et jugement, pas une erreur causale démontrée.

**Conclusion : PASS logiciel du correctif Stage10/12, PARTIAL scientifique pour la calibration.** Maintenir `window=12`, `bias_min_outcomes_each=2` et `threshold=0.75`. Pas de fusion #155, pas de clôture #110 et pas de réception Stage12.
