# Audit différé de migration : Individual Zero MVP v1.3.0

**État : PRÉPARÉ — NON EXÉCUTÉ SUR LA BASE FINALE — MIGRATION INTERDITE AVANT FEU VERT.**  
**Date de préparation :** 11 octobre 2026  
**Cible normative :** [MVP v1.3.0 (anglais)](../../architecture/reference/en/mvp-specification-v1.3.0.md) ; [français](../../architecture/reference/fr/mvp-specification-v1.3.0.md)  
**Référence historique du travail en cours :** MVP v1.2.1 anglais, conservé inchangé.  
**Branche de préparation :** `i0/mvp-v1.3-mortal-audit` (documents et outils d'audit seulement).  
**Ne pas fusionner, rebaser ni interrompre les branches des agents.**

## 0. Mission, limites et résultat attendu

À la fin **validée par l'opérateur** des Stages 10 et 11, mener un audit technique, architectural et de dépendances **en lecture seule** qui prépare une migration vers la mortalité irréversible et la suppression du journal exhaustif **sans modifier la physique du monde ni les règles cognitives**.

L'audit produit :

1. Le SHA de base figé, les références des branches/PR sources et les validations de chaque agent et de l'opérateur.
2. L'inventaire exhaustif des chemins d'exécution, restaurations, checkpoints, journaux permanents et dépendances aux événements.
3. Une matrice de conversion **ancien contrat → nouveau contrat → test d'équivalence → propriétaire → risque**.
4. Des priorités de migration ordonnées, fichiers touchés, tests obsolètes, nouveaux tests et points de blocage.
5. Un rapport de divergences mesurées sur des fixtures connues, sans usage de campagnes held-out ni revendication scientifique.
6. Une recommandation de lancement **GO / NO-GO / GO CONDITIONNEL** soumise à approbation explicite de l'opérateur.

L'audit ne modifie aucun fichier de runtime, aucune politique d'accès GitHub, aucun rapport scientifique antérieur et aucun verdict Stage 9.

## 1. Conditions obligatoires avant tout audit final

| Gate | Preuve exigée | État au 11/10/2026 |
| --- | --- | --- |
| G-01 | Stage 10 terminé selon périmètre et preuves logiciel/600 pas ; décision de l'opérateur explicite | **NON ATTESTÉ** |
| G-02 | Stage 11 terminé selon périmètre et preuves logiciel/600 pas ; décision de l'opérateur explicite | **NON ATTESTÉ** |
| G-03 | Toutes les branches de travail effectivement retenues sont connues et figées à des SHA identifiés ; aucune écriture concurrente sur la base d'audit | **NON ATTESTÉ** |
| G-04 | Les PR empilées Stage 10 ont un plan d'intégration sans ambiguïté, sans retcon scientifique | **NON ATTESTÉ** |
| G-05 | L'opérateur autorise explicitement l'**audit final en lecture seule** de la base intégrée | **EN ATTENTE** |
| G-06 | Audit final conclu et opérateur autorise **séparément** le développement de migration | **EN ATTENTE** |

**IMPORTANT :** La publication de cette spécification et la création de l'audit ne prouvent aucune de ces conditions. Si G-01 à G-05 ne sont pas atteintes, ne pas appeler l'audit préparatoire une validation finale. Si G-06 manque, ne pas lancer le moindre refactoring runtime.

### Sources GitHub à réconcilier après livraison des agents

| Périmètre connu | Branche / PR | Utilité |
| --- | --- | --- |
| Stage 11 et intégration vNext | `i0/vnext-stages-10-12`, [PR #25](https://github.com/josselin-orta-lab/individual-zero/pull/25) | Source Stage 11 ; évolue pendant l'audit préparatoire |
| Stage 10 fatigue/sommeil | `i0/stage10-sleep-health-integration`, [PR #26](https://github.com/josselin-orta-lab/individual-zero/pull/26) | Travail empilé ; vérifier s'il a été repris/fusionné dans la base intégrée |
| Stage 10 consolidation et Stage 12 fondations | `i0/mvp-parallel-completion`, [PR #29](https://github.com/josselin-orta-lab/individual-zero/pull/29) | Travail parallèle ; risque élevé de conflits sur consolidation, journaux et contrats atomiques |
| Prototype non validé de mortalité | `i0/mortal-world-no-rollback`, [PR #31](https://github.com/josselin-orta-lab/individual-zero/pull/31) | Matériel expérimental à auditer puis adapter ; **ne pas fusionner directement** |
| Cible et audit | `i0/mvp-v1.3-mortal-audit` | Docs et outil en lecture seule, sans implémentation |

**SHA de développement observé lors de la création de l'audit :** `3cdc5d4d151b9790901368056732e6e7e3aec519` pour `i0/vnext-stages-10-12`. Ce n'est **pas** le SHA final gelé. L'agent doit recalculer et enregistrer toutes les références à l'ouverture de l'audit final.

## 2. Inventaire initial des chemins à inspecter

Ces indications proviennent des fichiers et PR observés avant la fin des agents. Elles sont **provisoires** ; refaire la recherche complète sur les SHAs gelés.

| Priorité | Fichiers / zone | Risque à vérifier | Migration recherchée |
| --- | --- | --- | --- |
| **P0** | `src/lab/world.py` | Physique modifiée par inadvertance pendant le retrait du rollback ; états mortels écrasés | **Ne pas changer les règles de physique** ; figer des comparaisons d'états avant/après transition |
| **P0** | `src/lab/stage2_runtime.py`, `src/lab/safety_protocol.py` | Checkpoint avant chaque commande, restauration létale, protocole de masque, compteur, nouvelle tentative | Terminal `dead`, exécution unique, aucune restauration ni réanimation |
| **P0** | `src/lab/stage3_runtime.py`, `src/lab/stage4_runtime.py`, `src/lab/stage7_runtime.py` | Réflexe létal rejoué ou délibération relancée ; résultat `rolled_back` attendu ; fermeture TD incorrecte | Propager `dead` immédiatement et préserver les seules mises à jour valides |
| **P0** | `src/i0/modules/action_control.py` | Filtrage masqué supprimé avec suppression accidentelle des veto légitimes | Conserver réflexes et veto **fondés sur les connaissances**, enlever seulement le masque létal |
| **P0** | `src/lab/scheduler.py` et autres chemins d'émission | `new_attempt_after_rollback`, fermeture avec compte physique nul après mort, pas supplémentaire | Compter 1 commande / 1 transition / 1 fermeture terminale |
| **P0** | `src/lab/injected_scenario.py` | Restauration du monde si lot externe rejeté après mutations partielles | Prévalidation et publication atomique ; sinon `technical_halt`, jamais compensation d'état validé |
| **P0** | `src/lab/snapshots.py` et propriétaires de snapshots | Restauration d'un mort, instantanés létaux, points historiques réutilisés | État causal courant unique ; snapshots de **copies distinctes** uniquement à la demande |
| **P1** | `src/lab/journal.py`, `src/lab/journal_views.py`, `src/lab/events.py`, `src/lab/sinks.py` | Journal causal complet sert d'infrastructure de distribution cognitive et d'audit | Flux transitoire vécu, provenance minimale et preuves externes bornées |
| **P1** | `src/i0/modules/memory.py`, `src/lab/stage7_runtime.py` | Episodes et intentions dépendent des événements retenus après `AutoSegmentCommit` | Alimenter exactement les mêmes faits vécus par un nouveau flux borné |
| **P1** | `src/i0/modules/td_values.py`, `src/i0/modules/causal_model.py`, `src/lab/stage9_runtime.py` | Dédoublonnage, provenance physique, apprentissage TD et interventions basés sur des ID/journaux | Remplacer par identifiants locaux causaux uniques, sans fabrication de preuve |
| **P1** | Stage 10 : `consolidation_transaction`, `consolidation_pass_runner`, `consolidation_replay_agenda`, `sleep_health`, et intégrations définitives | Rebase lisant toutes les mises à jour post-coupure dans le journal ; compensation de transactions après publication | Deltas causaux locaux conservés jusqu'au commit ; états privés non publiés annulables |
| **P1** | Stage 11 : `stage11_runtime.py`, Exploration, modulation, routage géographique, prédiction vécue | Visites, métriques et capteurs comptent une tentative restaurée ou des événements techniques | Mesurer uniquement conséquences physiques réelles et preuves vécues autorisées |
| **P1** | `src/lab/bench.py`, `src/lab/replay.py`, batterie, harness Stage 9 et tests scientifiques | `lethal_rollbacks`, archive complète, hypothèse que toute vie est rejouable | Compteurs de morts/résultats, traces sélectionnées, signatures d'états ; préserver l'isolation oracle |
| **P2** | `docs/architecture/IMPLEMENTATION_MAP_V1.2.1.md`, runbooks, fixtures, étiquettes de CI et schémas | Sources obsolètes et affirmations scientifiques non justifiées | Marquer historiques ou fournir remplacements, sans réécrire les preuves antérieures |
| **P2** | Copies, trait battery, tests de résistance, archivage | Sauvegarde cachée réactivant un mort ; parent contaminé par une copie | Identités distinctes, pas de transfert rétroactif, mesure scientifique séparée |

Tout module non listé qui utilise `JournalEvent`, `SnapshotManager.restore`, des `restore_causal_state` en cours de vie, des hashes d'événements globaux, ou une transition létale doit être ajouté à l'inventaire, pas ignoré.

## 3. Audit mécanisme par mécanisme

### A. Mortalisation et conséquences du monde

- Vérifier que les prédicats de létalité sont uniquement ceux du monde historique.
- Vérifier l'ordre : admission normale → commande unique → effets physiques complets → résultat létal éventuel → état `dead` → fermeture et arrêt.
- Comparer zone létale cachée, baie létale, faim, nuit/créatures, dégâts cumulés, et erreur de prédiction.
- Vérifier qu'un danger inconnu ne devient pas connu du seul fait de l'analyse externe, et que les veto sur danger connu restent actifs.
- Vérifier les cas réflexe, délibération, `attendre`, `dormir` et action interrompue.
- Vérifier l'absence de réémission, de seconde transition, de nouveau cycle ou de publication cognitive après la mort.
- Comparer les corps, positions, inventaires, ressources et états aléatoires à `WorldBody.apply` sur les mêmes entrées.

### B. Suppression de tous les retours historiques

- Recenser **tous** les appels `restore`/`rollback`/`checkpoint` utilisés en production, sans confondre import initial d'une copie et rechargement de l'état courant.
- Inspecter le scénario d'entrée externe, les transactions de consolidation, le planificateur, le budget UC et les interfaces de snapshots.
- Exiger un schéma de prévalidation et commit atomique pour toute opération auparavant « réparée » après publication.
- Interdire un mécanisme d'auto-sauvetage même s'il est caché derrière un test, un mode diagnostic ou un argument de compatibilité.
- Tester le cas critique « erreur après premier effet externe du lot » : il ne doit rester ni commit partiel ni compensation d'une transition déjà validée.
- Tester la restauration d'un état `dead` sous le même identifiant : rejet sans ambiguïté.

### C. Retrait de l'archive exhaustive sans amnésie

- Construire une matrice **émetteur → ancien type d'événement → lecteur autorisé → nouvelle interface → durée de rétention**.
- Pour chaque accès de Mémoire, Consolidation, Valeur/Besoins, Exploration, CausalModel, Metacognition et Planification, prouver l'équivalence des champs réellement nécessaires.
- Préserver les IDs d'épisodes et la provenance physique nécessaires à la distinction entre perception, action, hypothèse et intervention.
- Vérifier que la mémoire continue de recevoir tous les événements **vécus légitimes**, pas les observations de l'oracle ni un résultat mortel posthume.
- Conserver jusqu'à consommation **tous les deltas causaux post-coupure** de chaque propriétaire de la consolidation, même si des pas de vie ont lieu pendant un sommeil interrompu.
- Prouver qu'après la frontière de consommation, les événements techniques intermédiaires peuvent être effacés et que la taille du stockage ne croît pas linéairement avec le nombre total de cycles d'une vie à mémoire apprise constante.
- Tester les prises de copie et la filiation sans journal partagé de préfixe de vie.

### D. Preuves, métriques et scientifiques

- Fixer un manifest des versions, graines et conditions causales sur lesquelles porte chaque diagnostic.
- Remplacer les obligations de replay historique par comparaisons de transitions et d'empreintes d'état dans des exécutions **indépendantes** de test.
- Ne jamais réécrire un verdict Stage 9 historique NO-GO.
- Chaque Stage : séparer tests unitaires, campagne minimale **600 pas effectivement exécutés**, hypothèses de fonctionnement, tests opérateur éventuels et validation explicite.
- Mort précoce : conserver mort et dénominateur, poursuivre seulement avec **de nouveaux individus de test**, jamais la même identité ressuscitée.
- En fin de projet seulement : campagne scientifique indépendante et tests séparés pour chaque module, avec critères de falsification, résultats négatifs et incertitudes.

## 4. Cartographie des tests à réviser

**Tests historiquement concernés, à confirmer contre le SHA final :**

| Groupe | Exemples | Remplacement recherché |
| --- | --- | --- |
| Stage 2 | `tests/test_stage2_runtime.py`, `tests/test_scheduler.py` | Mort terminale ; monde non restauré ; aucun `attempt_ref` supplémentaire au même pas |
| Stage 3 | `tests/test_stage3_runtime.py`, `tests/test_action_control.py` | Un réflexe mortel termine l'instance ; veto connu inchangé, pas de masque létal |
| Stage 4 / budget | `tests/test_stage4_runtime.py`, `tests/test_compute_budget.py` | Mort pendant délibération ; aucun cycle supplémentaire ; UC déjà consommées respectées |
| Stage 7 / 8 / 9 | tests Mémoire, TD, κ, causalité, événements physiques | Expériences non mortelles équivalentes et absence d'apprentissage posthume |
| Stage 10 | nouveaux tests de transactions, sommeil, rebase et réveil sur branches agents | Abandon de brouillons privés, jamais rollback de vie ; deltas non perdus |
| Stage 11 | `tests/test_stage11_guarded_lethal_rollback.py` et tests de hazards/snapshots | Retirer les assertions « monde restauré » et vérifier la mort effectivement vécue physiquement |
| Reproductibilité / copies | `tests/test_replay.py`, `tests/test_snapshots.py`, `tests/test_stage5_copies.py` | Exécution indépendante et état courant ; aucun chemin de résurrection |
| Banc et oracle | `tests/test_oracle_bench.py`, `tests/test_causal_journal.py`, `tests/test_journal_views.py` | Métriques légères, flux vécu isolé, absence de fuite oracle |

**Ne jamais simplement supprimer un test rouge pour obtenir un résultat vert.** Remplacer une assertion obsolète par un test positif du nouveau contrat, documenter la couverture avant/après, et préserver les fixtures scientifiques historiques sans fausser leur interprétation.

## 5. Exécution reproductible de l'audit après validation

Le script `scripts/audit_mvp_v1_3_dependencies.py` fournit un **inventaire statique en lecture seule** du checkout sélectionné. Ses alertes ne sont ni des preuves de défaut ni des validations automatiques. Les matches appartenant à des commentaires, tests historiques ou fixtures isolées doivent être classifiés manuellement.

Mode d'emploi **uniquement après G-01 à G-05**, sur un clone local de la base intégrée gelée :

```sh
git rev-parse HEAD
python3 scripts/audit_mvp_v1_3_dependencies.py --root . --json-out /tmp/i0-v1.3-impact.json
python3 -m unittest discover -s tests -p 'test_*.py'
```

Les tests et expériences complémentaires sont définis **après** lecture des résultats et par ordre de priorité. Respecter la politique de budget CI ; aucune campagne longue ni emploi des données held-out sans autorisation. Ne pas commencer par lancer des centaines de jobs GitHub Actions.

Pour chaque match statique retenu, noter le chemin et le numéro de ligne, l'appelant effectif, l'effet causal, l'ancien et le nouveau contrat, la preuve attendue, la sévérité et la décision.

## 6. Risques rédhibitoires et critères de blocage

| Criticité | Blocage |
| --- | --- |
| **P0 / NO-GO** | Restauration de monde, corps ou cognition après une transition létale commise |
| **P0 / NO-GO** | Toute modification involontaire des lois physiques ou du résultat d'une commande admise |
| **P0 / NO-GO** | Une instance morte peut continuer, être rechargée vivante ou partager son identité avec sa copie |
| **P0 / NO-GO** | Une entrée invalide publie partiellement une transition puis la corrige en arrière |
| **P0 / NO-GO** | Fuite d'oracle ou d'information technique vers la cognition |
| **P1 / NO-GO tant que non résolu** | Retrait du journal alors que Mémoire/Consolidation perd des expériences autorisées ou des deltas post-coupure |
| **P1 / NO-GO tant que non résolu** | Une anomalie de test est dissimulée par retrait des assertions, réécriture des preuves ou interpolation de pas après mort |
| **P1 / NO-GO tant que non résolu** | Collision entre les derniers travaux des agents Stage 10 et 11 ou base finale non figée |
| **P2 / suivi** | Index docs, affichages CLI, métriques descriptives, anciennes références non exécutées ; doivent être mis à jour avant intégration finale |

Une seule anomalie P0 non levée implique **NO-GO** pour la migration. En présence d'une incompatibilité de consolidation, **ne pas commencer par supprimer l'archive d'événements** ; migrer d'abord ses consommateurs et prouver l'équivalence.

## 7. Découpage proposé après autorisation de migration

**Lot 0 — baseline figée.** Consigner les SHA exacts, manifestes, API et rapports des Stages 10/11 ; établir la série de tests de physique et d'apprentissage de référence.

**Lot 1 — mortalité.** Supprimer le checkpoint létal et le chemin de restauration ; fermer physiquement le pas `dead`. Comparer les effets du monde à l'identique. Réconcilier le prototype PR #31 manuellement, sans cherry-pick aveugle.

**Lot 2 — atomicité sans correction rétroactive.** Adapter les injections de scénario, les contrôles de publication et les persistances pour préparer avant de publier ; `technical_halt` sur incertitude technique.

**Lot 3 — mémoire et consolidation.** Ajouter le flux vécu borné et les deltas locaux jusqu'au commit ; démontrer que les apprentissages restent identiques en vie non mortelle.

**Lot 4 — persistance minimale.** Remplacer le journal exhaustif par l'état courant, l'empreinte d'intégrité et les preuves ciblées ; contrôler les anciennes fonctions de replay/restauration et les copies.

**Lot 5 — tests, documentation et acceptation.** Faire converger les tests, fixtures, métriques et nouvelles règles 600 pas ; remettre un dossier opérateur et solliciter son feu vert.

Chaque lot obtient une PR indépendante ou une série de commits révisables, tests ciblés, état explicite et règle de non-fusion. **Pas de migration silencieuse de toutes les dépendances en une seule opération.**

## 8. Fiche d'audit final à compléter

Remplir **après** la clôture des Stages ; laisser `PENDING` et non `PASS` tant qu'aucune preuve n'est disponible.

| Champ | Valeur |
| --- | --- |
| SHA final Stage 10 / branches intégrées | `PENDING` |
| Décision et date validation opérateur Stage 10 | `PENDING` |
| SHA final Stage 11 / branches intégrées | `PENDING` |
| Décision et date validation opérateur Stage 11 | `PENDING` |
| SHA exact du checkout d'audit | `PENDING` |
| SHA des documents normatifs v1.3.0 revus | `PENDING` |
| Hash et chemin du rapport d'inventaire statique | `PENDING` |
| Tests de physique / mortalité / mémoire exécutés | `PENDING` |
| Résultats de non-régression et limites | `PENDING` |
| Liste des risques P0/P1/P2 avec décisions | `PENDING` |
| Avis final audit `GO / NO-GO / GO CONDITIONNEL` | `PENDING` |
| Autorisation opérateur de lancer les changements | `PENDING` |

**Règle finale :** Ne pas interpréter cet audit préparé comme un audit passé, ni la cible normative v1.3.0 comme une modification déjà installée. Attendre la fin validée des deux Stages, figer la base réelle, auditer, soumettre, puis seulement implémenter.
