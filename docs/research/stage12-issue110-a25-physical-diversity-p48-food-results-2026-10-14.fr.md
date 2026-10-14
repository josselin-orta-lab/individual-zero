# Stage 12 / Issue #110 : résultats A2.5, diversité physique, nourriture et P-48

Date : 14 octobre 2026. **Statut global scientifique : PARTIAL.** Protocole préenregistré le même jour au commit `482cb17ac6bf2231039a4db478153aa404bc6f7d`, **avant** l'auditeur et le runner. SHA d'exécution `6d8cb9988cb7c26563226785a258f3cc17d4d220`. Workflow [#38579458689](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38579458689) : **SUCCESS**, Python 3.11 **et** 3.12, neuf tests négatifs par interpréteur, 16 vies autonomes de 42 pas, **672 transitions physiques uniques** (et non 1344). Zéro erreur déclarée par les audits complets d'origine et le nouveau census indépendant. Artefacts ZIP du run : `issue110-a25-py3.11`, `issue110-a25-py3.12`, incluant journaux JSONL, WAL, synthèses par vie et census des nouvelles métriques.

## Résultats bruts et métriques dérivées

Quatre profils physiques (`restored`, `sustained`, `replenished`, `urgent`) × deux mondes (`free`, `A2`) × deux bras (intérêt instrumental P-48 OFF/ON). Scénario et code cognitif **inchangés** depuis l'A/B précédent, sans nouvelle vérité Oracle, ni changement UC, sommeil, détecteur, seuil ou physique.

| Profil | Monde | Sites physiques distincts OFF | Sites ON | Mouvements réussis OFF | Mouvements ON |
|---|---|---:|---:|---:|---:|
| restored | free | 31 | 31 | 30 | 30 |
| restored | A2 | 28 | 28 | 27 | 27 |
| sustained | free | 33 | 33 | 32 | 32 |
| sustained | A2 | 32 | 32 | 31 | 31 |
| replenished | free | 33 | 33 | 32 | 32 |
| replenished | A2 | 32 | 32 | 31 | 31 |
| urgent | free | 33 | 33 | 32 | 32 |
| urgent | A2 | 33 | 33 | 32 | 32 |

**Diversité C3 (strictement sur 42 pas) :** **8/8** paires ON/OFF satisfont la rétention >=80 % préenregistrée, précisément **100 % pour chacune**. Aucun bras instrumental n'efface la locomotion sur cet horizon. Le compteur utilise les coordonnées du journal physique, pas seulement le registre limité de sites d'Exploration. L'égalité des comptes ne prouve ni l'égalité de tous les trajets ni une stabilité après 42 pas.

**Nourriture C4 :** les 16 vies totalisent **4 commandes `manger` avec effet `ate` physique** et **4 pas avec augmentation nette de `body_after.food`** (comparaison au précédent résultat corporel; premier pas exclu). **Deux vies instrumentales** ont simultanément au moins une ingestion et une augmentation corporelle nette. Ces faits soutiennent une **expérience alimentaire localement vécue**, et corrigent l'impression trompeuse selon laquelle il n'existerait aucun résultat alimentaire réel sur cette cohorte. Mais le census ne démontre **aucune augmentation de compétence alimentaire causée par le mécanisme instrumental** : les bras témoins peuvent avoir les mêmes consommations. La réussite d'un sous-objectif `spatial_distance` ne vaut pas fin d'objectif alimentaire.

**P-48 C5 :** **deux groupes** de signal informationnel authentique sont partagés entre plusieurs options concurrentes au même pas/cycle, **zéro répétition d'un même ID dans l'évaluation d'une option**. Le même site-frontière peut servir à une exploration autonome et à un mouvement instrumental vers un objectif. Il doit demeurer **une unique information-source**, pas deux preuves de causalité ni deux épisodes d'agence. Les neuf tests du census incluent la répétition intra-option (rejet), le partage inter-options (acceptation), l'égalité numérique sans identité de provenance, les faux mouvements et l'augmentation corporelle sans ingestion.

**Attribution C1/C2 :** **0/16 vies** dispose de deux `success` et deux `failure` consommés dans une fenêtre subjective de 12 pas. `attribution_bias` reste **non évaluable**. Les 16 vies indépendantes ne peuvent jamais être fusionnées pour faire artificiellement une seule fenêtre personnelle. Les couples A/B antérieurs (3 OFF, 5 ON) restent des preuves de progrès locaux, pas la validation de la calibration.

## Reproductibilité et limites

Les agrégats A2.5 ci-dessus concordent exactement sous Python 3.11 et 3.12. Les différences IEEE-754 Stage8 antérieurement constatées peuvent néanmoins altérer les octets JSONL complets; **aucune identité binaire inter-Python des 16 journaux n'est revendiquée** ici. Les deux exécutions par interpréteur représentent les mêmes 16 conditions, non des réplications statistiquement indépendantes. Aucune campagne de 600 pas continus n'a été conduite par **cette** nouvelle instrumentation. La matrice de discrimination causale, les effets retardés d'alimentation et la stabilité long-terme restent à investiguer.

## Verdict individuel C1–C8 à ce checkpoint

| Critère | Verdict | Justification |
|---|---|---|
| C1 Attribution subjective | PARTIAL | `self/world/unknown` authentiques hérités de A2, mais calibration par vie manquante |
| C2 Distinction causale | PARTIAL | Sources indépendantes et audit A2 conservés; pas de variabilité causale assez dense |
| C3 Diversité | PASS (42 pas) | 8/8 paires conservent 100 % des sites; pas de conclusion au long cours |
| C4 Compétence alimentaire | PARTIAL | 4 ingestions et 4 hausses corporelles observées; pas de gain comparatif démontré |
| C5 Discrimination P-48 | PARTIAL | 2 signaux partagés inter-options, 0 doublon intra-évaluation; discrimination causale non prouvée |
| C6 Stabilité prolongée | INCONCLUSIVE | Aucun parcours continu de 600 pas dans A2.5 |
| C7 Reproductibilité | PARTIAL | Deux versions Python concordent en indicateurs et audits; ULP/binaire non résolu |
| C8 Conformité | PARTIAL | Aucun changement normatif/UC/cognition; revue finale d'intégration à achever |

**Verdict global PARTIAL.** Les résultats renforcent l'exploration et la preuve locale d'ingestion mais ne démontrent pas l'attribution causale subjective robuste. L'issue #110 doit rester ouverte jusqu'à meilleure couverture dans une même vie et réception explicite de l'opérateur. La spécification MVP historique v1.3.1 n'a pas été modifiée; le changement est un **auditeur scientifique indépendant**, non un nouveau comportement d'I0.

Prochaine expérience prioritaire : exécution prolongée d'un petit nombre de vies **sans commandes forcées** pour déterminer si les jugements et la diversité subsistent, puis expériences alimentaires positives/nocives/retardées avec vérification physique, sans transformer l'étiquetage de l'Oracle en perception d'I0.
