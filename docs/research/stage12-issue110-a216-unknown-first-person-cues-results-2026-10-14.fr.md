# Individual Zero / Stage12 #110 : A2.16, les huit abstentions subjectives sur échecs réellement vécus

**14 octobre 2026, verdict GLOBAL Stage12 PARTIAL.** Préenregistrement antérieur au code `9506fafecdd52b83516cd0a688fa0ac5d8ee4a7d`, référence `main 055daf6443bd3f88a2e94330378984298e876a80`. Le modèle et la spécification normative v1.3.1 sont INCHANGÉS ; les huit cas restent `unknown` et ne sont pas convertis en responsabilité `self` ou `world`.

## Protocole réel et reproductibilité

[CI A2.16 #38628902310](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38628902310) : **SUCCESS Python 3.11 ET Python 3.12**, mêmes agrégats. Relecture externe uniquement des **16 vies mortelles réelles de A2.10b**, 16 journaux JSONL scellés, **672 pas physiques**, originellement vérifiés par [CI #38607070724](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38607070724). Rejoués *aucun nouveau pas*, aucune collecte d'informations Oracle. Chaque journal passe les audits indépendants de chaîne, Goal Progress, first-person subjective agency et GA-06 attribution join avant l'interprétation. Chaque jugement est rattaché à son engagement antérieur `assessment_ref`, au but `intent_ref`, à la commande réellement déclarée et au critère `success/failure` effectivement suivi. Les documents détaillés par vie restent dans les artefacts de CI.

## Observation exhaustive sur les huit jugements `unknown`

| Commande volontaire prérégistrée | Objectif | Mécanisme de première personne | Motif `unknown` déclaré | Cas | Résultat d'objectif vérifié |
| --- | --- | --- | --- | ---: | --- |
| `collecter` | `food` | `unresolved` | `no_distinct_goal_relevant_agency_cue` | **6** | `failure` dans les 6 |
| `se_deplacer` | `spatial_distance` | `witnessed_goal_spatial_target_v1` | `ambiguous_spatial_displacement_cue` | **2** | `failure` dans les 2 |
| **Total** | | | | **8** | **8 échecs** |

Les **8 jugements étaient UC-payés et munis d'un `cue_ref` perceptif authentique** : 0 `unknown` dépourvu de référence. Le nombre de jugements admissibles `self/world` dans ce même corpus est **14**, concordant exactement avec A2.15. Les hypothèses de refus UC, de résultat `unknown` ou de perte pure de capture comme cause commune de ces huit abstentions ne sont **pas étayées**.

**Interprétation importante :** disposer d'une capture après une collecte infructueuse ne démontre pas que I0 en soit la cause, ni que son action était causalement inutile ; d'autres explications subsistent. Sur les six collectes, le mécanisme de jugement prérégistré était `unresolved`, parce qu'aucun indice actuellement prévu par le contrat du `GoalAgencyService` n'atteste l'agence d'une collecte. Les deux mouvements spatialement ambigus ne fournissent ni déplacement distinctivement corroboré ni indice de nouvel obstacle compatible avec une étiquette `world`. Ces `unknown` sont **subjectivement défendables** au regard de la politique et des captures disponibles. Ils ne révèlent pas à eux seuls un bug de mémoire, un danger caché ou une intention volontaire inefficace.

Le fait que les huit `unknown` concernent **uniquement des échecs** explique une **partie importante** du manque d'échecs admissibles aux fenêtres de biais. A2.15 comptait **22** résultats connus, **14** jugements self/world, **14** paires admises, **10** appliquées, **4** expirées lors d'un pas sans diagnostic éveillé, aucun refus UC de jointure. La fenêtre ne dépasse jamais **un échec admissible / 12** dans une même vie. La distribution déséquilibrée vers `unknown` sur l'échec est un résultat observé de ce corpus, pas une preuve de biais d'attribution favorable à soi : le détecteur ne dispose justement pas de l'échantillonnage requis.

## Hypothèses et C1–C8

- **H_unresolved : confirmé dans ce corpus** (6/8 `unknown`, sur des commandes `collecter` du but alimentaire). Aucun mécanisme spécifique à la collecte ne doit être imposé sans preuve perceptive et contrefactuelle supplémentaire.
- **H_spatial : confirmé dans ce corpus** (2/8 `unknown`, résultats de déplacement vers cible ambigus). Une explication environnementale ne peut être inférée uniquement parce qu'un résultat attendu n'a pas eu lieu.
- **H_ingestion : non observé dans ce sous-ensemble** (0 `unknown` prérégistré sur `manger` avec inventaire).
- **H_source : PASS borné** : 8/8 `unknown` ont leur préengagement, suivi de but et `cue_ref` authentiques, aucune attribution extrapolée ni vérité physique externe donnée à I0.

| Critère | Verdict A2.16 |
| --- | --- |
| C1 Attribution subjective | PARTIAL : abstention cohérente et vérifiable ; calibration toujours impossible |
| C2 Distinction causalité/prédiction | PASS borné aux huit cas : aucun échec n'est automatiquement converti en `self`/`world` |
| C3 Diversité | INCONCLUSIVE pour l'audit hors-ligne |
| C4 Compétence alimentaire | PARTIAL hérité ; aucune nouvelle ingestion autonome |
| C5 P-48 | INCONCLUSIVE |
| C6 Stabilité longue | PARTIAL historique A2.6 6×600, sans biais évaluable |
| C7 Reproductibilité | PASS borné : mêmes 16 vies, 2 Python, SHA physiques audités |
| C8 Conformité épistémique | PASS borné : observateur externe seulement |

**GLOBAL Stage12 PARTIAL, issue #110 OPEN, réception opérateur NON EFFECTUÉE.**

## Décision scientifique et prochaine hypothèse

**NO-GO** pour remplacer les huit `unknown` par des attributions automatiques. L'opportunité A2.17 doit porter sur une expérience **vécue, volontaire et perceptivement discriminante** des collectes infructueuses ou déplacements ambigus, avec témoins de perturbations externes, afin d'apprendre la relation subjective aux effets sans deviner l'étiologie des causes cachées. Avant de modifier le contrat du jugement, proposer un protocole séparé d'ablation ON/OFF des indices réellement accessibles et vérifier la sécurité alimentaire Stage9/DC-05 et la proportion de biais sur **plusieurs vies multi-seeds**, idéalement avec des fenêtres suffisamment alimentées **sans forcer de succès ni d'échec**. La spécification v1.3.1 demeure inchangée.
