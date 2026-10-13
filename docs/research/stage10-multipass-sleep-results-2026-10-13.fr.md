# Issue #133 : multipasse 1 vs 3, analyse rétrospective des journaux (13 octobre 2026)

## Provenance, périmètre et validité

- Dépôt : `josselin-orta-lab/individual-zero`. Base fusionnée PR #138 : `040f49832f6861edfbb606203b5446ffa633052d`.
- Préenregistrement antérieur à l'implémentation : `docs/research/stage10-multipass-sleep-prereg-2026-10-13.fr.md`, commit `731c8dd62cc383d4c4c351cf742fcd3335f08967`.
- Source exacte des quatre vies : `6ae41770bbb57680d663b0901d91ccc029757292`, PR #139.
- Actions `38351291405` (Stage12, succès sur Python 3.11 / 3.12) et `38351291422` (CI rapide, succès ; full-validation **SKIPPED**).
- ZIP expérimentaux : artefacts `11790629234` (Python 3.11) et `11790632946` (Python 3.12), chacun contenant `canonical.jsonl`, `life.wal`, `life-result.json`, `index.json`, `summary.json`.
- 240 pas physiques par vie, deux profils d'une même fixture ; 480 pas par interpréteur, 960 pas physiques au total. **La duplication 3.11/3.12 est une reproduction logicielle exacte et non quatre graines statistiques indépendantes.** Comparaison exploratoire, pas de validation scientifique définitive.
- `w_C=0` pour les deux profils, `p_cons_min=0` déjà utilisé dans la fixture, lot maximum 3, scan incrémental opt-in, slot P-42 : 100 UC/pas, 600 UC/période. Paramètres physiologiques et arbitrage de la veille inchangés.

## Mesures directement vérifiées dans les journaux

| Mesure après 240 pas par vie | 1 passe/pas | 3 passes/pas |
| --- | ---: | ---: |
| Épisodes effectivement fermés | 119 | 119 |
| Épisodes éligibles au dernier pas (fin strictement antérieure au pas) | 119 | 119 |
| Références sélectionnées dans des lots gelés, y compris lot encore actif | 20 | 50 |
| Publications atomiques de h | 6 | 16 |
| Références effectivement consolidées | 17 | 47 |
| Backlog éligible non consolidé | 102 | 72 |
| Sommeil physique (`dormir`) | 96 | 96 |
| Veille physique (`se_deplacer`) | 144 | 144 |
| Checkpoints validés | 39 | 99 |
| Maximum de checkpoints dans un même pas | 1 | 3 |
| Enregistrements scannés et facturés (avec rescans) | 436 | 1 032 |
| Reports de travail, journalisés | 0 | 9 |
| Âge moyen des éligibles en attente (pas) | 103 | 73 |
| Âge médian (pas) | 103 | 73 |
| Âge P90 (pas) | 183,8 | 129,8 |
| Âge P95 (pas) | 193,9 | 136,9 |

Les sorties des deux versions Python et leurs journaux canoniques sont identiques octet par octet **pour chaque profil**. Empreintes SHA-256 des exports canoniques : 1 passe `83e3e90772ccf53337317ec2e3aa2b6fd4cf5953907578008989ab823ae04ecb`, 3 passes `b00d1d76cfd273e360025ec5b2007b741b5791e57d55a75776d76b3760aa9b91`.

La vérification indépendante de cette lecture confirme les références consolidées uniques, leur appartenance aux épisodes fermés avant le cut gelé, les six checkpoints dans l'ordre normatif avant chaque h publié et au plus un h par pas physique. Pour les quatre vies, `life.wal` contient les mêmes enregistrements canoniques que `canonical.jsonl` (avec terminateur final). Les audits intégrés au runner ont aussi réussi. Ce sont des preuves de cohérence technique, **pas** de vérité physique externe ni de qualité cognitive des connaissances.

## Croissance, pentes et latence

| Fenêtre de pas | Nouveaux épisodes éligibles | Consolidés (1 passe) | Backlog Δ (1 passe) | Consolidés (3 passes) | Backlog Δ (3 passes) |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1–80 | 39 | 2 | +37 | 14 | +25 |
| 81–160 | 40 | 6 | +34 | 15 | +25 |
| 161–240 | 40 | 9 | +31 | 18 | +22 |

Débit moyen : arrivée `119/240 = 0,496` épisode/pas, publication `17/240 = 0,071` vs `47/240 = 0,196` épisode/pas, gain de publication `+176,5 %`. Même sur les 80 derniers pas, le débit `18/80=0,225` reste inférieur à l'arrivée `40/80=0,5`; le stock **ne se stabilise pas**. Le dernier lot gelé, de trois épisodes, n'est pas encore publié, et n'est pas compté comme consolidé.

## UC, refus et préservation de la veille

- Tous les compteurs `consumed_step_uc` accessibles dans les checkpoints des passes et scans restent à **100 UC/pas maximum**, et `consumed_period_uc` observé à **100 UC/période maximum**, sous plafonds respectifs de 100 et 600.
- Les maxima des seuls événements de checkpoints ne mesurent pas nécessairement toutes les UC d'un pas : préparation/replay peuvent être facturés avant un report sans checkpoint final. Ne pas présenter la somme des maxima de checkpoints comme consommation exacte. Le runner est désormais instrumenté en observation externe pour archiver le budget P-42 *effectivement consommé en fin de chaque pas*, les UC entre publications h et la dette de travail non publiée : ces valeurs exigent un nouveau run de cette version instrumentée.
- Les neuf reports du profil trois passes proviennent de cinq `insufficient_pass_completion_budget` (dont 2 replay, 2 sélection, 1 extraction d'hypothèses) et de quatre `incremental_scan_out_of_uc`. Ils ont lieu aux pas 133, 154, 175, 196 (deux reports), 208, 217, 226 et 235. Ce sont des reports explicites, pas des pertes observées.
- Les **96 commandes dormir et 144 déplacements** sont identiques ; aucune famine supplémentaire de veille n'est visible **dans cette seule fixture**. Les besoins vitaux urgents, dangers, profils de charge variables et mondes held-out ne sont pas couverts ici. La vie continue 240 pas dans chaque bras.

## Lecture logicielle et scientifique

1. **Conforme en observation** : multipasse réellement exécuté, UC observées sous enveloppe, h atomique à six checkpoints, aucune consolidation répétée, sommeil/veille identiques. Le défaut historique d'une seule passe par étape était un frein logiciel au débit ; le nouveau paramètre est opt-in et vaut 1 par défaut.
2. **Limitation conceptuelle, non bug prouvé** : à chaque transaction, l'inventaire complet des épisodes pré-cut est parcouru sous prix `episode_scan`, y compris les épisodes déjà consolidés. Le travail reste O(N) par transaction et la création d'épisodes à ~0,5/pas dépasse le débit constaté. La borne UC physique est réelle ; elle ne doit pas être relevée artificiellement.
3. **Preuves absentes** : exactes UC par pas et transaction dans les anciennes archives, stress P-42 serré avec confirmation indépendante, comportement sur plus de 240 pas / autre monde et qualité de la mémoire apprise, crash-atomicité M11 Stage12. Les archives initiales établissent un gain descriptif, pas une stabilité.
4. **Piste ultérieure**, sous décision opérateur si la contrainte normative s'y oppose : index de références éligibles encore non consolidées, mis à jour et facturé explicitement, sans accéder gratuitement à l'inventaire complet ni modifier la politique de priorité, les points de coupure ou les plafonds. Ne pas implémenter une file « gratuite » ou une expiration destructive des épisodes.

**Verdict provisoire : VALIDÉ TECHNIQUEMENT SUR LES SCÉNARIOS OBSERVÉS, HYPOTHÈSE SCIENTIFIQUE DE SOUTENABILITÉ NON SUPPORTED.** L'issue #133 reste ouverte ; une validation opérateur et des tests ciblés supplémentaires restent nécessaires. Stage12 et M11 ne sont pas reçus par ce rapport.
