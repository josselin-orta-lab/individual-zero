# A2.30-ZG : preuve physique bornée d'une couverture manquante sur les vraies racines vécues d'I0

**15 octobre 2026.** Préenregistrement **avant code et expériences ZG** au commit `533a2afac13d6dd4228a3f0ddbd635413ce6b808`; résultat physique de référence [run GitHub Actions #38777542232](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38777542232), code `f416424292501671eda7f9ed65accb7a2712f9ef`, **15 tests PASS** sous Python 3.11 et 3.12, trois fichiers de sortie identiques **octet pour octet**. Revalidation supplémentaire sur la tête de PR #200 [#38778683909](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38778683909) PASS dans les deux versions. Première tentative CI #38777391379 rouge : *uniquement* assertion de texte du message d'échec d'un témoin négatif; la falsification a bien été rejetée dès le premier run, corrigée ensuite sans changer protocole, physique ni métrique.

## Lacune ZD/ZE explicitement résolue

ZD (PR #198) a établi à partir des journaux **de douze vies I0 réellement autonomes** ZB (#197) que `berry_b` était visible et candidate localement ou à l'est, mais **aucun** acte B n'était exécuté, **zéro** refus UC et **174/196** recherches Stage6 sans première arête prédictible. ZE/ZF (PR #199) a montré sur **des états fictifs de laboratoire (5,5)** que des observations physiques de déplacement/collecte B rendent l'algorithme `SimulatorPlanner.search` capable d'un `partial_progress`. Manquait un test sur les **racines exactes originales des vrais individus I0**, et non une géométrie illustrative.

ZG compare, pour chaque **première perception complète réellement vécue** à la naissance, le `FrozenTableEquipment` historique **A_ONLY** et un témoin scientifique **A_PLUS_B_NON_INGESTIVE**. Les deux sont figés avant les recherches en shadow ; les démonstrations B viennent **exclusivement de mondes physiquement indépendants**, ne sont jamais présentées comme la mémoire subjective d'un I0, et ne contiennent **aucune ingestion B**.

## Cohorte physique et test archives

**Sources physiques nouvelles (une fois par run/version Python)** :

- **Deux** mondes pré-nataux A, `restored` et `sustained`, avec leurs 4 véritables commandes A historiques `north→east→collecter(A)→manger(A)` : **8 transitions appliquées**. Modèle construit avec le corpus/versionnement historique, puis son empreinte comparée **exactement** au modèle effectivement présent à la naissance des 12 I0 du run ZB.
- **Quatre** mondes B externes, un par profil × disposition `B_LOCAL` ou `B_EAST`, tous avec un effet de B physiquement bénin **à l'entraînement uniquement**. `B_LOCAL` : `collecter(B)`, **1 pas**; `B_EAST` : `se_deplacer(east)→collecter(B)`, **2 pas**. **6 transitions appliquées** au total, aucune ingestion, aucun terminal.
- **Total** : exactement **6 mondes de démonstration physiquement distincts, 14 actes** de `WorldBody.apply`, deux profils × (4 exemples A +3 exemples B). L'instance de référence Stage11 utilisée pour construire la configuration reste une **fixture inerte** ; aucun nouveau I0 Stage12 n'est né, aucun `life.run_step` exécuté.
- **Test** : les **12 premières perceptions historiques ZB** (2 profils ×3 layouts ×2 effets B cachés), déjà vécues lors des **384 pas autonomes d'origine**. L'étude ZG ne rouvre ni ne prolonge une seule de ces vies. Les deux résumés sources ZB (#38767643472), dont les SHA complets **diffèrent entre Python** à cause de variations flottantes internes déjà connues, ont été vérifiés; leurs captures initiales, modèles A et commandes vécues concordent intégralement.

**Conformité des racines** : chaque `SimulationState` initial B_LOCAL/B_EAST (corps, coordonnées (2,2), inventaire, voisins visibles, ressources, heure) correspond **exactement**, octet de structure après sérialisation, à l'état de début du monde B externe qui a produit la première transition. Les huit correspondances se réfèrent à **quatre modèles d'entraînement physiques** : les deux effets cachés du monde cible sont comparés au **même** exemple bénin externe, jamais au futur résultat de la vie cible. En cas de discordance, le runner échoue au lieu d'adapter la table.

## Résultats Stage6 avec preuve physique à l'entrée

| Disposition réellement ressentie au t0 | Racines | Stage6, modèle A historique | Stage6, modèle A+B externe, shadow |
|---|---:|---|---|
| **B_NONE** : B absente | 4 | `partial_progress` via `north→east→collecter(A)` | **même** `partial_progress`, aucune B inventée |
| **B_LOCAL** : B visible sous les pieds | 4 | `incomplete_model`, **0 arête racine** | `partial_progress`, **1 arête racine**, première commande `collecter(B)` |
| **B_EAST** : B visible à l'est passable | 4 | `incomplete_model`, **0 arête racine** | `partial_progress`, **1 arête racine**, préfixe `se_deplacer(east)→collecter(B)` |
| **TOTAL** | **12** | **8 `incomplete_model` / 4 `partial_progress`** | **12 `partial_progress`**, aucune ingestion B |

Les **24 recherches** utilisent le vrai code `SimulatorPlanner.search`, avec même perception en entrée dans les deux bras, profondeur 3, `r_eff=1`, sous-objectifs progressifs et réévaluation de préfixe. **8/8 premiers actes B explicitement proposés en shadow**, avec des prédictions physiques de collecte ou déplacement démontrées; **0 plan `manger(B)`**, **0 `plan_found` alimentaire B**, **0 action dispatchée**. L'absence d'une première arête prédictible était **une cause mécanique suffisante** du statut `incomplete_model` aux huit racines B visibles de ce banc; cela ne prouve **pas** la cause unique de la non-consommation B des vies ZB, puisqu'aucune proposition enrichie n'a été arbitrée par un véritable sujet.

**Parité épistémique** : les six paires bénin/létal de naissances ZB, dont quatre portent B visible, ont des captures initiales, empreintes A et sorties Stage6 shadow **strictement identiques**. Les paramètres cachés de toxicité ne deviennent **jamais** des attributs du modèle ou de l'action. Le témoin bénin de collecte ne prétend pas démontrer la sûreté d'une ingestion.

## Limites et verdict

- **ZG1 : soutenue** sur les huit vraies racines B visibles : la table physique externe connaît l'arête de premier pas et la table réellement née ne la connaît pas.
- **ZG2 : soutenue mécaniquement** : `partial_progress` et premières commandes B attestées par le véritable algorithme Stage6, mais **sans décision**, mandat d'action ou jugement subjectif vécu. Le modèle était enrichi artificiellement depuis des vies de laboratoire externes, ce qui n'est pas le fonctionnement autonome d'I0.
- **ZG3 : vérifiée** : quatre témoins B_NONE inchangés, parité des six paires cachées, zéro modèle de conséquence ingestive B et zéro certitude de sûreté.
- **ZG4 : toujours non démontrée** : sélection en compétition, coûts UC vécus, apprentissage actif propre, ingestion B, sécurité et attribution causale distale. Les états personnels d'I0 ne sont pas modifiés par cette expérience.

**PASS technique de l'expérience ZG; Stage12 PARTIAL, issue #110 OPEN, A2.30 PARTIELLE, NO-GO de déploiement cognitif.** Pas de modification de `src/i0`, Stage9/DC-05, WAL M11, UC ou MVP v1.3.1. La décision d'introduire un mécanisme d'exploration non ingestive admissible ou une nouvelle classe de modèles reste **opérateur** et réclame une expérience distincte.
