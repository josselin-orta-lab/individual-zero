# A2.30-W : résultats prospectifs sur la discrimination alimentaire avant exposition

**15 octobre 2026.** Préenregistrement fixé AVANT le code et l'exécution W au commit `5d5f7b0bb03c822d2490fd8865bb9f9e5fe26cd7`. [GitHub Actions #38753518412](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38753518412) : **PASS Python 3.11 et 3.12** au code `aecb8d1172846620c3038a4bc10e7716ec7bde1e`, mêmes données JSON byte à byte. Le premier run #38753398353 avait un seul test négatif invalide : il falsifiait l'intégrité corporelle tout en oubliant de synchroniser sa propre copie de l'observation après ingestion. Le vérificateur rejetait cette incohérence plus tôt que prévu. Le test a été corrigé au commit `aecb8d1172846620c3038a4bc10e7716ec7bde1e`, **sans modifier les 92 mondes, les paramètres scientifiques, la logique d'observation ni la physique**.

## Protocoles réellement exécutés

**80 mondes `WorldBody` détachés** = 4 préfixes sans ingestion (immédiat, attendre×2, collecter, ouest→retour) × 5 effets internes cachés de `berry_a` × 2 niveaux initiaux de nourriture × 2 positions. Les sondes réalisent 100 commandes non alimentaires, suivies de 140 commandes de collecte/ingestion de laboratoire, soit **240 applications `WorldBody.apply`** physiquement exécutées, dont **16 ingestions terminales** arrêtées immédiatement. **12 témoins perceptifs supplémentaires** n'exécutent aucune action et comparent une différence visible d'espèce `berry_a` vs `berry_b`, ou de passabilité de l'ouest. **Total 92 mondes nouveaux, 240 pas physiques, zéro naissance I0 et zéro commande autonome.**

Le protocole fige une **histoire complète des `SimulationState` accessibles avant ingestion**, exactement après chaque sonde, puis n'utilise les informations cachées et les conséquences d'ingestion que **pour l'évaluation physique externe après décision**. Même une ingestion létale ne crée aucune observation vécue postmortem ; seul le laboratoire conserve le dernier état physique dans les reçus externes.

## Mesures discriminantes et coûts des sondes

| Préfixe de sonde | Pas physiques de sondes / 20 mondes | Coût corporel AVANT la décision, par monde | Classes perceptives distinctes | Résultats après engagement du préfixe alimentaire |
|---|---:|---|---:|---|
| Immédiat | 0 | aucun | 4 | 12 succès avec survie, 4 décès, 4 résultats insuffisants |
| `attendre` deux fois | 40 | −1 énergie, −1 nourriture, −0,4 eau | 4 | 12 succès avec survie, 4 décès, 4 résultats insuffisants |
| `collecter(berry_a)` | 20 | −0,75 énergie, −0,5 nourriture, −0,2 eau | 4 | 12 succès avec survie, 4 décès, 4 résultats insuffisants |
| Ouest puis retour | 40 | −2 énergie, −1 nourriture, −0,4 eau | 4 | 12 succès avec survie, 4 décès, 4 résultats insuffisants |
| **Ensemble** | **100** | coûts non additionnables à un seul individu | **16** | **48 succès, 16 décès, 16 insuffisances** |

**Résultat W1 :** les **160 paires** formées au sein de ces 16 classes à cinq variantes présentent toutes une **histoire d'observation pré-exposition identique**. Les cinq effets internes `benign`, `toxin_7`, `toxin_30`, `toxin_100`, `gain_zero` ne sont pas différenciés par les quatre sondes testées. La comparaison porte sur le `SimulationState` **complet**, pas sur un sous-ensemble choisi après observation. Un mécanisme prudent ne peut donc pas affirmer connaître la toxicité cachée avant ingestion dans les conditions W.

**Témoin positif W2 :** sur les quatre contextes nourriture/position, **4/4 substitutions d'espèce visible** et **4/4 modifications d'obstacle adjacent** sont effectivement distinguées avant toute action. Le banc n'est donc pas insensible aux différences *réellement publiées par la perception*. La visibilité d'une espèce ne certifie pas la sécurité de l'espèce.

**W3 :** en limitant explicitement la politique à `commettre le préfixe alimentaire après la sonde prédéclarée` ou `s'abstenir`, les 16 classes engendrent **65 536 politiques déterministes**. Une seule obtient zéro décès dans **cette matrice**, celle qui n'engage jamais le préfixe ; aucune n'obtient de nourriture avec **garantie d'absence de décès sur tous les 80 mondes**. L'expérience ne simule pas un I0 autonome, ni la possibilité de changer librement les sondes selon une politique adaptative, d'explorer d'autres aliments, ni une fréquence physique naturelle de danger.

## Frontières de la preuve

W est **prospective et originale** quant aux quatre séquences d'observation sur 80 mondes agis et 12 contrôles passifs, mais utilise les **mêmes règles déterministes `WorldBody`** et les mêmes types d'effets latents que les expériences antérieures. Rejouer la matrice à l'identique sous Python 3.11/3.12 ne crée **pas** 160 mondes physiques indépendants au sens statistique. Les commandes sont préengagées par le laboratoire, pas sélectionnées par Stage6. Le résultat n'est ni un apprentissage réel d'I0, ni un jugement subjectif d'agence, ni un diagnostic de performance UC. Le fait que trois sondes coûtent ressources corporelles sans gain de sécurité dans W ne les rend pas inutiles dans un autre environnement.

Cette expérience ne démontre **pas** qu'il est impossible de trouver une nourriture sûre par toutes les politiques. Elle démontre seulement qu'avec l'interface perceptive actuelle, les **quatre sondes autorisées testées** ne rendent pas visibles les causes latentes de toxicité `berry_a` dans ces cellules, y compris lorsque les témoins de visibilité sont fonctionnels.

## Traçabilité et décision

Les trois artefacts d'origine sont accessibles sur le [run #38753518412](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38753518412) ; hashes SHA-256 du contenu JSON, identiques sur les deux Pythons :

- `a230w-acted-physical-worlds.json` : `999b0ade7734b5591e26eec0c4e2fbfa57a8d6742f5aa229476df9b8caca1889`.
- `a230w-passive-positive-controls.json` : `dcfcacc9f44644a137f6c334dc13fcbac0173d3b07787b6e7ee1b548352fc666`.
- `a230w-summary.json` : `859806366dea71e30c791889e6cef0f4195bd40d78fa9c135b32c894f24a23c9`.

**Décision : W PASS technique ; A2.30 PARTIELLE, Stage12 PARTIAL, #110 OPEN, PR #194 DRAFT.** Un audit indépendant des archives (X) et une éventuelle relecture physique (Y) restent à faire sans modifier rétroactivement les critères. Modèle cognitif NO-GO, aucun changement normatif ou de code `src/i0`.
