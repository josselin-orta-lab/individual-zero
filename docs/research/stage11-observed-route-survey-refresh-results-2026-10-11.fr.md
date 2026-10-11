# Stage 11 : actualisation des passages observés, comparaison logicielle v2/v3

**Date :** 11 octobre 2026. **Classification :** développement logiciel public, **non held-out**, non Golden et **non validation scientifique**. **Norme :** `docs/architecture/reference/en/mvp-specification-v1.2.1.md` ; ne pas modifier la spécification. **Stage 11 : EN COURS. Stage 9 : NO-GO scientifique.**

## Antériorité, code et campagnes

- [Protocole déclaré avant l'implémentation](stage11-observed-route-survey-refresh-protocol.en.md), commit `3a6901ca8b575c76991224cf083fa76e411bff18`. L'[échec historique de retour après disparition d'une créature](stage11-creature-reflex-remediation-results-2026-10-11.fr.md) reste attaché au commit `8210af69`.
- Le propriétaire `GeographicExploration` dispose maintenant d'une option **`refresh_surveys=True`**, exigeant `observe_routes=True`. Sa version de snapshot est `geographic-exploration-v3-survey-refresh`. Les schémas v1 et v2 et les configurations sans opt-in conservent leurs comportements.
- Dans `src/lab/stage11_runtime.py`, un relevé mis à jour provient exclusivement d'une capture locale au **même site physique** et après une charge `exploration_observe` acceptée. Le journal conserve le voisinage ancien, le voisinage actualisé, la date d'observation précédente et le cycle. Aucun ancien site n'est recompensé comme nouveau.
- L'implémentation et les diagnostics comparatifs sont vérifiés au commit **`610c4809dbd8ab16fdd7130b53a4d26f1e95dd92`** par [GitHub Actions #38121478640](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38121478640) : **838 tests Python 3.12 PASS** et bootstrap smoke PASS.
- Première exécution [#38121348184](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38121348184) au commit `f89fb3d4` : **838 tests exécutés avec 10 erreurs**, toutes attribuées au parseur de la *nouvelle sonde*, qui lisait par erreur `operation` dans `external_input_applied` au lieu de `external_input_received`. Les corrections `9179bb8c`, `21f38a7f`, `610c4809` ont réparé cette lecture et mesuré correctement le décalage entre cycles ; ni les seuils, ni le mécanisme cognitif, ni les configurations de danger n'ont été modifiés pour faire disparaître l'échec.

## Comparaison contrôlée : quatre mondes, deux modes, dix pas chacun

| Monde déclaré | Registre v2 : sans actualisation | Registre v3 : actualisation opt-in | Résultat physique v3 |
| --- | --- | --- | --- |
| `unchanged_control` | Rejoint (2,2), puis (2,3) et (2,4) | Même trajectoire | 2 transits de retour, aucune révision |
| `creature_blocks_return` | Reste sur (4,2) | Reste sur (4,2) | 0 transit vers la case occupée, aucune révision |
| `creature_removed` (posée pas 3, retirée pas 5) | Reste sur (4,2) jusqu'au pas 10 | Revient via (3,2) et (2,2), puis explore (2,3) et (2,4) | **2 transits**, révision locale observée |
| `unknown_danger` (zone activée pas 3, non visible) | Même trajet que témoin, 10 dommages physiques | Même trajet que témoin, 10 dommages physiques | Aucune révision ni connaissance préalable déduite |

**Trajectoire exacte v3 avec retrait de la créature** (captures Perception, dans l'ordre des dix ouvertures de pas) :

```text
t1  (2,2)   -> est
t2  (3,2)   -> est
t3  (4,2)   -> attendre, créature visible sur le passage ouest
t4  (4,2)   -> attendre
t5  (4,2)   -> ouest, après suppression externe de la créature
t6  (3,2)   -> ouest, transit vers le carrefour
t7  (2,2)   -> sud, première visite de l'autre branche
t8  (2,3)   -> sud, exploration vers (2,4)
t9  (2,4)   -> attendre
t10 (2,4)   -> attendre
```

Au pas physique **5**, l'ancien relevé de (4,2), acquis au pas **3** et ne contenant **aucun voisin libre**, est remplacé en **cycle 1** après capture et UC Exploration acceptée. Le nouveau voisinage contient **(3,2)**. Les recherches routées positives apparaissent au **pas 5, cycles 2 et 3**, puis au pas 6 ; **aucune lecture de l'observation du cycle 1 ne sert de sortie Planning dans ce même cycle**. Les transits de retour sont appliqués aux pas **5 et 6**.

La visite enregistrée sur (4,2) ne devient pas une nouvelle visite lors du rafraîchissement. Les sites crédités et les positions physiquement capturées coïncident ; chaque variante se rejoue à l'identique et ses journaux vérifient leur chaîne d'intégrité. Le budget Exploration nul ne peut enregistrer ni nouveau relevé payé ni révision. Le résultat v3 s'obtient sans destination injectée ni accès à la vérité cachée du simulateur.

## Empreintes SHA-256 des diagnostics de développement

| Variante | Version | Entrée | Journal | Résultat |
| --- | --- | --- | --- | --- |
| Témoin | v2 | `72d8fde095c2d9e447c5a10f4ea97f0a35975fb5b02eeafe0db1794ac95f614c` | `9ebcd79f0bfd90bf70de75a97ef7a323eb79d7e322a1e1b3db3fcaf514cdc5df` | `aa423ad749b6ba91a90251556dc3936cb00b98dd174d4b15ccafceaf801d7675` |
| Témoin | v3 | `f953317474ff9173dca0c8bb12dc3dfcb3b09345bccee26df9a8217cd4d941d2` | `b3e7d94615c170da8bdd9ca44cc0365e659b14b7a75e458e1a1e40087545a78e` | `e990a74d790f32ef65a2baec42ef621d5c4d17a2fd1e789dff781093170a3643` |
| Créature persistante | v2 | `54e8cd187442d42d9b648d1dc5a9dad0c6d4b887751dda7cdfc30f443a540350` | `d1456f1aee545941041af7b86200186de14c26aa84c002005878d92626379092` | `23b45e725caff4744c67a8993cf69f3b16db2904b203c4a7292f4055f03de4d2` |
| Créature persistante | v3 | `9cc2ecbdff232c48ab52f7c44b52aee5670c52f409f0610113c172947b9503a1` | `05269849d4ecc689adcc64c39d7210a528cb6a396b098ed626062b7364f66bfd` | `d3c768ea5f509b554f90e9d3e6ec972f47e871a6ffc5d7a29c7e3496bd42b2cd` |
| Créature retirée | v2 | `99e331f79480d7fbc8a8c7ba236f9eda486b4234dec399d7e3f0d4cf37ef9f71` | `6372e6a7ac5d2430d16ff62e29a313f4ef8a1ad00d3c38d187ae8cc7272901c2` | `c7a6da768fa90cab4fde649f6b51ca6cbbfb54fe4e3fcc35c5a0fc11a591c1fa` |
| Créature retirée | v3 | `314607a626252337a7b90b06c75d578e35e11013949d254696577ab6efd134db` | `c9658557daa1ae0c0f3bccf40e39bf70ec6cd7d680963670ee6fd49cc16f1268` | `459b0f198a1e37c3874dbd84f8521d7f11a2b8975f613e63463f92fb2ddb497c` |
| Danger inconnu | v2 | `97a070d96e7320bce5b2a3b0202faaa370a336946a3cb92029ff4bec56e11575` | `e65e11899990bd59ef24ed4f7332c26f4f77117a9b540a7c0e4889de5121bfc6` | `34b048dbf638091e43eeb7215a223e2508d9bd8cfdfce8165b34f7ad25b6c318` |
| Danger inconnu | v3 | `a013744c6e50dd0ccac5c56e5ccf30464174aeb807dd8bf7bef9275499f189ca` | `803760ab5c72d343b247da555ae766a8cb7ba4fce1f251794c1ced5d1f4a880b` | `f8b4603f4aa42aaa9ea9a3de6d6ba033632153bd282994962782785ea24461` |

Les SHA-256 sont ceux du code **`610c4809`** testé ; ne pas les attribuer à d'autres commits ni à une campagne scientifique.

## Reproduction minimale pour observateur

Dans un environnement Python 3.12 identifié, avec accès au dépôt et au commit exact :

```sh
git checkout 610c4809dbd8ab16fdd7130b53a4d26f1e95dd92
python -m pip install -e .
python -m unittest tests.test_stage11_survey_refresh_owner tests.test_stage11_survey_refresh_comparison -v
python -m lab.stage11_survey_refresh_probe
```

La sonde émet huit lignes `stage11_public_survey_refresh=` contenant les captures, actions, cycles, relevés révisés, budgets, SHA de journal, SHA d'état Exploration et SHA de résultat. Les tests de régression historiques ne sont pas remplacés par ce protocole.

## Limites et suite

Le test démontre uniquement qu'un voisinage physique local **récemment réobservé** peut remplacer l'ancienne description d'un site **dans cette configuration opt-in** et permettre un retour borné. Il ne démontre ni apprentissage causal du danger, ni modèle de carte générale, ni adaptation dans des environnements arbitraires. Les 10 dommages de la zone cachée restent un résultat défavorable inchangé. Les budgets cognitifs et les vetos canoniques restent obligatoires.

**Statuts distincts :** tests Stage 11 ciblés et suite courte Python 3.12 : **PASS** ; vérification complète Python 3.11 : **NON EXÉCUTÉE** ; Goldens : **NON EXÉCUTÉS** ; Stage 11 : **EN COURS** ; Stage 9 : **NO-GO scientifique**. Aucun changement de visibilité du dépôt, de permissions, de spécification normative ou de protection de branche.
