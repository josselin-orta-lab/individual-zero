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

Les six auditeurs de journaux et de persistance indiquent PASS, sans exception ni interruption. Les sources et artefacts WAL/JSONL sont déposés avec les exécutions GitHub. `source_step_trace` et `coverage_census` ne créent aucune observation cognitive. La cible extérieure conserve son temps préprogrammé t2 et son retrait t4 indépendamment des commandes de l'individu.

**Interprétation limitée** : dans ces trois contextes, la simple augmentation/diminution du besoin alimentaire, du gain d'une baie et de la quantité de nourriture locale n'a pas induit de nouveaux engagements d'objectifs. Même la condition A2 ne peut être jugée par I0 faute de préengagement pertinent. Ce n'est **pas** un faux négatif documenté du détecteur de biais : il n'a aucune donnée admissible. Les contrôles originaux du 14 octobre, avec la nourriture initiale à 35 et le gain +30, restent pertinents : ils avaient donné un `world` et un `self` dans des vies séparées.

**Action suivante** : instrumenter, sans rétroaction dans I0, la trajectoire des pressions motivationnelles et des options proposées/admissibles, pour établir pourquoi zéro engagement est généré malgré des ressources visibles. Ne pas prolonger arbitrairement au-delà de 36 pas ni forcer une décision. En cas de verrou d'architecture, proposer une modification de spécification à l'opérateur, sans la modifier avant autorisation.

**Verdict** : PASS technique du protocole et des audits ; **calibration scientifique toujours NON ÉVALUABLE, Stage12 PARTIAL, issue #110 ouverte, PR #155 en brouillon, aucune fusion**.
