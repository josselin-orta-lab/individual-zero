# A2.30-P : conséquences conjointes et mortalité différée, résultats reproductibles

**15 octobre 2026.** Préenregistrement des préfixes et de la matrice **avant code** : `fbc735bfef3f0b285c4eb1989a3547f5b7710957`. Modèle de laboratoire `55d9afab17fa088f2904684b5f358f67153a8b7e`, runner `8b71b65a7a90fce050646131484eab61ec1eca1b`, contrôles `d1a95823d5c221b797462b35142d5b8d51b0e7b5`. [GitHub Actions #38730415503](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38730415503) **SUCCESS Python 3.11 et 3.12** au SHA final d'exécution `3ab03a90b38d6c968cddcd9ed699c3f089d0544c`. Les deux versions ont réexécuté **les mêmes cellules déterministes**, et les trois sorties JSON de laboratoire sont égales octet à octet : on ne compte pas deux cohortes différentes.

## Intervention scientifique physiquement contrôlée

**48 mondes de physique pure pour l'entraînement (132 pas réellement appliqués)** et **80 mondes de test indépendants (220 pas réellement appliqués)**, soit **128 mondes indépendants, 352 transitions appliquées**. Aucun monde n'a poursuivi la séquence après une transition létale. Les trois séquences préfixes de longueur au plus 3 sont :

- `MOV = se_deplacer(east) → attendre → attendre` ; risque caché à l'est éventuellement létal immédiatement ou par dégâts de zone répétés.
- `EAT = collecter(berry_a) → manger(berry_a) → attendre` ; effet d'intégrité et gain alimentaire de la même espèce visible pouvant varier de manière cachée.
- `WAIT = attendre ×3` ; altération corporelle lente ou dégâts répétés d'une zone cachée sur la case initiale.

Les variantes cachées ne font **jamais** partie de la clé du prédicteur, qui n'exploite que l'état accessible au premier pas et la suite de commandes préétablie. Le corpus conserve **quatre branches physiques conjointes par préfixe**, leurs 11 deltas corporels/spatiaux/d'inventaire cumulés après chaque action, et la première étape terminale éventuellement attestée. `observed_terminal_possible` signifie « au moins un monde d'entraînement est devenu terminal dans cette famille », et n'est **ni** une probabilité, **ni** un jugement subjectif, **ni** une garantie d'exhaustivité.

## Résultats discriminants

| Strate de test | Mondes | Pas | Préfixes connus | Traces conjointes déjà observées | Traces inédites / abstentions |
|---|---:|---:|---:|---:|---:|
| Conditions ordinaires, faim et position nouvelles | **48** | **132** | 48 | **48/48** | 0 |
| Effets physiques cachés **nouveaux** | **24** | **64** | 24 | **0/24** | **24 branches inconnues** |
| Obstacle perceptible nouveau ou séquence jamais entraînée | **8** | **24** | 0 | 0 | **8 abstentions** |
| **Test complet** | **80** | **220** | **72** | **48** | **24 inconnues + 8 abstentions** |

**Mortalité différée :** dans les 48 mondes de test ordinaires, **16 terminaisons physiques** sont attestées, dont **12** à la deuxième ou troisième commande. Huit de ces 12 (ingestion mortelle à t2, zone dangereuse sous attente mortelle à t3) concernent des préfixes dont l'entraînement ne contenait **aucune** terminalité au premier pas. Le témoin empirique limité au premier pas ne peut donc pas fournir la temporalité terminale attestée, tandis que le témoin P l'enregistre sur le même groupe perceptible.

**Effets cachés nouveaux :** les 24 nouvelles variantes ont toutes produit une **trajectoire conjointe absente des quatre branches entraînées** pour leur contexte accessible, malgré des commandes et préconditions visibles familières. Huit mondes ont rendu le corps terminal à un **pas qui n'était pas présent** dans l'ensemble empirique de pas terminaux de ce groupe. Le modèle sait seulement conserver ce qui a déjà été observé, **et ne détecte pas spécifiquement le nouveau danger**. Aucune fausse certification de sûreté : **0 verdict `safe`**, chaque préfixe connu conservant la possibilité d'un autre danger non rencontré.

**Contrôles d'abstention :** 4 essais MOV vers un obstacle nouvellement visible et 4 essais sur la commande `se_deplacer(west)` inédite du corpus ont été refusés `abstain_unknown_context`, sans extrapolation ni commande alternative.

## Hypothèses et portée

- **P1 soutenue localement :** préservation des trajectoires conjointes effectivement observées et transfert descriptif vers des niveaux corporels et positions différents, **48/48** sur le domaine expérimental prévu. La répétition déterministe n'est pas une estimation de probabilité de réussite dans un autre monde.
- **P2 soutenue :** les pas létaux tardifs observés au laboratoire sont bien représentés dans les mêmes branches, contrairement au témoin qui ignore tout après le premier pas, sans inventer de causes internes.
- **P3 démontrée comme limitation :** 24 branches physiques nouvelles échappent toutes au catalogue empirique; 8 mortalités à un pas inédit dans le contexte connu. Les dangers latents sont épistémiquement irréductibles sans information accessible supplémentaire ou mécanisme explicite d'incertitude non calibré. Le label prudent évite de prétendre « sûr », mais **ne constitue pas une prédiction effective de la forme du risque jamais rencontré**.
- **P4 soutenue :** huit abstentions correctes, aucune instruction envoyée à un vrai I0.

**Conclusion logicielle :** le modèle de laboratoire constitue un mécanisme crédible de représentation de **conséquences jointes et différées déjà constatées**. Il ne constitue pas un modèle général de planification alimentaire. Il ne peut pas être branché directement dans `Simulator` ou `Stage6` (pas d'état suivant complet ; pas d'action recommandée ; pas de contrat `EquipmentModel`). L'entraînement via observations de la physique du laboratoire n'est pas une preuve de connaissance vécue par I0.

**Décision : A2.30 PARTIELLE, Stage12 PARTIAL, issue #110 OPEN, PR #189 DRAFT. Déploiement dans I0 : NO-GO.** L'intégration d'un nouveau moteur de conséquences ou l'amendement de v1.3.1 requiert une décision opérateur indépendante. Une vérification d'archives aveugle (A2.30-Q) est préenregistrée séparément : elle doit vérifier que la reconstruction des métriques P ne dépend pas du modèle d'origine.
