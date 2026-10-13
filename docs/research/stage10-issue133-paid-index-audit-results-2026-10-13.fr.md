# Issue #133 : index payant, contrôle causal indépendant et correction des reçus

Date : 13 octobre 2026. Source de la campagne : `45f1286a473e57e12ef9a25502ffed2b85c306d9`. Préenregistrement : `docs/research/stage10-issue133-priced-pending-index-prereg-2026-10-13.fr.md`, commit `17d7216710a6b54b08e0f03a35aea77038c3b36d`. Référence normative : `docs/architecture/reference/en/mvp-specification-v1.3.1.md` (et les sections Stage10 conservées du MVP v1.2.1). `w_C=0`, `p_cons_min=0`, budgets P-42 100 UC/pas de sommeil et 600 UC/période.

## Campagne H600 achevée, sans relance des vies initiales

[Stage12 #38362163145](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38362163145) : SUCCESS. [CI #38362162933](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38362162933) : quick-unit SUCCESS, **full-validation SKIPPED**. Artefacts originaux immuables : `11796713546` (Python 3.11), `11796777621` (Python 3.12) avec quatre vies chacun. Les deux interpréteurs produisent un export canonique SHA256 octet pour octet identique pour chacune des quatre configurations (deux mondes x deux politiques), sans compter comme quatre graines indépendantes. Chaque vie a 600 pas physiques et 299 épisodes fermés.

| Mesures par monde | Scan intégral F / référence | Index I / référence | Scan F / eau | Index I / eau |
| --- | ---: | ---: | ---: | ---: |
| Références consolidées | 242 | **295** | 238 | **296** |
| Backlog final | 57 | **4** | 61 | **3** |
| UC P-42 totales réellement consommées | 10827 | **6044** | 9791 | **6264** |
| UC débitées pour scan | 6733 | **853** | 5872 | **1094** |
| Part des scans dans les UC | 62,2% | **14,1%** | 60,0% | **17,5%** |
| Publications h | 51 | 61 | 44 | 58 |
| Reports de travail journalisés | 75 | 34 | 76 | 37 |
| Sommeil / mouvements / boire | 313/287/0 | 313/287/0 | 300/299/1 | 300/299/1 |

**Audit indépendant des archives** : relecture complète des 8 journaux `canonical.jsonl` et WAL, recanonicalisation NFC/SHA-256 de chaque entrée, identification unique, intégrité du chaînage, fermeture réelle des épisodes avant la coupure, absence de références publiées plusieurs fois, six checkpoints dans l'ordre avant chaque activation de h, concordance des refs effectivement consolidées, UC par pas <= 100 et UC par période <= 600, sommes UC égales aux traces finales, exactes égalités des hash inter-Python. Aucun défaut constaté dans ces contrôles. Attention : audit documentaire hors-runtime, il ne certifie pas la prise en charge de toutes les fautes M11 ou la valeur cognitive des h produites.

**Pentes comparatives déjà préenregistrées** : dans le monde de référence, backlog I −7 sur les 200 et 80 derniers pas (F +27, +3 selon bornes fin 400/520 vers fin 600) ; monde avec eau : I −17 sur les 200 et 80 derniers pas (F +27, −3). L'hypothèse de régime local à 600 pas est soutenue dans deux mondes, sans preuve générale.

## Défaut d'auditabilité identifié et correctif

Au SHA testé `45f1286`, `index_maintenance` est facturé par `ConsolidationWorkBudget.charge()` avant `coordinator.publish()`, mais **aucun événement individuel du journal ne rattache explicitement ces débits au retrait exact des refs**. Les UC totales incluent les paiements, mais le journal seul ne peut attribuer directement leur montant et le retrait à un batch donné. L'absence d'événement ne prouve pas que les UC sont gratuites ; c'est une lacune de provenance au regard du protocole de campagne.

Correctif poussé au commit [`e056359`](https://github.com/josselin-orta-lab/individual-zero/commit/e05635946b7b1e1a7dbd9409953991f29900efd6) :
- validation de l'existence des refs **après** le paiement, mais **avant** la publication irréversible (une incohérence ne passe plus silencieusement après h) ;
- événement causal `stage10_consolidation_index_maintenance_charged` détaillant refs, décompte, UC et état de l'index **avant** `coordinator.prepare()`, afin de ne pas invalider la preuve postcut figée par la préparation ;
- événement causal `stage10_consolidation_index_retired` uniquement **après** l'activation h et la mise à jour effective de l'index ;
- test logiciel de l'ordre événement de paiement → activation h → attestation de retrait, et bornes UC.

**Ne pas utiliser les anciens résultats H600 comme preuve de reproductibilité de `e056359`.** Le nouveau commit change le journal, donc ses SHA canoniques devraient changer. La nouvelle CI doit passer et la facturation être auditée sur un nouvel artefact. Le traitement du défaut intervient après la mesure, sans réécriture des ZIP antérieurs.

## Risques encore ouverts et verdict

- La modification de l'index juste après la publication h n'est pas une transaction matérielle indivisible en elle-même. Un crash précisément entre les deux opérations nécessite une preuve de cohérence du journal/WAL et de l'état causal, ou un arrêt irréversible contrôlé. **Ne pas prétendre que M11 garantit déjà cette fenêtre.**
- La politique de sélection et la source des épisodes sont inchangées ; le test de priorité sur un flux contrôlé existe, mais une campagne plus large sur l'équivalence des rangs, les interruptions de sommeil et les lots longs est souhaitable.
- La qualité des connaissances consolidées et leur effet sur l'apprentissage ne sont pas établis par la taille du backlog.
- La stabilité reste un phénomène *local* à 600 pas et deux mondes ; charge extrême, profils supplémentaires et validation opérateur restent ouverts.

**Décision : technique des archives 45f1286 conforme sur les scénarios audités ; hypothèse scientifique locale soutenue ; nouveau correctif e056359 non validé tant que ses propres CI et preuves d'ordre causal ne sont pas examinées.** Laisser issue #133 OPEN, ne pas fusionner la PR #139, ne pas changer `w_C=0` et ne pas modifier silencieusement le MVP.
