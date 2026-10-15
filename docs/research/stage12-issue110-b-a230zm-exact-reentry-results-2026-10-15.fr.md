# A2.30-ZM : retour géographique, dérive corporelle et réutilisation exacte d'une première transition

**15 octobre 2026. Étude physique prospective préenregistrée AVANT le code au commit `82cbb06b98d05816038db1fba02ce118cb1c5e7e`.** Résultat physique de référence : [GitHub Actions #38788052317](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38788052317), code `daf800007330b420b92578270e0ec4f2ae37e410`, **20 tests PASS par version** Python 3.11 et 3.12, sorties de même contenu sur le même ensemble de facteurs déterministes.

## Question discriminante

A2.30-ZK/ZL (PR #206) avait démontré que 16 transitions non terminales **physiquement vécues par leurs propres mondes de laboratoire** deviennent des clés exactes connues **rétrospectivement**, mais que les 16 nouveaux états courants associés restent sans première arête de Stage6. ZM isole une raison formelle : être revenu au même endroit n'est pas être revenu au même **`SimulationState` complet**.

Un modèle `FrozenTableEquipment` se fonde sur la clé `hash(SimulationState × PrimitiveCommand)`, incluant la condition corporelle et `is_night`. Le temps physique vécu est représenté à travers les effets sur le corps et la phase jour/nuit, sans être un argument caché du modèle. ZM n'autorise ni projection factorisée, ni substitut de risque, ni entraînement depuis d'autres mondes.

## 64 mondes, boucle fixe et témoin positif réellement appliqué

Les **64 mondes physiques détachés** correspondent à deux positions initiales `(5,5)/(7,7)`, deux dispositions de `berry_b` (absente/locale), deux coûts énergétiques de déplacement `0/1`, deux décroissances de nourriture `0/0,5`, deux décroissances d'eau `0/0,2` et deux débuts de nuit `200/3`. Tous exécutent les mêmes quatre vraies primitives `east → south → west → north`, sans obstacle, ingestion ou terminalité, puis sont observés sur leur état accessible complet. Aucun I0 n'est né et aucune commande n'a été envoyée depuis le planificateur en shadow.

Dans **quatre mondes explicitement désignés AVANT l'expérience** (2 positions × 2 ressources visibles, coûts/décroissances nuls et jour constant), un **cinquième déplacement physique `east`** est effectivement appliqué **après la prédiction**, afin de vérifier l'effet enregistré au premier mouvement.

| Mesure ZM | Résultat |
|---|---:|
| Mondes détachés réellement appliqués | **64** |
| Pas physiques du cycle de quatre mouvements | **256** |
| Pas physiques prospectifs de confirmation `t5` | **4** |
| **Total de nouvelles transitions physiques** | **260** |
| Position spatiale initiale retrouvée à `t5` | **64/64** |
| `SimulationState` complet initial retrouvé | **4/64** |
| Position retrouvée mais état perceptif modifié | **60/64** |
| Sous-cas état inchangé, même première clé `move(east)` retrouvée | **4/4** |
| Recherches du véritable `SimulatorPlanner.search` | **64** |
| Plans **spatiaux d'un pas** `plan_found` | **4** |
| Recherches sans racine prédictible, `incomplete_model` | **60** |
| Prédictions contrôlées par un cinquième effet physique réellement appliqué | **4/4 exactes** |
| Décès, ingestions B, naissances I0, UC I0 facturées | **0, 0, 0, aucune** |

**Abstraction interdite :** `4/64` est la fréquence dans **une matrice factorielle construite**, pas une estimation statistique de récurrence d'état dans la vie ordinaire d'I0.

## Témoins anatomiques et temporels distincts

- **4 conditions entièrement sans dérive et sans bascule nocturne** : l'état complet redevient identique; `FrozenTableEquipment.predict` reconnaît la première arête et le vrai Stage6 forme un **plan géographique** `move(east)` validé ensuite physiquement.
- **4 conditions où seule la bascule jour→nuit empêche la réutilisation** : la position et les composantes corporelles sont identiques, mais `is_night` change; **aucune** première arête connue. Dans `WorldPhysicsConfig`, `night_start_step=3` est un indice **à base zéro**; l'observation au pas 4 est la première nocturne. Ce détail a été contrôlé dans l'audit indépendant ZN.
- **56 conditions avec dérive physique du corps** : énergie de déplacement, nourriture et/ou eau changent; première arête inconnue malgré le même lieu et la même ressource accessible. La présence de `berry_b` ne modifie jamais ce résultat lorsqu'elle n'est pas collectée.

L'expérience inclut des réglages artificiels zéro-coût/zéro-métabolisme comme témoins positifs **d'ingénierie**, pas comme états physiologiquement représentatifs. À chaque état courant, la recherche Stage6 utilise le vrai code, `max_depth=3`, `r_eff=1`, un objectif **spatial** vers la case est, et `progress_measure=None`; une progression de nourriture ou un jugement d'agence n'est **jamais** inféré d'un déplacement.

## Décision scientifique ZM

**ZM1 SOUTENUE** : un retour géographique ne préserve pas l'identité de la clé perceptive complète lorsque le corps ou le cycle nocturne évolue.

**ZM2 SOUTENUE avec contrôle physique** : quatre retours à état strictement identique permettent quatre réutilisations exactes et quatre déplacements ensuite réellement conformes à la prédiction; il s'agit d'une validité **locale dans les mêmes mondes**, pas d'un modèle universel.

**ZM3 SOUTENUE pour les 60 témoins négatifs** : aucune arête n'est réutilisée dans l'état corporel/nocturne changé et le vrai Stage6 déclare `incomplete_model`. Ce résultat ne démontre pas l'impossibilité d'un futur modèle factorisé correctement borné; il atteste le refus de généralisation de la **table exacte actuelle**.

La vraie cognition I0, ses UC, l'arbitrage des options, l'ingestion B, la sécurité motrice en présence de dangers cachés et le jugement subjectif d'agence **ne sont pas testés** par ces boucles externes. ZK a déjà montré des dangers moteurs invisible où `confidence=1.0` nominal n'est **pas** une garantie physique.

**Résultat : ZM PASS technique; A2.30 PARTIELLE; Stage12 PARTIAL; issue #110 OPEN; déploiement cognitif NO-GO.** Spécification MVP v1.3.1, Stage9/DC-05, mortalité M11, WAL, Oracle/Bench et `src/i0` inchangés.
