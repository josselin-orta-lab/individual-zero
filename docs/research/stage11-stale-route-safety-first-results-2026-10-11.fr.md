# Stage 11 : modification d'un trajet déjà observé, première observation de sécurité

**Date :** 11 octobre 2026. **Type :** essai public de développement, jamais tenu pour une validation held-out ni scientifique. **Norme :** `docs/architecture/reference/en/mvp-specification-v1.2.1.md`. **Stage 9 : NO-GO scientifique inchangé.** Les tests synthétiques du modèle causal sont sans valeur de preuve physique et sont isolés des expériences ci-dessous.

## Antériorité et verdict du premier passage

- [Protocole déposé avant exécution](stage11-stale-frontier-route-safety-protocol.en.md) au commit `30a6b590`. Les quatre variantes ne donnent aucune carte cachée à l'individu. Les événements du monde sont fournis par `InjectedScenario` et consignés dans le journal avant capture Perception.
- Implémentation et tests initiaux : commit `3f71b8aad0870e48942b1eec22c75a61f5c8fa8c`, [CI #38120585742](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38120585742) : **818 tests exécutés, 1 échec d'assertion**. Ne pas déclarer cette campagne PASS.
- **Échec conservé :** le test supposait que la présence persistante d'une créature sur (3,2) devait empêcher de rejoindre la branche sud. En réalité, l'individu rejoint cette branche **par un réflexe direct**, bien que **le routage géographique lui-même ne propose aucun saut sur la case occupée**. Il ne faut pas cacher ce résultat en modifiant l'environnement ou en assimilant réflexe et transit d'option.

## Trajectoires physiques observées sur dix pas

| Variante | Positions successives à partir de l'impasse | Décision au troisième pas | Transit géographique appliqué sur case occupée | Branche sud atteinte | Dommages de zone | Intégrité finale |
| --- | --- | --- | ---: | --- | ---: | ---: |
| Sans modification | (4,2), (3,2), (2,2), (2,3), (2,4), puis stationnaire | transit de retour vers l'ouest | 0 | Oui | 0 | 100 |
| Créature persistante en (3,2), introduite au pas 3 | mêmes positions | **déplacement sans option**, déclenché par le réflexe prioritaire | 0 | Oui | 0 | 100 |
| Créature introduite au pas 3 puis retirée au pas 5 | mêmes positions | **déplacement sans option**, déclenché par le réflexe prioritaire | 0 | Oui | 0 | 100 |
| Danger physiquement inconnu en (3,2), activé au pas 3 | mêmes positions | transit de retour identique au témoin | 0 | Oui | **10** | **90** |

Les pas 1–2 et la première observation locale sont identiques pour toutes les variantes. L'activation du danger caché ne modifie pas la première décision de retour (pas 3) par fuite d'information : l'individu rencontre effectivement la zone dangereuse et le monde enregistre 10 points de dommages. Cela ne prouve **ni connaissance préalable du danger ni apprentissage de celui-ci**.

Le placement de la créature au pas 3 provoque un réflexe direct `se_deplacer` **avec option_ref null**, de (4,2) vers (3,2). À ce moment, la créature se trouve en (3,2). Le test initial avait raison de constater **0 transit géographique appliqué vers une case occupée**, mais tort d'en conclure **0 déplacement global** vers cette case. La règle normative du réflexe §9.2 impose de « move away from an adjacent creature » ; son implémentation actuelle classe parmi les déplacements `passable` une case occupée si elle est le seul voisin accessible. C'est une **limitation / anomalie de sécurité à instruire distinctement**, sans modifier rétroactivement ce premier protocole. Le monde inflige des dommages de créature la nuit uniquement dans cette physique : l'intégrité observée ici reste 100 le jour.

## Sources et empreintes de l'exécution échouée

| Variante | SHA-256 du journal | SHA-256 de la sortie de diagnostic |
| --- | --- | --- |
| Témoin | `9ebcd79f0bfd90bf70de75a97ef7a323eb79d7e322a1e1b3db3fcaf514cdc5df` | `58815be970890684272dbcac807d32aaf1d9a0703b6fad3c0ecc6b72f80ed1da` |
| Créature persistante | `63b703fd795d58b294798ace3db83b42732c1affb7ac04773825bc0d9d89075c` | `e6822cdfe8ff535d32591dbb0c34d6f0f3ea0ce9668646af15548cdcc73d7f71` |
| Créature retirée | `95ca048e59114a42c01df3096dcd93673df5bd86d160a91b7b02572c13b50d82` | `9a013cdd44566a6fe8c0dfe631dd40d9979f3a8bad34121db516394317259365` |
| Danger inconnu | `e65e11899990bd59ef24ed4f7332c26f4f77117a9b540a7c0e4889de5121bfc6` | `c479999cb15810de949d9da6b2d599f093a782499896eb62a6adb61cfa10b353` |

Les empreintes décrivent **le code initial `3f71b8aa`**, non les diagnostics enrichis par les correctifs ultérieurs.

## Correctif de mesure, sans modification de la décision

Au commit `0493c18e`, la sonde sépare dorénavant `action_sources`, `applied_reflex_steps` et `applied_reflex_moves_into_active_creature` du compteur `applied_route_into_active_creature`. Au commit `68921e5b`, le test considère comme contre-exemple attendu le réflexe qui traverse la case occupée et cesse de présenter ce déplacement comme un transit d'exploration. Ces changements de **mesure** ne corrigent pas le réflexe. Leur vérification CI doit être rapportée séparément.

## Reproduction minimale

```sh
python -m pip install -e .
python -m unittest tests.test_stage11_stale_route_safety -v
python -m lab.stage11_stale_route_safety_probe
```

La suite complète Python 3.11 et les Goldens restent **NON EXÉCUTÉS**. Le routage reste opt-in, la PR #25 brouillon, le dépôt privé. **Stage 11 EN COURS, Stage 9 scientifiquement NO-GO.**
