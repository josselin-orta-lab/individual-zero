# ISSUE #133 / CRASH-I1 : fenêtre de publication de l'index, matrice os._exit

**Préenregistrement le 13 octobre 2026, avant écriture des nouveaux tests et leur exécution.** Source auditée : `215b71aba507c09ae76e475df1504486a04a2f48`, PR #139. La validation Stage12 `38370078881` et CI rapide `38370079005` sont SUCCESS. Archives `11800379399` (3.11) et `11799883492` (3.12), quatre vies indépendantes par interpréteur. Audit indépendant source des résultats : `/mnt/data/issue133_afterfix_pairwise_audit.json` dans le compte-rendu opérateur et prochain rapport GitHub.

## Faits motivants
Sur 600 pas physiques, P6-B6 indexé consolide 295/299 références (référence) et 296/299 (eau), avec 6044 et 6264 UC, backlog 4 et 3. Sur les mêmes vies, l'ancien scan complet consolide 242 et 238 et consomme 10827 et 9791 UC. Dans l'index, **61 et 58** séquences consécutives `stage10_consolidation_index_maintenance_charged` -> `stage10_consolidation_version_activated` -> `stage10_consolidation_index_retired`, avec **295 et 296** UC de maintenance, ont été reconstruites depuis le WAL. Les champs, identités et totaux correspondent. Les exports canoniques sont identiques entre 3.11/3.12.

Le runtime incrémente les états actifs et journalise la publication h *avant* `index.acknowledge_published()`. Une mort brutale après l'événement h mais avant le retrait de l'index peut laisser une chaîne durable contenant h sans attestation de retrait. Le runtime Stage12 n'est pas pris en charge par la récupération transactionnelle SQLite M11 (voir `tests/test_m11_stage12_compatibility.py`). Aucune reprise de vie ou reconstruction cognitive d'après un ancien export ne doit être présumée sûre.

## Cas prospectivement définis
Utiliser une vraie vie mortelle en mode Stage12 et WAL fsyncé, construite à partir de la fixture de `run_stage10_issue133_paid_index.py`, profil `pass06-batch06-indexed`, `w_C=0`, `step_slot_uc=100`, `period_capacity_uc=600`, `index_maintenance=1`, monde `reference_untrained`. Pas de simulation de succès, pas de copie restaurée. Patcher uniquement le point technique puis provoquer **`os._exit`** dans le processus enfant :
1. **CRASH-PRE-H** : sortie juste avant l'appel à `Stage10PublicationCoordinator.publish`, après l'événement de maintenance facturée. Le WAL doit avoir le reçu mais aucune publication h du batch.
2. **CRASH-POST-H/PRE-RETIRE** : sortie dans le début de `ChargedPendingEpisodeIndex.acknowledge_published`, juste après le retour de `publish`. Le WAL doit avoir reçu + activation h, mais pas d'attestation de retrait.
3. **CRASH-POST-RETIRE** : sortie immédiatement après le journal fsyncé de `stage10_consolidation_index_retired`. Le WAL doit contenir les trois événements, ordonnés et attestés.
Pour chaque point, le parent inspecte les vrais octets WAL, vérifie l'intégralité des maillons SHA-256, unicité des IDs, événements exacts, absence de `step_closed` pour le pas incomplet et statut de la récupération **non certifié**. Le parent ne réinstancie jamais l'individu, ne joue pas une action supplémentaire et ne fabrique pas de décès physique.

## Critères
- **PASS auditabilité** : WAL valide et topologie d'événements attendue pour chacun des points, mêmes budgets et calendrier, sans création de vie après crash.
- **FAIL** : événement h disparu malgré son fsync, h postérieur au retrait, journal invalide, étape physique fabriquée, duplication, ou reprise autorisée depuis une sauvegarde antérieure.
- **Risque architectural distinct** : même si la matrice passe, la fenêtre entre h durable et retrait indexé demeure une **publication non atomique d'états propriétaires**, qui interdit un GO de reprise Stage12. Une évolution n'est acceptable qu'avec un commit propriétaire commun ou un protocole vérifiable de réconciliation durable **sans restaurer l'ancienne vie**.
- Les résultats du banc actuel restent intacts, et aucune surcharge de sommeil, UC ou `w_C` n'est autorisée. Ne pas modifier la norme MVP sans décision opérateur. PR #139 et #133 ouvertes jusqu'à validation opérateur.
