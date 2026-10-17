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

## Migration native SQLite et capture M11 (2026-10-17)

La branche #253 contient désormais les fichiers natifs `src/i1/runtime/sqlite_life_store.py` et `src/i1/runtime/sqlite_runtime_custody.py`. Quatre transformations de génération ont été retirées : `i1_sqlite_life_audit_canonical_source`, `i1_sqlite_streaming_audit_source`, `i1_sqlite_journal_count_source` et `i1_sqlite_detached_owner_export_source`. La réduction est d'environ 9 173 caractères. Le générateur copie ces sources I1 dans `i1lab` et ne les recopie plus depuis `src/lab`.

Les contrats conservés comprennent la validation canonique de chaque état, le contrôle de la chaîne SHA-256, la continuité du roster de propriétaires, les fences SQLite d'intention, la mort terminale et le refus de reprise M11 en cas d'incertitude. La capture des propriétaires reste non publiante et fail-closed ; seules les instances de types strictement identifiés autorisent des exports déjà détachés.

Le test `test_i1_generated_isolation.py` vérifie la provenance et le contenu direct des deux modules. [GitHub Actions #39034795110](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39034795110) a conclu **success** sur Python 3.11 et 3.12 pour le commit `fe8427ba131bfa156a4b3fe222c2a641a43be5da`.

Le moteur I0 et le Lab historique n'ont pas été changés. L'absence de nouveaux défauts dans cette CI ne remplace pas une campagne adversariale exhaustive de corruptions SQLite, crashes entre COMMIT et ACK et publications Stage10 non vides. Ces scénarios restent des conditions à satisfaire avant la suppression finale du générateur et la fusion de #253.

## Publication Stage10 native et interdiction de retour arrière (2026-10-17)

La source `src/i1/runtime/consolidation_publication.py` contient désormais directement `SlowHistory`, le coordinateur de publication à quatre propriétaires (`value_needs`, `metacognition_health`, `perception`, `causal_model`) et ses contrôles d'états de référence. Six patchs textuels ont été supprimés : `i1_committed_history_metadata_source`, `i1_publication_detached_candidate_source`, `i1_slow_history_preflight_no_full_birth_copy_source`, `i1_no_live_publication_rollback_source`, `i1_stage10_publication_bounded_count_source`, `i1_stage10_canonical_baseline_source`. La réduction du générateur atteint 12 380 caractères pour ce lot.

La source native conserve le refus d'un retour arrière après installation incertaine des propriétaires et la vérification canonique des états. Aucun historique vivant ne doit être restauré pour poursuivre un individu dont la publication a échoué. Le générateur produit `i1lab/consolidation_publication.py` depuis I1 directement ; `test_i1_generated_isolation.py` contrôle sa provenance et le contenu généré.

La [CI #39035056341](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39035056341) est verte sur Python 3.11 et 3.12 pour `b46eb9809e30ac10611bd2f0ee79bfc593982115`. Ce succès couvre les vérifications actuelles I1 SMOKE/FULL et M11 ; il n'établit **pas** une preuve de publication active non vide sur plusieurs consolidations, ni les scénarios adversariaux de crash au milieu de l'installation des quatre propriétaires. Ces lacunes restent à traiter avant la migration définitive du coordinateur Stage10 et la fusion.

## Source native Stage4 et Stage11 (2026-10-17)

Les `src/i1/runtime/stage4_runtime.py` et `src/i1/runtime/stage11_runtime.py` portent maintenant respectivement l'instanciation effective du propriétaire Value/Needs de I1 naturel et les optimisations de découverte géographique/probes facturées. Le constructeur n'applique plus `i1_canonical_active_value_source`, `i1_stage11_owned_geography_lookup_source` ni `i1_stage11_paid_exploration_probe_source`. Les interfaces `i1lab.stage4_runtime` et `i1lab.stage11_runtime` sont préservées. Les modèles expérimentaux importables ne sont pas réactivés comme oracles de I1. I0 et `src/lab` restent inchangés.

La provenance des deux modules est exigée par `test_i1_generated_isolation.py`, avec égalité textuelle au code source I1. CI réelle [#39035745064](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39035745064) pour Stage4 et [#39035838270](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39035838270) pour Stage11 : succès Python 3.11 et 3.12, dont I1 SMOKE/FULL, séparation et reprise M11. Les transformations M11 restantes sont volontairement maintenues tant que l'équivalence sur reprise, publication active et crash n'est pas démontrée par des contrôles adversariaux dédiés.
