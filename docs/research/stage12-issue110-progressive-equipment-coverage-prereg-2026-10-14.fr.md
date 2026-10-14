# Issue #110 : campagne de traçabilité du modèle Equipment et des segments progressifs

Date : 14 octobre 2026, préenregistrée avant nouveau code de diagnostic et expériences.

## Faits initiaux

La campagne A/B `fcf945d` ([CI #38551355467](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38551355467)) a réussi ses huit vies et audits sous Python 3.11 / 3.12 sans variation des résultats entre le mode baseline et le mode progressif. Le résultat scientifique est négatif : dans les deux mondes `sustained`, 0 engagement, 0 paire, aucun biais calculable.

Le modèle `FrozenTableEquipment` est un apprentissage **exact sur état complet et commande** sans généralisation, sans fallback : tout couple état/commande absent du corpus donne `LookupError`, traduit en `incomplete_model` par le Stage6. Le corpus de référence de cette campagne possède **quatre transitions physiques seulement**, effectuées hors I0 avant la naissance : nord, est, collecter baie_a, manger baie_a. Leur existence ne prouve pas leur disponibilité depuis les captures effectivement vécues au moment où le planificateur travaille.

## Protocole de diagnostic

Sur la **même cohorte A/B** que précédemment (8 vies uniques, 36 pas physiques chacune maximum) et sous Python 3.11 / 3.12, journaliser exclusivement comme reçus du runtime du planificateur déjà exécuté :
- statut de recherche `plan_found`, `partial_progress`, `incomplete_model`, `not_found_within_horizon`, `reused_cached`, ou `no_goal` ;
- nombre d'états expansés et de transitions indisponibles, tel que **comptabilisé dans la recherche réelle**, jamais reconstruit ou deviné depuis le monde caché ;
- référence du plan progressif proposé, s'il existe, commande d'ouverture, et confirmation de sa sélection via le reçu `stage12_action_motive_attested`, puis clôture `stage6_progress_segment_closed` après une action réellement appliquée.

Les observateurs ne doivent faire **aucune simulation de plus** que la recherche naturelle, ni ajouter de coût interne ou de données Oracle, ni accorder de priorité au but. Activer le détail supplémentaire **seulement avec `progressive_subgoals=True`**, pour préserver les fichiers de référence des profils legacy. Tests de contrat hors autonomie : (a) le résultat terminal a priorité, (b) un vrai progrès corporel/inventaire est nécessaire, (c) un modèle incomplet ne crée pas d'arête synthétique, (d) aucun progrès d'alimentation ne justifie un but `water` ou `energy`, (e) une option progressée ne doit pas être attribuée au planificateur si elle n'est pas sélectionnée.

## Décisions possibles

1. **`partial_progress=0`, `incomplete_model` dominant** : principal obstacle = couverture d'Equipment; envisager uniquement une expérience de corpus pré-naissance plus riche et strictement physique, sans donner à I0 des exemples choisis selon ses actions.
2. **`partial_progress>0`, mais `selected_progress=0`** : arbitrage Competition/admissibilité/évaluation de l'option, examiner les reçus; ne pas forcer de choix.
3. **Segments réellement sélectionnés, mais sans nouveaux objectifs vérifiés** : revoir indépendamment le contrat du segment, la progression corporelle et sa traçabilité, jamais confondre `step_completed` avec réussite du but.
4. **Biais calculable** uniquement si au moins 2 `success` et 2 `failure` vérifiés dans la même fenêtre de 12 observations éveillées d'une même vie, sans pooling.

Toute divergence des hachages sous Python 3.11/3.12 reste enregistrée séparément. Aucun changement de MVP normatif v1.3.1 ni de seuil de Stage12, PR #155 toujours brouillon, issue #110 ouverte, Stage12 non reçu.

**Critère de fin :** les huit journaux/WAL audités, les comptes réels de modèle et de sélection, un diagnostic causal probatoire ou un refus explicite de conclure, et rapport versionné.
