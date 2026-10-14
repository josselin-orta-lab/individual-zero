# Stage 12, issue #110 : A2.15, audit préenregistré des pertes de preuves d'agence vécue

**Préenregistrement du 14 octobre 2026, avant code ou CI A2.15.** Référence vérifiée `main@86bff3a8a8ccb4a146a71dc7153a47fea65b5557`, issue #110 OPEN, Stage12 scientifique PARTIAL et non reçu par l'opérateur. MVP normatif v1.3.1 INCHANGÉ.

## Défaillance observée et question vérifiable

Les campagnes A2.9–A2.14 ont établi la distinction entre ingestion réellement vécue, prédiction et jugement subjectif. Pourtant la fenêtre diagnostique Stage12 de **12 cycles cognitifs** exige **au moins deux succès et deux échecs** *vérifiés, dotés d'une agence `self` ou `world`, avec pairage GA-06*, et aucune calibration robuste du biais d'attribution n'a été établie. Les campagnes d'enrichissement du modèle Equipment ont présenté des améliorations techniques de couverture sans bénéfice alimentaire. **Il reste à déterminer où se raréfie effectivement la preuve** : objectifs non prérégistrés, résultats inconnus, jugements d'agence suspendus, refus UC, échecs de jointure, perte au prochain pas (sommeil), ou paires admises mais trop espacées dans une fenêtre.

Les seuls échecs de `focused-stage12` précédemment constatés provenaient aussi d'un test A2.6 supposant à tort un sommeil tardif ; la [PR #168](https://github.com/josselin-orta-lab/individual-zero/pull/168) a corrigé cette hypothèse sans changer le runtime. Les tests A2.6 ciblés et la suite focused sont maintenant verts sur Python 3.11 et 3.12. La cohorte longue 6 ×600 pas est en cours au moment du préenregistrement et **ne sera pas présentée comme terminée** avant ses artefacts vérifiés.

## H0/H1/H2, scénario, données et restrictions

- **H_goal** : les critères de succès/échec ne deviennent pas assez souvent des résultats *réellement vérifiés*. Les simples changements de scores Goal, les prédictions et les intentions non suivies ne doivent jamais être convertis en succès.
- **H_agency** : les résultats existent, mais les préengagements ou les jugements `self/world` assortis de `cue_ref` sont rares ; `unknown` ou `unavailable` ne sont **pas** des contre-exemples d'agence et ne doivent pas remplir artificiellement la fenêtre.
- **H_join** : deux sources existent mais la jointure GA-06 (UC, identité, chronologie) ou l'admission du pas suivant limite l'échantillonnage.
- **H_window** : les paires consommées existent, mais leur espacement produit moins de 2 succès ou 2 échecs parmi les 12 derniers *diagnostics effectivement publiés*. Abaisser le seuil ou supprimer les `None` de cette fenêtre constituerait une modification de mesure, **non autorisée** dans cette campagne.

**Corpus principal fixé :** réanalyse posthoc en lecture seule des **16 vies réelles de 42 pas / 672 transitions** A2.10b, archives source [CI #38607070724](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38607070724), hash SHA-256 de chaque archive. Les deux artefacts Python contiennent la même matrice de scénarios ; **seul l'artefact Python 3.11 sert à l'inférence scientifique**, l'autre sert de contrôle de reproductibilité. Aucun nouveau seed ni vie n'est inventé. Si les archives A2.6 longues [run #38624426580](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38624426580) deviennent **terminées avec validation technique**, leur lecture posthoc constituera un sous-lot explicitement séparé ; ne pas mélanger 42 et 600 pas ou leurs conditions.

## Instrumentation indépendante

Lire **uniquement les journaux JSONL causaux scellés** à l'extérieur d'I0 et appliquer impérativement `audit_export_bytes`, `audit_stage12_goal_progress`, `audit_stage12_first_person_agency` et `audit_stage12_attribution_pairs` avant toute inférence. Aucun accès runtime aux propriétaires cognitifs privés, ni vérité cachée Oracle, ni modification de journals. Relever les événements exacts :
- `stage12_goal_progress_preregistered`, `stage12_goal_progress_followup` et `criterion_outcome` ;
- `stage12_goal_agency_precommitted`, `stage12_goal_agency_judgement`, `subjective_agency` et `cue_ref` ;
- `stage12_attribution_pair_admitted`, `stage12_attribution_join_deferred`, `compute_charge` de jointure ;
- `stage12_lived_diagnostics_published` et leurs couples `attribution_pair_ref`, `verified_successes`, `verified_failures`, `bias_min_outcomes_each`, `diagnostic_window`, `attribution_bias` ;
- `stage12_attribution_sample_unavailable` et `stage12_lived_diagnostics_deferred` ;
- les reçus de sommeil `stage10_reduced_capture` **uniquement pour expliquer un vrai pas fermé et dormir**, jamais comme événement présumé.

Produire des comptes exhaustifs par vie, sans mélange entre occurrences physiques, paires, diagnostics et fenêtres. Ventiler les résultats suivis par absence de préengagement, label inconnu, jugements non admissibles, jointure différée, pairage et consommation au pas suivant. Vérifier les propriétés de conservation : `paires_admises = paires_appliquees + paires_expirees_ou_indisponibles + paires_encore_en_attente` avec attention aux cas terminaux; les diagnostics et les compteurs du banc doivent coïncider exactement avec les reçus d'I0.

## Critères prospectifs, décisions et limites

- **T1 intégrité :** 16/16 journaux authentiques, cumul **672** pas, 0 divergence des auditeurs de provenance; refuser les reçus sources absents, les doublons de paires et la falsification de `verified_successes/failures`.
- **T2 fenêtre :** reconstituer exactement la fenêtre glissante de 12 *diagnostics payés*, y compris les cases `None`; aucun `PASS` sur une série condensée de seules paires. Vérifier explicitement que les chiffres comptés par l'auditeur correspondent à tous les `verified_successes/failures` déclarés.
- **T3 attrition :** rapporter pour chaque vie les taux et comptes dans la séquence `objectif→followup connu→jugement non-unknown admissible→join accepté→paire consommée→fenêtre 2+2`. **Une absence de jugement n'est pas automatiquement un manque de mémoire**, et le nombre de `unknown` ne prouve ni réussite ni échec.
- **T4 ablation causale :** garder la politique et les seuils fixes. Après observation, choisir au maximum **une hypothèse à départager** dans un prochain protocole ON/OFF préenregistré séparé. Aucun modèle normatif changé ici.
- **C1/C2/C5 :** aucune inférence de responsabilité physique depuis une association empirique ou une prédiction correcte. La vérité extérieure du banc ne peut jamais entrer dans le détecteur.
- **C3/C4/C6 :** la relecture ne constitue ni nouvelle diversité, ni ingestion, ni stabilité physique 600 pas. Les conséquences alimentaires ne comptent que si elles figuraient réellement dans `world_transition_experienced`.
- **C7 reproductibilité :** SHA source, run CI, commit, schéma JSON et fichier par vie. Deux interpréteurs Python ne sont pas 32 seeds scientifiques.
- **C8 conformité :** aucune modification de `FrozenTableEquipment`, `Stage12LivedDetectors`, `Stage9`, UC, journal causal, Oracle, ActionControl ou MVP normatif.
- **Issue/réception :** Stage12 **PARTIAL**, issue #110 ouverte jusqu'à réception opérateur, même si cet audit passe.

**Verdict scientifique prospectif :** l'instrumentation peut être `PASS` si elle est cohérente, mais la robustesse d'attribution d'agence reste `INCONCLUSIVE/PARTIAL` tant qu'il manque des vies autonomes dans lesquelles le détecteur est réellement calibrable.
