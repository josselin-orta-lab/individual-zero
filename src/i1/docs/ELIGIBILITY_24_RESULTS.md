# I1 : bilan complet des traces d'éligibilité, 24 vies

**Campagne :** [GitHub Actions #39124968808](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39124968808), SHA physique exact `26d98c47421d5047ceda37994b9faf61cb1a1aac`. 8/8 jobs techniques réussis. 24 naissances indépendantes sur WAL complètes, trois graines appariées 411/412/413, λ = 0 / 0,8 / 0,95 / 1, gain alimentaire de berry_a = 0 / +10, 300 pas par vie maximum, mort irréversible. Chaque WAL a été vérifiée contre la tête du rapport et sa chaîne. λ effectif et politique de naissance sont vérifiés.

| λ | Gain alimentaire | Individus morts avant 300 | Repas totaux | Collectes après première ingestion | Nourriture moyenne observée |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 0 | 3/3 | 6 | 0 | 12,848 |
| 0,8 | 0 | 3/3 | 6 | 0 | 12,848 |
| 0,95 | 0 | 3/3 | 6 | 0 | 12,848 |
| 1 | 0 | 3/3 | 6 | 0 | 12,848 |
| 0 | +10 | 0/3, censurés | 6 | 0 | 24,950 |
| 0,8 | +10 | 0/3, censurés | 9 | 3 | 34,567 |
| 0,95 | +10 | 0/3, censurés | 9 | 3 | 34,567 |
| 1 | +10 | 0/3, censurés | 9 | 3 | 34,567 |

Le contraste pairé gain +10 / λ0 vs λ0,8 **démontre sur ces graines un retour supplémentaire à la collecte après ingestion utile**, permis par une propagation différée de récompense, **sans priorité manger artificielle ni oracle de nutrition**. L'effet ne grandit pas avec λ0,95 ou λ1; le paramètre de référence λ0,8 ne doit donc pas être modifié sur ce résultat.

**Limite vitale déterminante :** dans les bras nutritifs λ0,8/0,95/1, deux des trois individus terminent l'horizon 300 à **eau zéro**, le troisième à eau ~60.4. Tous ont survécu au seuil observé sans démonstration de survie durable; des observations avec eau zéro ne constituent pas un maintien des besoins. La survie à 300 pas est censurée, pas un certificat d'auto-suffisance.

**Autre diagnostic sur la WAL vécue (graine 411, λ0,8, gain+10) :** action `boire` appliquée au pas 29 : eau avant **48,8**, après **88,4**; au pas 30, la TD associe `i1_water_probe:boire` à **return_g = −16,9**. Le calcul actuel `ValueAndNeeds.reward_between` somme les écarts absolus aux setpoints, dont 60 pour l'eau. Dépasser 60 transforme artificiellement un remplissage salutaire en récompense fortement négative. Cela peut pénaliser aussi les actions antérieures par les traces. Aux pas 65, 100 et 250, une option `dormir` liée à l'objectif `recover_energy` reste proposée, mais sa valeur Q négative empêche son franchissement du seuil Competition; l'individu `attendre` se prive alors d'énergie jusqu'à zéro. Les effets sont liés sans démonstration que la seule cause serait `boire`.

**Décision scientifique :** GO *local* pour existence d'un crédit instrumental différé; **NO-GO** pour apprentissage intégré qui maintient les besoins vitaux. Ne pas promouvoir λ ni fusionner la PR. [Issue #306](https://github.com/josselin-orta-lab/individual-zero/issues/306) : vérifier une récompense de *déficit seulement* plutôt que d'écart absolu en variantes de laboratoire, sur nouvelles naissances avec et sans effet alimentaire, sans modifier les moteurs canoniques. [Issue #305](https://github.com/josselin-orta-lab/individual-zero/issues/305) : problème de crédit de collecte documenté avec ce contraste. Toutes les expériences anciennes restent rattachées à leur SHA; I0, main et mortalité définitive sont préservés.
