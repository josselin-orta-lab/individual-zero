# Individual Zero / Issue #110 : bilan A2.10b mémoire vécue et indisponibilité Equipment

**14 octobre 2026. Verdict Stage12 PARTIAL.** Préenregistré au commit `222a50065d3bf222ecbfb80dc3a21c50a20e7282` **avant** le nouveau code et les expériences. Référence main `d34f50bba79b352ef418324a6ee8308ac2f2d6fe`. L'auditeur ne modifie **aucune composante cognitive, physique ou normative** du MVP, ni le détecteur d'attribution. La PR est une instrumentation externe seulement.

## Exécution et provenance

[GitHub Actions #38607070724](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38607070724) : **SUCCESS Python 3.11 et 3.12**, cohorte de **16 vies mortelles authentiques**, chacune 42 pas physiques, **672 transitions uniques**. Chaque interpréteur réexécute la même matrice déterministe ; il ne s'agit pas de 32 seeds indépendantes. Les journaux canoniques/WAL, contrôles de mortalité, audit A2 et checks externes Stage12 sont effectués par le runner déjà intégré A2.9. Le nouvel auditeur, `scripts/audit_stage12_issue110_a210b_opportunities.py`, lit uniquement les journaux scellés et enregistre SHA-256, captures locales, entrées `S_t`, indisponibilités Stage6 et ingestion physique. Les artefacts ont été téléchargés et inspectés à partir du run, avec **16 lignes de vies réelles dans `a210b-audit.json`**.

Le premier audit rouge ([#38606727563](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38606727563)) est conservé : l'hypothèse incorrecte « toute baie admise dans S_t doit être sur une case voisine au même pas » rejetait à tort des références persistantes. Le correctif refuse désormais une référence de baie sans **capture locale antérieure**, mais autorise le maintien d'une contribution vue plus tôt. Il **n'en déduit pas** que la ressource existe encore. Le reçu `perceptual_capture` publie les ressources des voisins, mais omet la liste de ressources de la cellule *occupée*. Ainsi **deux vies restored/early** contiennent chacune une observation sur la cellule occupée qui est localement plausible, mais dont la **présence ne peut être revalidée par ce seul reçu** : cet état est marqué `current_cell_observations_unverified_by_capture_receipt`, pas présenté comme une preuve certaine.

## Résultats bruts utiles

- **Toutes les 16 vies** possèdent une première perception de baie voisine véritablement attestée à **t2**. Une référence de baie atteignant `S_t` provient soit d'une observation voisine antérieure, soit de la cellule actuelle explicitement marquée comme non entièrement vérifiable par le reçu utilisé.
- `sustained/early/gain1.6` : baie observée localement aux pas **2, 3, 5, 7** ; observation référencée dans `S_t` à **t2** ; **35 pas** avec statut `incomplete_model` dans le diagnostic ; **0 ingestion**.
- `sustained/none/gain1.6` : baies observées aux pas **2 et 8** dans les voisins, entrée `S_t` à **t2** ; **33 pas** `incomplete_model`, mais **1 ingestion réelle**, attestée par la physique, dès la trajectoire initiale.
- `sustained/original/gain1.6` : observations de baies locales aux pas **2, 3, 11, 15**, entrées `S_t` à **2, 11, 12**, **35 pas** `incomplete_model`, **0 ingestion**.
- `sustained/persistent/gain1.6` : observations locales aux pas **2, 3, 11, 13, 15**, `S_t` aux pas **2, 11, 12**, **35 pas** `incomplete_model`, **0 ingestion**.
- Dans `restored/original/gain1.0`, `incomplete_model` pendant **17 pas**, **0 ingestion** ; en `restored/original/gain1.6`, **8 pas** et **1 ingestion**. Différence de valeur/trajectoire, non une intervention spécifique sur la mémoire.
- Toutes les vies demeurent à **0 calibration exploitable du biais d'attribution** avec le seuil `2 succès + 2 échecs / fenêtre 12`, inchangé.

## Interprétations séparées

**H_mem : NON DÉMONTRÉE.** La baie a bien été perçue, parfois plusieurs fois. Le fait qu'une observation ne soit pas continuellement en `competitive_refs` n'établit pas sa disparition de `Memory`, ni une anomalie de rappel autobiographique. L'audit actuel ne mesure pas exhaustivement le contenu privé de Memory, les passages dans le bus et la motivation à rappeler les épisodes. Il ne serait pas justifié de créer un nouveau routage mémoriel sur cette seule base.

**H_eq : ÉTAYÉE COMME LIMITATION, cause exclusive INCONCLUSIVE.** Dans toutes les vies sustained, un nombre élevé de recherches Stage6 se terminent `incomplete_model`. L'Equipment `FrozenTableEquipment` est un tableau exact de transitions qui retourne `unavailable` si l'entrée état/commande n'a jamais été observée dans le corpus pré-natal. Le moteur ne peut pas s'inventer une issue. Pourtant une vie sustained sans obstacle ingère malgré 33 indisponibilités : l'indisponibilité est contextuelle et ne constitue pas une explication causalement suffisante à elle seule.

**H_val/H_control : NON DÉPARTAGÉES.** La compétition, les veto canoniques et les opérations UC restent inchangés. Des options P-48 peuvent être proposées malgré la simulation indisponible. L'auditeur n'infère ni refus de sécurité ni attribution subjective à partir de `incomplete_model`. Il faut croiser les reçus d'évaluation, de charge UC, de refus Action Control et les trajectoires pour isoler la cause au bon pas.

## C1–C8

| Critère | Verdict | Portée |
|---|---|---|
| C1 jugement d'agence | PARTIAL | Traces subjectives conservées, aucune calibration nouvelle |
| C2 distinction causale | PARTIAL | A2 externe audité sans injection à I0 ; mémoire vs modèle non isolés |
| C3 diversité | PARTIAL | Trajectoires demeurent exploratoires, utilité non prouvée |
| C4 alimentation vécue | PARTIAL | 1 ingestion sustained libre à gain1.6 ; 0 après obstacle |
| C5 discrimination P-48 | PARTIAL | Aucune séparation causale nouvelle |
| C6 stabilité longue | INCONCLUSIVE | 42 pas/vie |
| C7 reproductibilité | PARTIAL | Deux Python reproduisent les métriques, pas des seeds indépendantes |
| C8 conformité technique de l'audit | PASS borné | Journal/WAL et provenance locale audités ; 2 cas de preuve insuffisante signalés |

**GLOBAL PARTIAL.** Les preuves attestent un défaut fonctionnel de reprise alimentaire, mais pas une incapacité générale de mémoire ni une correction algorithmique validée. Le Stage12 reste non reçu et l'issue #110 ouverte.

## Décision de développement

Ne pas créer prématurément une option à commande `manger` forcée ou un « retour vers la baie » codé en dur. Le prochain protocole doit :
1. Traquer la couverture des couples `SimulationState × PrimitiveCommand` accessibles à l'Equipment, sans enrichir ce dernier à partir de vérités cachées.
2. Séparer le stockage de l'observation historique par Memory/Exploration de son accès effectif aux phases UC payées.
3. Si un modèle plus généralisant est autorisé par le contrat normatif, le former uniquement sur transitions physiques externes observables avant naissance, garder l'inconnu `unavailable`, puis exécuter des ablations ON/OFF sur les mêmes corps et perturbations, y compris des conséquences nocives et retardées.
4. Vérifier le veto de sécurité, le budget UC, la diversité et les attributions `self/world/unknown` avant fusion cognitive.
