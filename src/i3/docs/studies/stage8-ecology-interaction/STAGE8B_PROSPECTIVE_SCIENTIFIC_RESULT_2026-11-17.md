# i3 Stage8-B : résultat prospectif et seconde vérification des 23 040 vies originales

**Date des observations : 17 novembre 2026. Verdict scientifique primaire : `STAGE8B_NO_INTERACTION_DEMONSTRATED_F0`. Étude `CLOSED_NO_RETRY`.**

Ce document a été créé **après** l'unique exécution source-verrouillée et **après** l'audit indépendant brut. Il ne modifie ni le [protocole antérieur à l'exposition](STAGE8B_PROSPECTIVE_ECOLOGY_HELDOUT_PROTOCOL_2026-11-17.md), ni le test primaire, ni les vies, ni l'allocation, ni le moteur. Les résultats nuls et défavorables restent dans les archives.

## Provenance réellement exécutée

- **Campagne prospective unique** : [GitHub Actions #44060101150](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44060101150), tentative 1, source `9f94d1c2c4170fd923ea0de68761bed2ac3d8377`, `completed/success` le 17 novembre 2026 à 14:31 UTC. Deux répétitions techniques Python 3.11 et 3.12 ont terminé avec succès **avant** la cohorte scientifique ; chacune a produit 23 040 vies techniques distinctes. Ces répétitions ne sont **pas** des réplications scientifiques de l'effet.
- **Plan scientifique publié avant naissance** : artifact `stage8b-science-preexposure-44060101150` (`14329303886`), publié le 17 novembre à 12:52:10 UTC, allocation SHA-256 `0992af3e1f14d4d460e6046a03a278c2fb1d4d2979f2fc1ce695ed2eed25ed52`.
- **Sources scientifiques finales** : artifact `stage8b-science-result-44060101150` (`14337621478`) et 23 040 gzip natifs, artifact `stage8b-science-originals-44060101150` (`14336778972`). Les neuf artifacts du run étaient disponibles et non expirés à la vérification.
- **Audit indépendant, en lecture seule** : [Actions #44126032148](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44126032148), tentative 1, source d'audit `1a28bc9cbe25187a3c95c92f667a8295a8be66c7`, `completed/success` le 17 novembre à 16:32 UTC ; artifact `stage8b-original-level-independent-audit-44126032148` (`14346689726`). Cet audit réutilise un vérificateur structurel Stage7 mais **pas** le réducteur Stage8-B scientifique.

## Verdict préenregistré : interaction sélection parentale × écologie

Les **32 populations** sont les unités d'inférence. Pour chacune, le protocole compare en G2 la durée moyenne des descendants de parents sélectionnés selon leur persistance et celle des descendants de parents tirés uniformément, dans les **mêmes opportunités de World F0**. Les différences entre trois familles sont soumises à un test omnibus Hotelling T²/F(2,30), avec seuil strict `p < 0,025`, fixé avant naissance. **La statistique principale interroge l'interaction écologique, pas la seule existence d'un gain moyen.**

| Famille F0 | Différence moyenne G2 sélectionné − uniforme (pas) | Populations avec contraste positif / 32 |
| --- | ---: | ---: |
| `stable` | +16,0963541667 | 25 |
| `depletion` | +14,3743489583 | 25 |
| `pulse` | +18,0735677083 | 27 |

**Omnibus : `p = 0,6577705128174012`**, très supérieur à 0,025. Le critère primaire n'est donc **pas atteint** : `STAGE8B_NO_INTERACTION_DEMONSTRATED_F0`. Les 32 profils et tous les cas défavorables restent inclus. La moyenne descriptive non primaire des trois familles est +16,1814236111 pas ; elle **ne convertit pas** Stage8-B en succès d'interaction et les comptes par famille ne sont pas trois tests confirmatoires.

Une absence d'interaction significative **ne prouve ni l'égalité ni l'équivalence** des écologies, en particulier avec la dispersion anticipée et les hypothèses statistiques non vérifiées de façon indépendante. Les trois familles appartiennent à F0 ; aucune généralisation hors F0 n'est démontrée.

## Vérification des gzip originaux, distincte des sorties agrégées

Le journal de l'audit `independent_original_audit` atteste explicitement :

- `status = READ_ONLY_ORIGINALS_REPRODUCED`, `scientific_status = STAGE8B_NO_INTERACTION_DEMONSTRATED_F0` ;
- `native_original_lives_rehashed = 23040` (G0/G1/G2, deux panneaux de 16 populations), `g2_family_lives_rehashed_again = 9216` (seconde lecture écologique G2) ;
- `populations_verified = 32`, deux chaînes de phases scellées, 192 mondes G2 préalloués vérifiés via le plan, vie bornée à l'horizon 400, morts distinctes des censures ;
- statistiques familiales et `omnibus_p` recalculés indépendamment depuis les enregistrements gzip, **avec `new_worlds = 0` et `new_lives = 0`**. Les tests synthétiques et toutes les étapes du workflow d'audit ont réussi.

L'audit valide des hashes et reconstitue des résultats à partir des corps archivés. Il ne rejoue pas la physique ou la politique motrice, ne constitue pas une attestation hors hébergeur et ne prouve ni la normalité multivariée ni l'indépendance causale des 32 populations. Il ne doit pas être présenté comme une deuxième expérience scientifique.

## Décision et suite

Stage8-A demeure **positif** sur son **autre** critère préenregistré de gain moyen G2 (+14,4874 pas), avec neuf populations globalement défavorables. Stage7 demeure **négatif** selon sa règle 13/16. Stage8-B est **négatif** sur l'interaction F0 ; aucune de ces décisions n'annule les autres.

**Suite proposée** : [Stage8-C : contrôle par multiplicité parentale strictement appariée](../stage8-parent-concentration/STAGE8C_CONTROL_DESIGN_2026-11-17.md), question de mécanisme **nouvelle et non encore préenregistrée**. Ne pas relancer les cohortes Stage6/Stage7/Stage8-A/Stage8-B ; source, graines, contrôle, seuil et deux répétitions d'ingénierie d'une future étude devront être fixés avant toute nouvelle vie.

Provenance : `INTERNAL_PROSPECTIVE_NOT_EXTERNALLY_ATTESTED`. Le moteur I1 demeure actif ; I3 est référence de développement non enregistrée, et la décision Stage2.1 scientifique reste `NOT_ISSUED/HOLD_NO_VERDICT`. Les archives GitHub sont soumises à rétention : en conserver les ZIP et empreintes pour la pérennité.
