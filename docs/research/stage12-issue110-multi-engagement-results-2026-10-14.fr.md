# Issue #110 : résultats négatifs de la campagne multi-engagements, 14 octobre 2026

**Préenregistrement avant code :** `5519cf3`. **Exécution source :** `1e60762887ae8e10498965af009e225e3904574f`. **CI :** [run #38539364500](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38539364500), PASS Python 3.11 et 3.12. Six vies par interpréteur, **six conditions uniques × 36 transitions, 216 transitions physiques**, les réexécutions sous Python différent ne doublent pas la taille de la cohorte.

La procédure expérimentale construit avant naissance les paramètres physiques, la configuration du monde, le corpus Equipment produit par de vraies transitions détachées et les événements extérieurs A2. Aucun seuil Stage12 n'est modifié : fenêtre de 12 diagnostics, minimum de deux succès et deux échecs par fenêtre et seuil descriptif de 0.75.

| Condition | Pas | Commandes `se_deplacer` | Commandes `dormir` | Engagements | Paires consommées | Biais calculable |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| sustained, libre | 36 | 27 | 9 | 0 | 0 | non |
| sustained, A2 | 36 | 27 | 9 | 0 | 0 | non |
| episodic, libre | 36 | 28 | 8 | 0 | 0 | non |
| episodic, A2 | 36 | 28 | 8 | 0 | 0 | non |
| marginal, libre | 36 | 28 | 8 | 0 | 0 | non |
| marginal, A2 | 36 | 27 | 9 | 0 | 0 | non |
| **Total** | **216** | **166** | **50** | **0** | **0** | **0/6** |

Les six auditeurs de journaux et de persistance indiquent PASS sur chaque interpréteur, sans exception ni interruption. **ALERTE DE REPRODUCTIBILITÉ : les empreintes SHA-256 des journaux JSONL complets ne correspondent pas entre Python 3.11 et 3.12 pour les six mêmes identités de cohortes**, malgré les mêmes comptes de commandes. Ce résultat interdit de déclarer une reproductibilité binaire inter-version. Différences à localiser au niveau du premier événement divergent, puis à classer comme dérive du contenu causal ou simple sérialisation. Les sources et artefacts WAL/JSONL sont déposés avec les exécutions GitHub. `source_step_trace` et `coverage_census` ne créent aucune observation cognitive. La cible extérieure conserve son temps préprogrammé t2 et son retrait t4 indépendamment des commandes de l'individu.

**Interprétation limitée** : dans ces trois contextes, la simple augmentation/diminution du besoin alimentaire, du gain d'une baie et de la quantité de nourriture locale n'a pas induit de nouveaux engagements d'objectifs. Même la condition A2 ne peut être jugée par I0 faute de préengagement pertinent. Ce n'est **pas** un faux négatif documenté du détecteur de biais : il n'a aucune donnée admissible. Les contrôles originaux du 14 octobre, avec la nourriture initiale à 35 et le gain +30, restent pertinents : ils avaient donné un `world` et un `self` dans des vies séparées.

**Action suivante** : instrumenter, sans rétroaction dans I0, la trajectoire des pressions motivationnelles et des options proposées/admissibles, pour établir pourquoi zéro engagement est généré malgré des ressources visibles. Ne pas prolonger arbitrairement au-delà de 36 pas ni forcer une décision. En cas de verrou d'architecture, proposer une modification de spécification à l'opérateur, sans la modifier avant autorisation.

**Verdict** : PASS technique des audits propres à chaque interpréteur ; FAIL / investigation requise pour la comparaison binaire inter-version. **Calibration scientifique toujours NON ÉVALUABLE, Stage12 PARTIAL, issue #110 ouverte, PR #155 en brouillon, aucune fusion**.

## Contre-audit direct des journaux Python 3.11 / 3.12

Le job indépendant [compare-python-journals, run #38539808519](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38539808519) a téléchargé les douze journaux effectifs, comparé les lignes et affiché le **premier événement causal différent** pour les six conditions. Différence observée dans chaque cas : `stage8_option_evaluation` au pas 8, 10 ou 11 selon la vie. L'événement conserve le même `event_id` mais la représentation hexadécimale IEEE-754 du champ `learned_value` change de quelques unités de dernier rang (ULP), avec une différence ponctuelle du champ `evidence`. Exemple `sustained_free`, pas 8 : Python 3.11 `-0x1.ebefaf04cc8b7p-3`, Python 3.12 `-0x1.ebefaf04cc8b8p-3`. Le hachage causal diverge donc de manière légitime pour cet événement. Les deux journaux ont le même nombre d'événements par condition, les mêmes totaux de commandes et tous leurs propres audits locaux PASS.

**Conclusion précise** : la divergence inter-Python est un **écart numérique causal dans l'évaluation d'options Stage8**, pas simplement une différence de sérialisation JSON, ni une preuve documentée d'une décision motrice divergente sur cet horizon. L'invariance stricte de journal est un FAIL. Ne pas corriger en arrondissant a posteriori les journaux, ni en changeant le détecteur. Si une invariance binaire inter-interpréteur est exigée normativement, auditer l'algorithme d'apprentissage/accumulation numérique, choisir une politique numérique reproductible puis valider sur les autres Stages avant correction.
