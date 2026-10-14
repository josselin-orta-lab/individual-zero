# Stage 12 / Issue #110 : rapport scientifique consolidé A2.5–A2.6

**Date : 14 octobre 2026. Verdict global : PARTIAL.** L'intégration logicielle et la réception scientifique de Stage12 sont **distinctes**. La [PR #156](https://github.com/josselin-orta-lab/individual-zero/pull/156) est fusionnée sur `main` via `ab3be3ed0087b80999896ec037326376c0da66ec`. **L'issue #110 reste ouverte, la réception opérateur n'a pas eu lieu et la spécification normative v1.3.1 demeure inchangée.**

Ce rapport s'appuie sur les artefacts bruts GitHub Actions et les journaux physiques indépendamment vérifiés. Il ne revendique ni conscience ni responsabilité causale objective démontrée par les seules prédictions internes.

## 1. Provenance et hypothèses préenregistrées

- **Référence historique :** `main e94e86a868594ed3dac8bee2cec74a8b419876e5`; PR #155 déjà fusionnée lors de la reprise. Le checkpoint préalable était **PARTIAL**.
- **A2.5 :** protocole committé **avant** l'instrumentation (`482cb17ac6bf2231039a4db478153aa404bc6f7d`). [CI #38579458689](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38579458689), **PASS** Python 3.11 et 3.12. 4 profils `restored/sustained/replenished/urgent` × 2 mondes `free/A2` × P-48 instrumental OFF/ON, soit **16 vies ×42 pas = 672 transitions uniques**. Le critère a priori de diversité est la rétention de >=80 % des sites physiques distincts dans chaque paire.
- **A2.6 :** protocole committé **avant** le runner (`29ca11cdd7b0f45b850ae9704eb7af35b303df14`). [CI #38582263685](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38582263685), **PASS** Python 3.11 et 3.12 sur le code `b4ae4111f5ecbc4bfab9fe60bbc19892bc6c5d2e`. 3 conditions `restored/free`, `restored/A2`, `sustained/free` × instrumental OFF/ON, soit **6 vies physiques réelles ×600 pas = 3 600 transitions uniques** ; arrêt externe à 600, sans mort/reprise. Jalons d'analyse **100, 300, 600** définis avant le test.
- **Indépendance épistémique :** les nouveaux auditeurs lisent après coup `canonical.jsonl`, la tête et le nombre d'événements du WAL durable, les reçus `command_experienced`/`world_transition_experienced`, les diagnostics et les sources P-48. Ils ne sont **pas** injectés dans le runtime I0. La vérité exogène A2 reste dans l'instrumentation externe.
- **Réplicabilité :** exécutions Python 3.11 et 3.12 avec la *même cohorte*, pas un doublement de l'effectif scientifique. Les différentes conditions sont des naissances distinctes, non des seeds aléatoires indépendants ; aucune étude robuste inter-seeds contrôlées n'est revendiquée.

La campagne reprend sans modification les politiques Stage12 `window=12` et `bias_min_outcomes_each=2`, les seuils Competition, le profil P-15 par défaut `w_m=0.75`, le sommeil avec pression de consolidation de développement `w_c=0`, la physique, les UC et le contrat normatif. Les scénarios A2 appliquent un obstacle **après admission** au pas 2 puis l'enlèvent **avant** le pas 4.

## 2. A2.5, diversité, nourriture et P-48 à 42 pas

| Profil | Monde | Sites OFF | Sites ON | Commandes physiques OFF/ON identiques ? |
| --- | --- | ---: | ---: | --- |
| restored | free | 31 | 31 | Oui |
| restored | A2 | 28 | 28 | Oui |
| sustained | free | 33 | 33 | Oui |
| sustained | A2 | 32 | 32 | Oui |
| replenished | free | 33 | 33 | Oui |
| replenished | A2 | 32 | 32 | Oui |
| urgent | free | 33 | 33 | Oui |
| urgent | A2 | 33 | 33 | Oui |

**Préenregistré :** 8/8 paires satisfont le seuil >=80 %, avec **100 % de rétention**. **Analyse complémentaire post hoc**, signalée explicitement : lecture séquentielle des 16 archives JSONL prouve que, dans chacune des huit paires, *toutes les commandes, positions, mouvements et états alimentaires corporels* sont **identiques pas par pas** entre OFF et ON. Cela constate l'absence d'effet moteur comparatif du nouvel intérêt instrumental sur les 42 pas; ce n'est pas une preuve que tous les processus subjectifs sont identiques.

**Alimentation :** 4 reçus `effects.ate=berry_a` avec 4 augmentations corporelles nettes `body_after.food`, répartis symétriquement entre OFF et ON des deux mondes `restored`. **Zéro ingestion `sustained`, `replenished` et `urgent` sur 42 pas**. La progression `spatial_distance` ne constitue pas une preuve de consommation ou de réussite globale `goal:eat`.

**Signaux P-48 :** deux groupes de signal de frontière sont partagés entre options concurrentes autonomes et instrumentales dans les vies `sustained` au pas 2; aucun ID de signal répété dans **une évaluation d'option**. Les références inter-options partagées représentent une **source informationnelle unique**, non des observations causales indépendantes. Des valeurs égales pour des signaux différents ne démontrent aucune équivalence causale. Ne pas transformer P-48 en classificateur `self/world`.

**Attribution :** 0/16 vies ne possède la composition `2 success + 2 failure` consommés dans une **même** fenêtre de 12 observations. Les 3 paires appliquées OFF vs 5 ON déjà constatées ne peuvent être regroupées artificiellement entre individus pour calibrer le détecteur.

## 3. A2.6, résultats physiques sur 600 pas réels

Toutes les six vies exécutent 600 pas et sont **arrêtées par le protocole opérateur**, jamais déclarées mortes. Chacune passe le contrôle indépendant du WAL, de la chaîne causale, de la physique, des objectifs, des jugements d'agence, des paires et, pour le monde A2, des entrées exogènes. **Zéro échec d'audit, zéro exception runtime, zéro décès.**

| Condition appariée OFF/ON | Sites à 100 | Sites à 300 | Sites à 600 | Actions `manger` avec reçu `ate`, OFF/ON | `food` après 600, OFF/ON | Paires d'attribution consommées, OFF/ON |
| --- | ---: | ---: | ---: | --- | --- | --- |
| restored / free | 75 / 75 | 149 / 149 | 299 / 299 | 1 / 1 | 65 / 65 | 1 / 1 |
| restored / A2 | 70 / 70 | 144 / 144 | 294 / 294 | 1 / 1 | 65 / 65 | 2 / 2 |
| sustained / free | 75 / 75 | 147 / 147 | 290 / 290 | **0 / 0** | **0 / 0** | 0 / 1 |

Les deux bras `restored/free` produisent chacun 298 mouvements, 300 pas de sommeil, un `collecter`, un `manger` ; dans `restored/A2` : 294 mouvements, 304 sommeil, un `collecter`, un `manger` ; dans `sustained/free` : 289 mouvements, 311 sommeil, **zéro `collecter` et zéro `manger`**. Toutes ces valeurs sont identiques ON/OFF.

**Critère de diversité :** 3/3 paires conservent **100 %** des sites à **chacun des jalons prospectifs 100, 300, 600**. **Analyse post hoc :** les 600 commandes et transitions corporelles sont exactement identiques OFF/ON pour chacune des trois paires. Tous les nouveaux sites à ce niveau sont effectivement issus de déplacements physiques ; le nombre de sites est élevé, mais cet exploit n'est pas synonyme de recherche alimentaire fonctionnelle. Les vies `sustained` ne reviennent pas exploiter la ressource déjà disponible ; elles atteignent `food=0` et poursuivent l'exploration.

**Limite de mortalité :** dans ce fixture `sustained`, l'intégrité corporelle reste à 100 lorsque `food` tombe à zéro. La règle du monde ne provoque pas de décès par ce seul fait; **600 pas de survie n'attestent donc aucune compétence de survie alimentaire**. Une preuve de mortalité causale nécessite d'autres scénarios et ne doit jamais être fabriquée.

**Attribution :** en `restored/A2`, les paires appliquées comprennent 1 succès et 1 échec dans la vie, mais n'atteignent toujours pas le seuil strict 2+2 dans une fenêtre de 12. Dans `sustained`, l'option instrumentale augmente de 0 à 1 les paires appliquées, sans aucune ingestion. Au total, **0/6 vies calibrables**, même après 600 pas. Le détecteur `attribution_bias` reste correctement **non évaluable**, et non faussement `PASS`.

## 4. Diagnostic explicatif, sans surinterprétation

Dans le monde `sustained/free`, l'option liée au but alimentaire est sélectionnée au pas 2 et réalise un déplacement vers la ressource. Au pas 3, l'option alimentaire évaluée possède une évidence de compétition d'environ **0,34**, inférieure au seuil **0,50**; une cible géographique remporte la compétition et I0 poursuit l'exploration sans `collecter` ou `manger`. Ceci est vérifié sur les reçus de compétition, Stage6 progressifs, Stage8 et les commandes physiques.

**Hypothèse explicative, non démonstration :** combinaison de mise en valeur prospective d'un objectif partiel, apprentissage/replanification du sous-objectif et priorité de nouveauté géographique. Ne pas attribuer d'office la cause à un seul poids P-15.

**Ablation déjà réalisée avant A2.5 :** `docs/research/stage12-issue110-intrinsic-goal-competition-results-2026-10-14.fr.md`. Sur 12 vies physiques de 36 pas, réduire P-15 de `0.75` à `0.35` donne **zéro engagement** plutôt qu'une amélioration; `0` détruit les mouvements exploratoires de la cohorte. **Cette piste est réfutée** pour les conditions évaluées et n'a pas été dupliquée ni reconduite ici.

## 5. Correctif logiciel démontré : seuil de réveil de l'auditeur

Le premier smoke A2.6, réel et plafonné à 6 pas, a révélé un défaut **de l'auditeur indépendant**, et non une attribution erronée par I0. Lorsqu'une paire attend encore le prochain échantillon de diagnostic après un pas physiquement endormi, un arrêt opérateur avant réveil faisait lever à tort `ValueError: admitted pair missing next-step diagnostic admission`.

**Procédure conservée :** échec initial préservé dans [run #38581606303](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38581606303), hypothèse/correction préenregistrée **avant le patch** `docs/research/stage12-issue110-a26-terminal-sleep-audit-fix-prereg-2026-10-14.fr.md`, modification **uniquement** de `stage12_attribution_pair_audit.py`. L'auditeur admet un suffixe entièrement endormi **seulement** lorsque tous ses pas physiques ont un `stage10_reduced_capture` autorisé unique, des clôtures valides et aucune capture/délibération éveillée. Une reprise éveillée sans réception de la paire reste **FAIL**. Les tests re-hachent une falsification supprimant le reçu de sommeil et vérifient le rejet. Les smoke tests de 6 pas et les campagnes 16×42/6×600 passent ensuite sous 3.11 et 3.12.

Aucune baisse opportuniste des seuils, aucun jugement postmortem et aucune modification de la politique cognitive Stage12.

## 6. Reproductibilité croisée, audit et limites

- **Toutes les commandes et conséquences physiques à 42 et 600 pas sont identiques** entre Python 3.11 et 3.12 pour les mêmes vies, avec les mêmes agrégats.
- **Journaux courts :** 2/16 archives JSONL octet-identiques, 14/16 présentent des différences numériques débutant notamment aux `stage8_option_evaluation.learned_value`.
- **Journaux longs :** 2/6 octet-identiques, 4/6 différents par des représentations numériques internes, **sans conséquence physique à 600 pas observée**. La reproductibilité au bit près n'est **pas** attestée.
- **Cohorte insuffisante pour une généralisation statistique :** 16×42 et 6×600 conditions déterministes contrôlées, sans vrai axe de seeds indépendants, sans répétition statistique indépendante; pas d'estimateur d'intervalle de confiance défendable.
- **Domaine alimentaire incomplet :** baies bénéfiques disponibles au départ et obstacle A2 réel, mais pas de série expérimentale indépendante positive/nocive/retardée/ambiguë avec exposition contrastée et contrôles suffisants.
- **Frontière Oracle :** aucune vérité évaluateur n'est accessible à I0; les contre-interventions et les métriques sont strictement en aval. L'authenticité crypto d'un journal seul ne prouve pas la causalité physique externe hors du modèle de monde et des reçus séparés.
- **600 pas opérateur historiques :** [workflow #38582263725](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38582263725) vert, mais la vie fixe correspondante réalise 600 déplacements et **zéro jugement d'agence** ; elle n'est pas une preuve scientifique suffisante pour C1–C2.

## 7. Verdicts séparés C1–C8

| Critère | Verdict | Fondement et limites |
| --- | --- | --- |
| **C1 : attribution subjective** | **PARTIAL** | Jugements `self/world/unknown` issus de la vie réellement observée, mais 0/16 courts et 0/6 longs calibrables |
| **C2 : distinction causale** | **PARTIAL** | Contrôle des interventions A2 et traçabilité des paires; pas assez de contradictions répétées dans une seule vie |
| **C3 : diversité** | **PASS borné** | Rétention de 100 % des sites et identités physiques ON/OFF aux jalons; diversité **utile** et retour vers ressources non démontrés |
| **C4 : compétence alimentaire** | **PARTIAL** avec **FAIL de l'hypothèse de progrès instrumental en sustained** | Ingestions vécues en `restored` mais identiques ON/OFF ; 0 ingestion et `food=0` après 600 en `sustained` |
| **C5 : discrimination P-48** | **PARTIAL** | Partages inter-options correctement explicités; 0 doublon intra-option; pas de séparation causale riche entre alternatives |
| **C6 : stabilité prolongée** | **PARTIAL** | 6 vies ×600, diversité physique stable et 0 erreur; utilité alimentaire toujours défaillante, généralisation limitée |
| **C7 : reproductibilité** | **PARTIAL** | Deux versions Python reproduisent métriques/physique; divergence binaire Stage8 et vrais multi-seeds non validés |
| **C8 : conformité** | **PASS borné aux changements testés** | Respect des frontières I0/Oracle/Bench et du WAL, aucune modification normative; conformité intégrale du Stage12 non attestée |

**GLOBAL : PARTIAL.** Les preuves augmentent fortement en précision, mais elles ne démontrent **ni une attribution subjective d'agence robustement calibrée, ni l'amélioration alimentaire recherchée**. Les résultats négatifs sont des connaissances reproductibles, et non des raisons de déclarer le Stage12 achevé.

## 8. Protocole de reproduction et réception opérateur

Depuis la racine d'une copie propre contenant le commit fusionné `ab3be3ed`, exécuter :

```bash
python -m pip install -e .
python -m unittest discover -s tests -p 'test_stage12_p48_diversity_audit.py' -v
python -m unittest discover -s tests -p 'test_stage12_a26_long_horizon.py' -v

# Utiliser à chaque exécution des répertoires qui n'existent pas déjà.
python scripts/run_stage12_issue110_a25.py \
  --output-dir /tmp/i0-stage12-a25-receipt-unique \
  --cohort-id operator-a25-20261014

python scripts/run_stage12_issue110_a26_long.py \
  --output-dir /tmp/i0-stage12-a26-receipt-unique \
  --cohort-id operator-a26-20261014
```

**Résultats attendus :** `a25-summary.json` : 16 vies /672 pas/0 erreur/8 paires diversifiées; `a26-summary.json` : 6 vies/3 600 pas/0 erreur/0 décès, 3 paires au seuil 80 %, `sustained` sans ingestion, 0/6 calibrable. Conserver ensemble configurations et SHAs, journaux `canonical.jsonl`, `life.wal`, census indépendant et résultats bruts; toute divergence doit être investiguée, jamais maquillée.

**Ce protocole ne constitue PAS une proposition de validation finale de Stage12.** Le destinataire opérateur pourra seulement confirmer la reproduction technique et la persistance du verdict PARTIAL. La réception Stage12 nécessite une nouvelle campagne avec expérience alimentaire réellement améliorée, diversité utile, erreurs d'attribution identifiables et jugements suffisamment contrastés par individu. La validation scientifique exhaustive finale du projet sera une phase distincte.

## 9. Prochaine expérience prioritaire

Préenregistrer une A2.7 **de continuité d'objectifs et d'utilité de la valeur prospective** : comparaison de mécanismes généraux de persistance/achèvement des sous-objectifs `se_deplacer → collecter → manger`, **sans forcer** les actions, avec OFF/ON et ablations du mécanisme, environnements alimentaires bénéfiques/nocifs/retardés, plusieurs configurations et seeds réellement contrôlés si le runtime l'autorise. Mesurer à la fois bénéfices corporels, coûts d'exploration, engagement d'objectif, révisions `self/world/unknown` et faux positifs contre un évaluateur séparé. Toute proposition d'amender v1.3.1 devra passer par une décision normative explicite distincte.

**Ne pas clôturer #110 ni déclarer Stage12 terminé avant une réception opérateur fondée sur de meilleures preuves.**
