# Stage8-E3B · pourquoi les individus G2 cessent-ils de décider ?

**Clôture du 20 novembre 2026 : `READONLY_ALL_36864_ORIGINAL_FUNDING_REASONS_IDENTIFIED_POSTHOC`.** Diagnostic **descriptif**, exploratoire et calculable à partir des vies historiques ; **zéro naissance, aucune relance de World ni mutation génétique, aucun nouveau test de causalité**. Le verdict prospectif Stage8-E2 est et demeure **`STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0 / CLOSED_NO_RETRY`**. Le résultat Stage8-E3A, qui avait identifié des différences de motricité/cognition, demeure également descriptif.

## Provenance et deux relectures indépendantes

- [Exécution historique scientifique source-verrouillée Stage8-E2 #44637950471](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44637950471), moteur intact `03faff4b9c194a5288b92e394f6a75cbe62cd095` et source SHA-256 `e816ff5f5ee679253fc57f6e9ee79d21dff73dd72d6adf3c7f55ba7aa0f3e7f6`, trois générations scellées, troisième racine scientifique indépendante. Les originaux G2 ont déjà été réaudités intégralement en Stage8-E2 et E3A, aucune nouvelle cohorte n'a été créée pour ce diagnostic.
- [Workflow one-shot E3B #44715847132](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44715847132) sur source `06696cc6cd4af8328a8655ad738c70ce33c10745`, **3/3 jobs PASS, run_attempt=1** : préflight, lecture exacte de **36 864 gzip originaux G2 et leurs 36 864 SHA-256 décompressés**, traces corporelles à chaque pas, chaîne de cognition payée, puis **réduction arithmétique indépendante Python 3.12 sur les 64 populations**.
- Artefact brut G2 historique `stage8e2-science-G2-original-gzip-44637950471` (ID **14601222013**), manifeste G2 SHA-256 `61eb74a1f429c2f9189ee13da5c52593776d2b6f9d2b2d8ac41bfdea31a6ba00` ; E3A original `STAGE8E3A_FULL.json` SHA-256 `16e69fdcb664f73b7d67fa6e620017dc30e78bec834ddb148a2c58c6b0939d8b` et contrôle E3A `16040d0da069ac25bb3be014729a129f1202d2f7812b13c688466013f45be027`.
- Artefact E3B original `stage8e3b-36864-original-decision-funding-causes-44715847132` (ID **14620362634**) : `STAGE8E3B_FULL.json` SHA-256 **`c0709ad5ff8491538eab5fcb4f93bd854502d3aec9714878550426a88a179720`**, **64×4 cellules complètes et 8 métriques** ; artefact indépendant `stage8e3b-independent-funding-cause-populations-44715847132` (ID **14620078363**) : `SECOND_E3B_REDUCTION.json` SHA-256 **`9ab20385db8529b2596d54d931a5107edf34b7cfb7287af8a805afda6e7e6f84`**.
- Troisième contrôle indépendant hors CI des **deux JSON téléchargés**, de leurs empreintes, des **256 cellules population×bras**, des comptes et des huit contrastes, directement recalculés depuis les lignes originales. Ce contrôle supplémentaire ne prétend PAS avoir retéléchargé les 1,49 Go de gzip originaux : cela a été fait par le job à froid précédent. Aucun original G2 n'est éliminé selon le signe du résultat.

## Les causes originales de chaque action `None`

Les quatre catégories sont les **valeurs de `life.trace[t].info.funding` effectivement produites par le moteur**, sans reconstitution imaginative des actions manquées :

- `FUNDED` : une action physique a été admise et exécutée.
- `NO_PROCESSING_BUDGET` : l'individu ne peut pas payer le premier traitement nécessaire à une décision ; l'action physique n'est pas exécutée (`None`).
- `NO_FUNDED_SCORE` : le calcul n'a pas réussi à produire de score finançable ; `None`.
- `NO_FUNDED_MOTOR` : des plans ont été évalués, mais le contrôle moteur les a tous rejetés ; `None`. **Ce dernier libellé n'est pas une preuve de manque d'énergie à lui seul.**

**Comptes exacts de pas sur les 36 864 vies G2** (total **9 211 248 pas vécus** ; 144 vies par cellule population/bras) :

| Résultat enregistré | S_sham | S_swap | M_sham | M_swap |
| --- | ---: | ---: | ---: | ---: |
| `FUNDED` | 1 947 123 | 1 892 800 | 1 778 416 | 1 794 593 |
| `NO_PROCESSING_BUDGET` | **388 295** | **443 906** | **489 866** | **474 164** |
| `NO_FUNDED_SCORE` | 263 | 288 | 329 | 325 |
| `NO_FUNDED_MOTOR` | 195 | 214 | 223 | 248 |
| Total de pas observés | 2 335 876 | 2 337 208 | 2 268 834 | 2 269 330 |

**1 796 231** des **1 798 316** pas d'inactivité (`None`) proviennent de `NO_PROCESSING_BUDGET`, soit **≈99,884 %**. Les deux autres portes représentent ensemble **2 085 pas** (≈0,116 % des inactivités), et ne sont donc pas la source principale de l'inactivité de cette cohorte.

## Comparaison entre bras : préserver l'unité de population

Les pourcentages ci-dessous sont les **moyennes des 64 taux population×bras à poids égaux**, chacune calculée sur les pas effectivement vécus par **144 vies**. Les comptes bruts ci-dessus ont des dénominateurs d'exposition légèrement différents ; il ne faut pas substituer un test basé sur 9,2 millions de pas à **64 populations**.

| Mesure par pas vécu | S_sham | S_swap | M_sham | M_swap |
| --- | ---: | ---: | ---: | ---: |
| `NO_PROCESSING_BUDGET` | **16,8184 %** | **19,1168 %** | **21,8283 %** | **21,2118 %** |
| `NO_FUNDED_SCORE` | 0,01167 % | 0,01241 % | 0,01478 % | 0,01449 % |
| `NO_FUNDED_MOTOR` | 0,00850 % | 0,00924 % | 0,01005 % | 0,01126 % |
| `FUNDED` | 83,1614 % | 80,8615 % | 78,1469 % | 78,7624 % |

Contraste descriptif de l'inactivité Stage8-E3A : **−2,9154785 points de pourcentage**. `NO_PROCESSING_BUDGET` en reconstruit **−2,9149084 points** ; donc **99,98045 % de ce contraste descriptif** est porté par cette porte précise. Les autres deux portes, sommées, ne le modifient que de **≈0,00057 point**. Le second calcul indépendant retrouve ces chiffres exactement et toutes les **64 observations de chaque contraste**.

Pour les **20 premiers pas observés** : dans **256 cellules population×bras sur 256**, `FUNDED=100 %` et les **trois causes d'inactivité sont strictement à 0**. Cela signifie que l'impossibilité de payer la décision apparaît **après le début de la vie**, pas dès la première période observée. Cela n'établit pas un délai de défaillance universel, car les vies ont des durées différentes.

## Énergie ou vigilance : chaîne logique identifiable

Le moteur natif [`Mind.decide`](https://github.com/josselin-orta-lab/individual-zero/blob/03faff4b9c194a5288b92e394f6a75cbe62cd095/src/i3/modules/mind.py) commence par un financement d'**au moins trois cycles** de cognition et de mémoire : `budget.try_spend(CognitiveWork(cycles=3, memory_items=slots))`. Les [lois corporelles v2](https://github.com/josselin-orta-lab/individual-zero/blob/03faff4b9c194a5288b92e394f6a75cbe62cd095/src/i3/modules/body.py) facturent ces trois cycles à **0,06 unité d'énergie**, plus **0,0002 par objet mémoire**, et à **0,15 unité de vigilance** (sans supplément de vigilance par objet mémoire). Le code n'invente pas un autre motif : si le paiement initial est refusé, `Mind.decide` retourne `NO_PROCESSING_BUDGET` et le moteur applique une inactivité physique à ce pas.

**Observation des réserves immédiatement avant la décision** sur tous les `NO_PROCESSING_BUDGET` : **100 %** avaient moins de **10 unités d'énergie**, **0 %** avaient moins de **10 unités de vigilance**. Moyennes pondérées par nombre de pas pour cette porte :

| Réserve juste avant `NO_PROCESSING_BUDGET` | S_sham | S_swap | M_sham | M_swap |
| --- | ---: | ---: | ---: | ---: |
| Énergie | **0,05110** | **0,05126** | **0,05051** | **0,04949** |
| Vigilance | 93,66 | 93,81 | 93,64 | 93,93 |

Puisque la vigilance est **toujours supérieure à 10**, elle est largement suffisante pour le paiement initial de **0,15** dans tous ces cas ; le facteur qui rend **ce premier paiement impossible** est donc **l'énergie**, y compris la part variable du stockage mémoire. C'est une **explication mécanique déterministe** de l'absence de commande motrice une fois cette réserve épuisée, pas une corrélation vague entre valeurs finales. Les coûts exécutés demeurent intégralement facturés ; il n'y a ni calcul gratuit ni action imposée.

**Limite capitale :** ce constat ne prouve PAS que l'échange gamma a **causé** l'épuisement énergétique, ni que l'énergie serait une **médiatrice causale** de l'effet sur la persistance. Les individus plus longtemps vivants exposent aussi davantage de pas au vieillissement, et l'intervention a échangé simultanément gamma1/gamma2/gamma3 avec RNG individuelles distinctes.

## Piste explicative et prochaine question falsifiable

Un [diagnostic supplémentaire fondé sur les 1 536 génomes archivés et le code P1.3](STAGE8E3B_POSTHOC_GAMMA3_ANTICIPATORY_REACH_2026-11-20.md) montre que `gamma3` est transformé en portée d'anticipation des besoins eau/nourriture par `min(255,int(1/(1−gamma3)))` ; **1 505/1 536** paires échangées changent cette portée, de **68,9 pas en valeur absolue moyenne**. Une association descriptive existe entre sa variation populationnelle et la variation d'inactivité, mais les corrélations sont **exploratoires multiples**, sans isolation causale de gamma3.

**Suite falsifiable sans naissance :** relire les mêmes traces, cette fois en **fenêtres temporelles fixées à l'avance** (`t=1–20, 21–100, 101–200, 201–400`) et pour le **premier instant de `NO_PROCESSING_BUDGET` par vie**. Comparer le stock d'énergie, trois composantes (sommeil `dormir`, cognition facturée, activité motrice) et les besoins hydriques réels au début de la défaillance, à population/bras appariés, sans traiter les pas tardifs comme indépendants. Publier les fenêtres y compris si les différences sont nulles ou opposées, sans p-values ni sélection de cohortes. Ne pas fabriquer de contrefactuel individuel.

**Erratum méthodologique prospectif, sans réécrire Stage8-E2 historique :** les plages natives du génome v4 sont `gamma1 ∈ [0,60 ; 0,90]`, `gamma2 ∈ [0,90 ; 0,98]`, `gamma3 ∈ [0,98 ; 0,998]`. L'ordre `gamma1≤gamma2≤gamma3` est donc **automatiquement conservé si l'on échange gamma3 SEUL** entre deux génomes valides. Test purement génétique sur les 1 536 paires originales : **1 536/1 536 échanges gamma3-only valides**, dont **1 533** modifieraient effectivement la coordonnée. Le texte de conception historique ayant motivé le bloc indivisible par la seule contrainte d'ordre est donc **trop restrictif** ; il reste immuable comme document préenregistré de la campagne passée, et cette correction ouvre seulement une **nouvelle option prospective**, non un résultat Stage8-E2 rétroactif. Une expérience de causalité gamma3 seul exigerait une nouvelle hypothèse et une nouvelle racine scientifique indépendante, précédée de deux répétitions techniques propres, sans réemploi des graines historiques.

**Statuts inchangés :** `STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0 / CLOSED_NO_RETRY` ; Stage2 général `NOT_ISSUED/HOLD_NO_VERDICT` ; I1 actif, i3 non promu ; preuve laboratoire interne, aucune attestation externe. Conserver les originaux gzip hors des **90 jours** GitHub Actions reste un chantier distinct : [#1463](https://github.com/josselin-orta-lab/individual-zero/issues/1463).
