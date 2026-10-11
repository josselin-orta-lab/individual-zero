# Pré-audit de migration v1.3.0 sur la base intégrée des Stages 10 et 11

**Date :** 11 octobre 2026  
**SHA exact de référence :** `4062c16c1f7b125f84c3d75edec1ada397babb68` (`main`, PR #35 fusionnée par squash)  
**Objet :** vérification initiale **en lecture seule** des dépendances à modifier avant de déclarer I0 mortel et sans journal exhaustif.  
**Classification :** diagnostic d'ingénierie ; pas de preuve scientifique, pas d'acceptation v1.3.0.  
**Autorisation :** l'opérateur a déclaré les Stages terminés et demandé leur intégration dans `main` puis la poursuite des modifications.

## 1. État réellement intégré

L'intégration contient le Stage 11 à partir de `aefba305c204779a99e8d28c5e1c7fc69464eb1d`, le Stage 10 de la PR #29 à `9814a2d69e695af8b7b848873012151618cbc4b0` via la PR #34, la PR #26 et les deux blobs de six passes sémantiques publiés au SHA `1d27e8e47ba2794b0400eb9eca13aedee9f00218`.

Preuves sur la **branche combinée** :
- [CI rapide Python 3.12 #38148420381](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38148420381) : `success`, tests unitaires et smoke.
- [CI complète Python 3.11 / 3.12 #38148493255](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38148493255) : les deux jobs `full-validation` ont terminé avec `success`.
- Le Stage 11 dispose par ailleurs de sa campagne de stabilité publique de 600 pas sur son SHA logiciel antérieur. Ne pas confondre cette preuve avec une campagne intégrée Stage 10+11 de 600 pas ou une validation scientifique.
- **Stage 9 : SCIENTIFIC NO-GO historique inchangé.**

**Limite essentielle :** les dernières sources Stage 10 possèdent des composants de consolidation, de six passes et de publication coordonnée, mais l'audit d'activation du runner sémantique dans `Stage10Runtime` reste à faire. Une présence de fichier et des tests unitaires ne démontrent pas à eux seuls la consolidation de bout en bout sur une vie réelle.

## 2. Inventaire ciblé effectivement inspecté

Inspection en lecture seule de **18 fichiers sources** sur `main` ; il ne s'agit pas du scanner exhaustif sur un clone local. Les chemins et lignes ci-dessous correspondent au SHA figé et doivent être recalculés après chaque migration.

| Priorité | Frontière et preuve source | Risque / décision |
| --- | --- | --- |
| **P0** | `src/lab/stage2_runtime.py:237,266,288` | Snapshot de type `LETHAL_CHECKPOINT` avant commande, `handle_lethal` puis retour `rolled_back` ; **migration indispensable**. |
| **P0** | `src/lab/safety_protocol.py:45,109,140,188` | `LethalSafetyProtocol` restaure l'état, incrémente des rollbacks et réouvre une tentative ; remplacer par statut terminal. |
| **P0** | `src/lab/scheduler.py:187-202` | Création d'une nouvelle tentative après rollback ; interdire pour le runtime vivant v1.3.0. |
| **P0** | `src/lab/stage3_runtime.py:190-247,283` | Transmission de checkpoints et reprise de délibération après réflexe létal ; garantir propagation `dead`. |
| **P0** | `src/lab/stage4_runtime.py:900,965,1055-1058` | Chemin cognitif fait `continue` après `rolled_back` ; remplacer par arrêt terminal. |
| **P0** | `src/lab/stage7_runtime.py:364`, `src/lab/stage10_runtime.py:432,495` | Envoi des commandes via les arguments de checkpoint ; tenir compte du chemin `dormir` et des réveils. |
| **P0** | `src/lab/injected_scenario.py:183,221-236` | Compensation `world.restore_causal_state` d'un lot externe partiellement appliqué ; remplacer par validation et commit atomique non rétroactif. |
| **P1** | `src/lab/snapshots.py:23,240-258` | Type létal et restauration des propriétaires ; distinguer copies de l'import courant, bannir restauration de la vie. |
| **P1** | `src/lab/bench.py:18,68-72` | Métrique `lethal_rollbacks` et trace associée à retirer des parcours mortels. |
| **P1** | `src/i0/modules/action_control.py:579` | Règle `rollback_sequence_mask` à supprimer **sans modifier** les veto informés. |
| **P1** | `src/lab/journal.py`, `src/lab/journal_views.py:57-169` | Historique complet et `AutoSegmentCommit` ; migration après flux transitoire vécu et preuve d'équivalence. |
| **P1 / critique Stage 10** | `src/lab/consolidation_postcut_journal.py:78-89` | Interface requiert un `HashChainedJournal` réel ; suppression prématurée ferait perdre la preuve des mises à jour post-coupure. |
| **P1 / critique Stage 10** | `src/lab/consolidation_publication.py:118-136,230-297` | Publication actuelle attachée au journal technique et aux restaurations de propriétaires en cas d'échec. Préparer les versions privées et leurs deltas avant remplacement. |
| **P1** | `src/lab/stage10_runtime.py:132-145` | Compensation des parties de propriétaire métacognitif en cas de restauration échouée ; auditer la frontière « privé non publié » versus « état causal validé ». |
| **P1** | `src/i0/modules/memory.py`, `src/i0/modules/consolidation_semantics.py`, `src/lab/stage11_runtime.py:1074` | Préserver événements vécus et origine des signaux. Le commentaire Stage 11 mentionne encore la restauration létale. |

### Classification et prudence

Un `restore_causal_state` n'est **pas automatiquement** un rollback interdit : un chargement de l'état courant cohérent ou une copie expérimentale indépendante peut le nécessiter. En revanche, restaurer un état **déjà remplacé par une transition de vie commise**, ou faire disparaître une mort, contrevient sans ambiguïté au contrat.

L'outil `scripts/audit_mvp_v1_3_dependencies.py`, livré dans la branche v1.3 documentaire, constitue l'inventaire généralisé à exécuter sur un vrai checkout. Ce rapport ciblé **ne prétend pas l'avoir exécuté**.

## 3. Contrat de migration et séquencement autorisé

1. **Mortalité d'abord**, en PR isolée : conserver strictement la physique de `WorldBody.apply` ; résultat `dead` irréversible, aucune redélibération, aucun apprentissage post mortem, aucune résurrection. Adapter les callers Stage 10 sommeil et Stage 11.
2. **Transactions du monde ensuite**, en PR séparée : entrée externe préparée/validée et publiée atomiquement ; impossibilité de rollback une transition commise. Refus `technical_halt` si l'intégrité n'est plus prouvable.
3. **Flux autobiographique transitoire** : prouver les mêmes épisodes, commandes physiques et mises à jour sur les trajectoires non mortelles avant de retirer le journal technique.
4. **Consolidation Stage 10** : remplacer `Stage10PostCutJournal` par des deltas bornés, locaux aux propriétaires et sans perte. Garantir six passes privées, interruption, rebase et commit atomique, puis traiter la persistance minimale.
5. **État causal courant et preuves ciblées** : après remplacement des lecteurs, supprimer archive exhaustive et snapshots de protection, préserver copies distinctes et métriques expérimentales nécessaires.
6. **Tests et documentation** : migrer les tests historiquement centrés sur les rollbacks en preuves positives du nouveau comportement ; maintenir provenance, données négatives et statuts scientifiques historiques.

**Aucun de ces lots ne peut être déclaré terminé simplement parce que les documents normatifs ont été publiés.** Les critères M-01 à M-15 de la v1.3.0 doivent être vérifiés sur le SHA effectif.

## 4. Cas indispensables à tester sur la vraie base de migration

- Mort par zone inconnue, baie toxique, créature nocturne, intégrité zéro et dommages cumulés ; chaque effet physique demeure dans l'état final et aucune action supplémentaire n'est envoyée.
- Mort pendant un réflexe, au cours d'une décision, et pendant un pas de sommeil Stage 10 ; aucun cycle ni consolidation post mortem.
- Deux exécutions indépendantes de mêmes commandes et aléas : états physiques identiques, même si les journaux techniques historiques ont changé de représentation.
- Refus de restauration d'une identité morte ; copie préexistante indépendante qui n'est pas transformée en résurrection.
- Aucune fuite d'oracle, de masque externe ou d'observation du banc vers Valeur, S_t, Mémoire, CausalModel ou Consolidation.
- Pas non mortels sur plusieurs épisodes : empreintes de Q/κ/TD/Memory et décisions identiques après substitution de journal.
- Consolidation interrompue avec mises à jour en ligne après cut-point : aucune perte, aucun travail UC non débité, aucun commit partiel.
- Entrée scénario techniquement invalide : aucun effet public ni compensation rétroactive après une transition validée.

## 5. Verdict de préflight

**GO pour commencer une migration technique contrôlée, lot par lot, sur des branches depuis la nouvelle `main`.**

**NO-GO pour déclarer le runtime conforme v1.3.0 ou fusionner le prototype PR #31 en l'état** : il a été développé avant les derniers travaux du Stage 10/11 et ne contient ni la migration des nouveaux consommateurs ni l'ensemble de leurs tests.

Le développement peut commencer sans autre question, conformément à la demande explicite de l'opérateur. Chaque fusion vers `main` reste conditionnée à ses propres tests et à la protection de branche.
