# Stage 11 : garde d'occurrence des cycles UC, validation logicielle versionnée

**Date : 11 octobre 2026. Nature : étude et régression logicielle publiques de développement ; NON held-out, NON Golden et NON validation scientifique.** Source normative exclusive et inchangée : `docs/architecture/reference/en/mvp-specification-v1.2.1.md`, §16.3, S-11/P-43, INV-21/INV-22, §17.1–17.6. **Stage 11 EN COURS ; Stage 9 NO-GO scientifique. PR #25 ouverte, Draft, non fusionnée.**

## Antériorité et SHA vérifiés

Le [protocole de garde des occurrences](stage11-scheduler-cycle-occurrence-custody-protocol.en.md) a été enregistré au commit **`4628e557c16cbe9f99ce4da71b82d8cb06e31e5f`**, **avant** tout test diagnostique ou changement de sémantique étudié ici. HEAD de départ : `b017b82110f3664807eaffa03a976b85f3284d4f`. La précédente CI de configuration P-43 [#38140853911](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38140853911) (911/911 sous Python 3.11 et 3.12) reste un historique distinct, non transférable au nouveau code.

1. **Diagnostic négatif préalable :** `431b2eb523cd88b4be839bd5086fe0323479a376`, `tests/test_stage11_cycle_occurrence_custody.py`, trois méthodes. [CI courte #38141702145](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38141702145), **914/914 Python 3.12.15 PASS**, exécution `137,956 s`. L'événement diagnostique public `stage11_legacy_duplicate_open_negative=erased_2_uc` confirme qu'une ouverture répétée directe de `cycle=1` **efface 2 UC** déjà chargées dans le budget historique. Cela ne prouve **aucune** double ouverture dans le runtime normal. Les deux autres tests constatent les occurrences légitimes `cycle=1` de deux pas physiques distincts, avec provenance `t_monde`/`attempt_ref`, et un rejeu indépendant après snapshot.
2. **Code du garde optionnel :** `f7eaf005cfd85eefd857fe257ec29b0f202a2813`, `src/lab/compute_budget.py` ; `bdb319833370b987f3b215d8074feb357f619438`, `src/lab/stage1_runtime.py` ; `280285bc8de90a5cdfee6b3df1a79bfea97668b0`, `src/lab/stage4_runtime.py` ; `e56b23b97b6d7b345114647469816a22e42d2e61`, `src/lab/stage11_runtime.py` ; `5565e9d34dd196d36e0c2f0ee6f06a6755241811`, `src/lab/stage11_routed_junction_probe.py`.
3. **Tests opt-in :** **`2b1537b25326d2586a7d5d7c9881bd05002bd6f7`**, `tests/test_stage11_cycle_occurrence_guard.py`, cinq nouvelles méthodes. C'est le **SHA exact du code/tests validé**. [CI courte #38142093957](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38142093957) : **919/919 Python 3.12.15 PASS**, `138,757 s`. [CI complète #38142308185](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38142308185) : **919/919 sous Python 3.11.17 PASS** (`75,920 s`) et **919/919 sous Python 3.12.15 PASS** (`71,801 s`). Les **deux jobs complets sont SUCCESS**, aucune étape en échec, **15 artefacts** de référence/diagnostic conservés ; job rapide du workflow complet délibérément `skipped` pour limiter les coûts. Ces jobs sont rattachés exactement au SHA source/tests précité.

## Défaut préexistant et frontière du correctif

La méthode historique `CycleComputeBudget.open_cycle(cycle)` accepte tout entier positif et remet sans condition `_consumed_cycle` et `_consumed_by_module` à zéro. Elle ne connaît ni `t_monde` ni `attempt_ref`. Une **double invocation directe pendant la même occurrence** efface donc des UC réellement consommées, ce qui pourrait permettre ultérieurement un dépassement du travail autorisé par P-43. Ce cas est désormais reproduit et conservé comme **résultat logiciel négatif**.

Une interdiction naïve de répéter le numéro de cycle était incorrecte. `Stage1Runtime` et `Stage4Runtime` recommencent leurs cycles cognitifs au prochain pas physique ; `cycle=1` au pas 2 est indépendant de `cycle=1` au pas 1. Une restauration et un nouvel `attempt_ref` après rollback constituent une autre frontière. Les identités techniques ne sont **pas** des connaissances du monde physique offertes à l'individu.

## Design implémenté, opt-in uniquement

La configuration `ComputeBudgetConfig.cycle_occurrence_guard=False` et l'interrupteur `Stage11Config.cycle_occurrence_guard_enabled=False` sont **désactivés par défaut**. Les vies historiques restent sur leur version, leurs quatre champs de budget sauvegardé et leurs journaux inchangés.

Quand le mode est explicitement activé :
- `open_cycle(cycle, occurrence=(t_monde, attempt_ref, cycle))` exige un triplet canonique, construit depuis le contexte réel du Scheduler et non depuis un oracle du monde. Une deuxième ouverture du **même triplet actif** déclenche `RuntimeError` **avant** toute remise à zéro des UC. Un cycle cognitif différent, un nouveau pas physique ou une autre tentative déclarée sont des occurrences distinctes.
- En mode protégé seulement, `export_causal_state()` ajoute `active_occurrence={t_monde,attempt_ref,cycle}` (ou `null` avant ouverture). `restore_causal_state()` impose strictement le schéma et la cohérence avec `cycle`, puis restaure l'identité **atomiquement avec les compteurs** ; elle ne l'infère pas du journal. Un état malformé ou mélangeant les deux schémas est refusé sans mutation.
- Les runtimes Stage 1 et Phase-0 de Stage 4 fournissent le vrai `t_monde`, `attempt_ref` et `cycle` dans leurs appels à `open_cycle`. Le mode par défaut ignore ce nouveau contexte, sans changer les coûts ni les événements.
- La fixture publique du carrefour Stage 11 expose `cycle_occurrence_guard=True` avec un suffixe de version Stage 11 et un suffixe de configuration budgétaire distincts. Aucun résultat historique antérieur n'est réécrit en Golden ni requalifié comme une expérience held-out.

Aucune dépense UC n'est remboursée, masquée ou rendue gratuite ; `charge`, `quote_operations`, les coûts et enveloppes P-43, Action Control, Planning, Exploration, S_t et le mécanisme d'Action Control restent inchangés. La vérification d'identité est un contrôle infrastructurel d'ouverture, non un service cognitif gratuit.

## Contrôles exécutés et portée de chaque preuve

| Contrôle | Preuve logicielle observée |
| --- | --- |
| Double `open_cycle(1)` dans l'API historique directe | **NÉGATIF conservé** : 2 UC effacées, garde par défaut absente |
| Deux pas physiques distincts, même `cycle=1` | **PASS** : `t_monde` et `attempt_ref` distincts, relecture indépendante exacte |
| Mode protégé : contexte manquant, types non canoniques, cycle incohérent | **PASS** : rejet `ValueError`, aucune mutation |
| Mode protégé : second appel même triplet après débit de 2 UC | **PASS** : `RuntimeError`, UC et octets canoniques conservés |
| Même pas/autre cycle ; autre pas/même cycle ; nouvelle tentative synthétique | **PASS** : renouvellement seulement pour une autre identité déclarée |
| Snapshot d'un propriétaire protégé, reprise d'un nouveau cycle, restauration | **PASS** : `active_occurrence`, UC, reçus, hash et journal déterministes |
| Restauration avec `active_occurrence` non canonique, incompatible ou absent | **PASS** : rejet atomique et maintien de l'état antérieur |
| Stage 1 avec vraie provenance et restauration d'un pas précédent | **PASS** : deux exécutions indépendantes, même continuation causale et journal append-only |
| Carrefour Stage 11 opt-in, cinq pas, snapshots après les pas 4 et 5 | **PASS** : version propre, actions physiques conservées dans la fixture comparée, journal et propriétaires identiques entre deux exécutions indépendantes **de la même version** |
| Mode historique désactivé, anciens tests de SHA du danger transitoire | **PASS** dans la suite intégrée ; les empreintes historiques gardent leur contrat |

**Différence attendue :** le schéma et les empreintes du mode protégé diffèrent volontairement du mode historique. Il serait invalide d'exiger le même hash entre deux vies de configurations différentes, ou entre deux calendriers de snapshots différents. Pour chaque version, les reproductions utilisent le même calendrier et le même ordre de captures.

**Limites majeures :** le nouveau garde ne s'applique **pas** aux configurations historiques avec l'option désactivée ; leur défaut d'API direct demeure documenté. La requalification d'un défaut bas niveau en incident réellement arrivé dans le runtime n'est pas autorisée par ces tests. La nouvelle tentative après rollback est couverte **au niveau de l'API synthétique**, pas par une campagne exhaustive de rollback létal du Stage 11 en mode protégé. Le contexte d'occurrence est transmis par des appelants légitimes ; il ne prétend pas confiner du code Python hostile forgeant un autre `attempt_ref` ou modifiant les attributs privés. La propriété post-validation des mappings mutables de `ComputeBudgetConfig` reste un verrou distinct.

La validation Python 3.11/3.12 est une réussite **logicielle**. Les campagnes Goldens historiques à part, les seeds held-out indépendantes, la reconnaissance autonome d'un danger, la récupération, les arbitrages sur horizons longs et le Stage 9 scientifique ne sont **pas** validés par ces résultats. **Stage 9 reste NO-GO scientifique ; Stage 11 reste EN COURS.**

## Reproduction

Checkout du code/tests exact **`2b1537b25326d2586a7d5d7c9881bd05002bd6f7`**, Python 3.11 ou 3.12 et dépendances du dépôt :

```sh
python -m pip install -e .
python -m unittest discover -s tests -p 'test_stage11_cycle_occurrence_custody.py' -v
python -m unittest discover -s tests -p 'test_stage11_cycle_occurrence_guard.py' -v
python -m unittest discover -s tests -p 'test_compute_budget.py' -v
python -m unittest discover -s tests -p 'test_stage11_geographic_capacity_guard.py' -v
python -m unittest discover -s tests -q
```

Le présent rapport est **postérieur** aux campagnes et ne prétend pas être lui-même un nouveau SHA logiciel testé. **Aucune modification de `main`, aucune fusion, aucun force-push, aucune permission ou protection de branche modifiée, et aucun changement de la spécification normative v1.2.1.**
