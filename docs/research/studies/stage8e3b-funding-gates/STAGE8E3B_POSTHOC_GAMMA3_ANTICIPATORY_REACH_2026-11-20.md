# Stage8-E3B · diagnostic complémentaire du rôle logiciel de gamma3 dans l'anticipation

**Date : 20 novembre 2026. Statut : `READ_ONLY_POSTHOC_EXPLORATORY / NO_NEW_LIVES / NO_CAUSAL_PROMOTION`.** Ce diagnostic descriptif est distinct de l'audit des motifs `info.funding` et ne modifie pas le verdict de Stage8-E2 : **`STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0 / CLOSED_NO_RETRY`**.

## Sources intégralement archivées

- Génotypes G2 des **quatre bras** : [Stage8-E2 science #44637950471](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44637950471), artefact métadonnées **14601206944**, `METADATA.tar / native-originals/SELECT_G2.json` ; SHA-256 des octets JSON **`b830e9e8500bdc32fa56d02bbbdac50fe1e475dad7c648ee532fb2ff57ffe3a7`**.
- Comportements G2 effectivement archivés : [Stage8-E3A original audit #44706318958](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44706318958), artefact **14615936609**, `STAGE8E3A_FULL.json` SHA-256 **`16e69fdcb664f73b7d67fa6e620017dc30e78bec834ddb148a2c58c6b0939d8b`** ; les **64 × 4** cellules contiennent les fréquences d'inactivité et actions sur les **36 864 vies** originales froidement réauditées.
- [Moteur natif P1.3 figé](https://github.com/josselin-orta-lab/individual-zero/blob/03faff4b9c194a5288b92e394f6a75cbe62cd095/src/i3/modules/mind.py), même source que les deux répétitions techniques et la science : pour l'anticipation des besoins hydriques et alimentaires, dans `Mind.decide`, **`reach = min(255, int(1.0/(1.0-self.gammas[2])))`**. Cet index est le **troisième gamma**. `reach` alimente les besoins `need_w` et `need_f`, qui interviennent dans `urgency`. Les trois gamma interviennent aussi dans la projection et la cible de mise à jour temporelle. Ce rapport **ne réduit pas le fonctionnement de gamma3 à cette seule formule**.

Toutes les extractions sont **en lecture seule** ; aucune vie, World, mémoire ou décision motrice n'est rejouée. Le résultat statistique primaire Stage8-E2 est définitivement clos.

## Fait numérique indépendant de toute valeur de persistance

Pour chacune des **1 536 paires (population, slot)**, calculer la portée depuis `S_sham.gamma3` et `S_swap.gamma3` selon la formule exacte du moteur ; revalider d'abord la permutation réciproque `S_swap.gamma3 == M_sham.gamma3` et `M_swap.gamma3 == S_sham.gamma3`. Toutes les **6 144 copies G2** sont présentes.

| Paramètre descriptif | Valeur observée |
| --- | ---: |
| Paires dont le triplet gamma a été échangé de façon non triviale | **1 536 / 1 536** |
| Paires dont `reach` change | **1 505 / 1 536 (97,98 %)** |
| Paires conservant la même portée | **31**, dont 22 simultanément saturées à 255 |
| Moyenne `|Δgamma3|` entre S et M sham | **0,00607013** |
| Moyenne `|Δreach|` entre versions sham/swap | **68,9043 pas** |
| Médiane `|Δreach|` | **48 pas** |
| Moyenne `reach` S_sham | **108,5703** |
| Moyenne `reach` S_swap | **117,3874** |
| Génotypes S_sham déjà saturés à 255 | **153 / 1 536** |
| Génotypes S_swap saturés à 255 | **198 / 1 536** |

**Conséquence correcte :** la faible différence brute de `gamma3` dans ce domaine `[0,980 ; 0,998]` n'implique PAS une faible variation de la portée interne. La fonction `1/(1−gamma3)` amplifie les différences avant saturation à 255. **Ce sont des différences calculées à partir du code et des génotypes ; ce ne sont pas des mesures du temps de prévision réellement dépensé ni de l'effet sur la survie.**

## Association exploratoire avec un comportement effectivement vécu

Définir pour chaque population l'exposition génétique moyenne `X[p] = mean_slots(reach(S_swap)−reach(S_sham))`. Les observations motrices par population sont les taux E3A `Y_S[p]=inactivité(S_swap)−inactivité(S_sham)`, `Y_M[p]=−(inactivité(M_swap)−inactivité(M_sham))`, et le DID descriptif d'inactivité `Y_DID[p]=(S_sham−M_sham)−(S_swap−M_swap)`. Calculer les corrélations de Pearson **sans p-values, et sans nouvelles unités fictives**.

| Variation génotypique moyenne par population (S_swap−S_sham) | `r(X,Y_S)` | `r(X,Y_M)` | `r(X,Y_DID)` |
| --- | ---: | ---: | ---: |
| `gamma1` | +0,186 | +0,126 | −0,182 |
| `gamma2` | +0,210 | +0,328 | −0,318 |
| `gamma3` | +0,751 | +0,548 | −0,761 |
| Portée calculée depuis `gamma3` | **+0,717** | **+0,609** | **−0,778** |

Ces quatre comparaisons ont été décidées **après** observation des résultats Stage8-E3A. Les valeurs `gamma1`, `gamma2`, `gamma3` et la portée calculée ne sont pas des interventions indépendantes : le **bloc entier gamma123 a été échangé simultanément**, et les différences de durée de vie peuvent créer une sélection des pas observés. **Ces corrélations ne sont ni un effet causal de gamma3, ni une médiation de gamma3 par l'inactivité, ni un second test confirmatoire.** Elles servent exclusivement à définir un mécanisme candidat falsifiable à étudier ultérieurement avec de nouvelles unités et une intervention prospective distincte.

L'inactivité enregistrée dans les **20 premiers pas observés** vaut 0 dans les 256 cellules `population × bras` ; les différences globales d'inactivité apparaissent plus tard, où l'épuisement des budgets de cognition et les refus moteurs peuvent intervenir. L'[audit à froid Stage8-E3B des catégories `info.funding`](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44715847132) cherche ces causes exactes, sans relance de vie.

## Borne méthodologique et traçabilité

Formule de reproduction (lecture de données seulement) :

`REACH(gamma3) = min(255, int(1.0/(1.0-gamma3)))`

Les 64 `X[p]` sont calculés avec moyenne **sur les 24 couples** de chaque population. Les 64 `Y[p]` viennent **de l'archive native E3A**, agrégée sur 144 vies par population/bras. Ni les 1 536 couples ni les 36 864 vies ne sont des unités indépendantes de cette corrélation. Aucun test, échantillonnage favorable, interaction ou seuil significatif n'est introduit.

**Décision maintenue :** `STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0 / CLOSED_NO_RETRY`, Stage2 général `NOT_ISSUED/HOLD_NO_VERDICT`, I1 actif, i3 non promu. Les archives originales restent soumises à la rétention GitHub Actions (pérennisation : [issue #1463](https://github.com/josselin-orta-lab/individual-zero/issues/1463)).
