# I1 native-source migration ledger

Date: 2026-10-17. Working PR: #253, stacked on #252 and #251.

## Migration performed

The 13 former `src/i1_overlays/` files now belong to `src/i1/runtime/` (verbatim original Git blobs). At build time they remain installed exactly once into the historical `i1lab.*` namespace, so canonical `birth_i1` and M11 birth identities are unchanged.

A further six I1 cognitive modules now hold their actual behavior **directly in checked-in `src/i1/modules/`**, rather than receiving source-string patches from `scripts/build_i1_fork.py`:

| Native module | Former build-time transformation |
| --- | --- |
| `memory.py` | cached visible competitive references and active-goal identity |
| `consolidation_batch.py` | priority-bounded `heapq.nsmallest` selection |
| `consolidation_pending_index.py` | detached indexed-episode view and privately owned charged ranks |
| `consolidation_pass_runner.py` | copies removed only at already-owned private boundaries |
| `consolidation_transaction.py` | validated candidate-digest metadata and checkpoint custody |
| `consolidation_semantics.py` | I1 six-pass semantic algorithm previously held in a non-Python text template |

**Source-level parity proof**: prior to each Git write, old `rewrite(original)` plus its exact original transformation was compared with `rewrite(new native source)`; all changed modules matched byte-for-byte. The six-pass native module was copied byte-for-byte from the former I1 template, then the former template was deleted. These assertions concern the produced source text, not a scientific result.

No modification was made to `src/i0/**` or `src/lab/**`. No H1/H2 policy was introduced; no runtime module was disabled. The canonical I1 birth continues to execute complete active cognition.

## Real validation

GitHub Actions [#39032352242](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39032352242) passed I1 SMOKE + FULL, real M11 cold recovery, live archive verification and I0 targeted non-regression under Python 3.11 and 3.12. This confirms this incremental migration passes the current software acceptance gate; it is not a full scientific validation of long-term behavioral emergence.

## Remaining migration

The generator still applies other source transformations, in particular to physical world `i1lab.world`, Stage10 runtime/publication, journal operations, Stage11, M11 and owner custody. They must be migrated **only** with explicit output parity, authenticated M11 cold-recovery checks and mortal fail-stop semantics. The aim is ultimately source-native I1 and an ordinary package build, but deleting the generator or changing persistence schema now would be unsafe.

Migration order: (1) native noncritical optimizations, (2) native typed cognitive owners, (3) native physical and durability implementations, (4) remove mechanical source rewriting only when the new build produces equivalent imports/states and the full CI and fresh independent experiments justify the architectural switch.

This work stays on PR #253, dependent on #252 and #251. Do not merge out of order.
## Phase suivante : physique native I1 (2026-10-17)

La copie indépendante `src/i1/runtime/world.py` possède désormais nativement les débits de privation, leurs paramètres versionnés, leur validation, leur sérialisation et les conséquences physiques par pas. Les substitutions `i1_physiology_source` ont été retirées de `scripts/build_i1_fork.py`. Le constructeur copie ce module exactement dans `i1lab/world.py`, sans recopier le `src/lab/world.py` historique. L'identité externe du module `i1lab.world` est préservée. Le test `test_i1_generated_isolation.py` vérifie la provenance `i1/runtime/world.py`, l'unicité du fichier produit et les sources I0/Lab inchangées.

La physique est copiée depuis la version isolée déjà produite précédemment : mêmes paramètres par défaut pour les anciennes naissances explicites, mêmes taux positifs activés par la naissance naturelle, même séquencement après action et mêmes effets de privation. La mort reste irréversible et toute défaillance d'état reste une défaillance, sans rollback.

La CI [#39032694945](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39032694945) a réussi sur Python 3.11 et 3.12 pour le commit `cbc3ce4cd1e4c607335a6c5a28281259bb312280`. Le renforcement ultérieur de l'assertion de provenance dispose de son propre commit et nécessite un contrôle sur ce dernier SHA avant toute fusion. **Aucune conclusion scientifique nouvelle n'est déduite de ce résultat logiciel.**

**Restent à migrer** : transformations de journaux et du sélecteur d'épisodes, publication Stage10 et chaînes M11, puis retrait final du générateur de texte uniquement après vérifications de parité et des naissances/récupérations authentiques.

## Phase suivante : journal causal et vues vécues natifs

Les sources `src/i1/runtime/journal.py` et `src/i1/runtime/journal_views.py` sont désormais détenues par I1 et copiées directement sous `i1lab/` pendant la construction. Trois fonctions de remplacement textuel ont été retirées du générateur : `i1_journal_bounded_view_source`, `i1_journal_full_integrity_copy_source` et `i1_scoped_autobiographical_view_source`.

Le journal conserve la vérification complète des SHA-256 et introduit nativement `entry_count`, `entries_since` et `iter_entries_reversed`; la vue autobiographique peut filtrer les événements sélectionnés tout en vérifiant chaque engagement de source. Les importations I0/Lab ont été réécrites uniquement dans ces copies I1, sans modifier les références d'origine. La naissance, les propriétaires et le format de persistance n'ont pas été modifiés.

La CI [#39033959465](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39033959465) a réussi en Python 3.11 et 3.12 sur `cf8ad3cc`. Le test de provenance du générateur a ensuite été renforcé ; **la réussite du SHA suivant doit être vérifiée indépendamment**. La couverture reste logicielle : il faudra encore des essais de corruption adversariale et de publication non vide à horizon long avant d'annoncer une équivalence complète scientifique et opérationnelle.

La prochaine famille de sources à migrer concerne `consolidation_lived_evidence`, `consolidation_postcut_journal`, les propriétaires Stage10 et la garde M11. Les migrations sensibles ne seront fusionnées qu'après confirmation de la parité et des conditions de refus M11.
