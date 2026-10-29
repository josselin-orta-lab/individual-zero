# Individual Zero: constat post hoc A1-C, crédit instrumental et signe de récompense

**Nature : diagnostic exploratoire en lecture seule, jamais une validation L3.**
Origine unique : [cohorte confirmatoire A1-C #40944104333](https://github.com/josselin-orta-lab/individual-zero/actions/runs/40944104333), commit source `26f7929b6db43f68e78b0cc0d9c67e7444f924c6`. Préenregistrement #617 antérieur aux 48 vies. **Verdict A1-C inchangé : NO-GO pour L3 ciblé; L3 général NOT_ESTABLISHED.**

48 archives ZIP M11 originales contrôlées par leurs SHA-256 publiés ; leurs événements ont été parcourus en lecture seule, vérification des chaînes SHA-256, des 48 générations, des identités, des commandes et des transitions physiques; les scores ECO-v1 ont été recomposés à partir des transitions et confrontés au reçu audité. Aucun individu n'a été recréé.

## Découverte reproductible

- **195/195 commandes `collecter`** obtiennent une baie et diminuent la nourriture corporelle. Au même pas, le score ECO se dégrade pour 181 collectes, ne change pas pour 14, ne s'améliore pour aucune.
- **195/195 collectes produisent néanmoins un retour TD positif** au cycle décisionnel suivant, avec la bonne signature `i1:affordance:collecter:target=berry_*`, `segment_length=1` et concordance de `return_g` avec la récompense physique recalculée (tolérance 1e−7). Récompense moyenne **+1,228718**.
- Décomposition moyenne de la récompense par besoin, à partir des poids effectivement nés : énergie **+1**, eau **+0,4**, nourriture **−0,171282**, intégrité **0**. Toutes les collectes se produisent lorsque l'énergie et l'eau dépassent leurs `setpoints`. La formule `ValueAndNeeds.reward_between` utilise la réduction de la **distance absolue** aux cibles, contrairement au score ECO qui n'intègre que les **déficits au-dessous**. Une diminution passive d'énergie et d'eau au-dessus des cibles peut donc être récompensée alors que la nourriture diminue.
- 195 collectes débouchent sur **113 ingestions réelles** avant H48, appariées par espèce FIFO à l'inventaire (ce qui n'identifie pas une baie physique unique); **82 collectes** restent non consommées à H48. **61/113** appariements ont un délai ≥5 pas.
- Pour les **112 ingestions suivies d'une publication TD**, la signature d'une collecte de la même baie figure dans `updated_signatures` **112/112**. La 113e ingestion survient au pas 48 et aucune décision ultérieure n'est publiée. Les traces d'éligibilité existent donc, contrairement à l'hypothèse d'une absence totale; leur **amplitude et contribution exacte** restent NON OBSERVÉES.
- Dans ces 48 vies, 574 pas `dormir` pour I1 canonique contre 876 pour TD masqué, mais **ce seul constat ne démontre pas la médiation causale** par le sommeil.

## Interprétation et bornes

L'écart entre récompense TD absolue pondérée et score de déficit est vérifié dans les événements M11. Il ne prouve pas que la récompense devrait être remplacée, ni que ce point explique à lui seul le NO-GO, ni que le niveau général L3 est acquis. Ne **pas** modifier rétrospectivement `lambda_e`, le moteur, les mondes, les seuils ou les individus. Préférer une investigation prospective séparée des deux questions : (1) cohérence de la récompense avec les conséquences physiques réellement apprises; (2) contribution chiffrée du crédit retardé `collecter → manger` au choix en Competition. L'observateur Q avant masque n'est pas une observation native M11 signée.

Dossier scientifique original, fichiers de diagnostic et tests adversariaux disponibles comme pièces jointes du compte rendu de campagne dans la conversation. Compte rendu associé à [l'issue #305](https://github.com/josselin-orta-lab/individual-zero/issues/305), sans nouvelle CI lourde ni nouvelle cohorte.