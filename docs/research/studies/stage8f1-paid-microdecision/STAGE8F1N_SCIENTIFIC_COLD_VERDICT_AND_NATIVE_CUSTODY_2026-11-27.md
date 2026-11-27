# Stage8-F1N | Verdict scientifique froid et audit des originaux du tir unique

**Audit et consignation : 27 novembre 2026. Tir scientifique original : 26 novembre 2026, GitHub Actions [#45824249204](https://github.com/josselin-orta-lab/individual-zero/actions/runs/45824249204).**

**Statut : `F1N_COMPLETE_SEPARATE_SCIENTIFIC_VERDICTS`, verdicts M/A/B tous NEGATIFS.** Cette pièce est **postérieure** à l'exposition de la cohorte. Elle rapporte des preuves désormais gelées. Elle ne remplace ni le préenregistrement du 25 novembre, ni la lecture froide immuable, et ne peut ni redéfinir les critères, ni entraîner un second tir.

## 1. Chaîne de réservation préexposition et droits

- **Source approuvée effectivement lancée** : `89f58723789ad0c88336b6e5b0eb7ff3227348a1`, arbre Git `464d02f2e974355917f1bcc4e4402ea6996d557c`, même arbre que les deux répétitions DEV distinctes [#45806263524](https://github.com/josselin-orta-lab/individual-zero/actions/runs/45806263524) et [#45806304129](https://github.com/josselin-orta-lab/individual-zero/actions/runs/45806304129), chacune six jobs `SUCCESS`.
- **Préenregistrement F1N exact, antérieur au tir** : prose Git blob `ff07a8db807bee15277052ea71e1e76321286ab9`, grille Git blob `c522d092cb7c1777ebb0f56c4162f61948b35653` (N01..N48, graines 202611259801..202611259848, huit écologies × six racines, génotype fixe `midpoint()`).
- **Exécution première et unique** : `event=workflow_dispatch`, `run_attempt=1`, `head_branch=main`, `head_sha=89f587...`, acteur propriétaire `josselin-orta-lab` ; les **trois jobs** `source_reservation_and_native_original`, `independent_python312_cold` et `final_immutable_cold_publication` sont `completed/success`.
- **Réservation IRREVERSIBLE avant toute naissance** : `refs/heads/i3-stage8-f1n-heldout-consumed-once` pointe sur `38d1c94a146d32bd89151fca906a26a775052560`. Marqueur `F1N_T60_CONSUMED_BEFORE_EXPOSURE.json` sur cette référence, Git blob `c14d3905746ea2cf975419e4f6d7dc7b936a97f0`, garde `F1N_IRREVERSIBLY_RESERVED_BEFORE_FIRST_BIRTH` à 12:56:12 UTC, `F1N_REMOTE_CLAIM_VERIFIED` à 12:56:14 UTC, avant production des originaux à 13:06 UTC.
- **Protection active vérifiée** : ruleset repository F1N **#28160088**, une seule inclusion exacte, `bypass_actors=[]`, `enforcement=active`, règles `deletion/update/non_fast_forward` ; la création initiale était autorisée. Politique de Releases immuables `enabled=true` authentifiée par jeton Admin:read. **Ne jamais recréer, mettre à jour ni rebrancher cette référence.**

## 2. Conservation des preuves et contrôle distinct des octets

- [Release RAW F1N immuable](https://github.com/josselin-orta-lab/individual-zero/releases/tag/i3-stage8f1n-t60-raw-heldout-once) : `immutable=true`, cible le commit consommé `38d1c94a...`. Asset `F1N_ORIGINALS_336_GZIP.tar.gz`, taille **307 618 201 octets**, SHA-256 **`8995e25ced26dceb85737da6b8e01fd94c3877421238f1fccc0c7dd0e3d01ea6`**. `F1N_CUSTODY_MANIFEST.json` SHA-256 `72c3d13da7a3266e0b71e670cfb930ce08470778d227bc1d7728c447a4dbea50`. Reçu GitHub `F1N_RESERVATION.json` SHA-256 `eddbc55147e2cf3f73659939d2964d4288dae830214b97c6e8cf627ea85e18e1`.
- Artefact GitHub Actions source `f1n-once-native-45824249204`, [run #45824249204](https://github.com/josselin-orta-lab/individual-zero/actions/runs/45824249204), **307 700 782 octets**, SHA-256 du ZIP `d2f03adc52cb8da95d11036e0d0344978dbef193ff4177a775dfa0470d3b5820`.
- **Contre-lecture nouvelle et indépendante du job froid** à partir de cet artefact téléchargé : analyse Python stdlib du ZIP, `tarfile` du tar gzip original, `gzip.decompress` de **chacun des 336 témoignages natifs** ; pour chaque témoignage, recomparaison de la taille **et** du SHA-256 des octets gzip compressés et des octets JSON décompressés à la ligne du manifeste original. Résultat : **336/336 SHA gzip PASS, 336/336 SHA JSON PASS, 0 octet non conforme**, total **320 717 508 octets gzip** et **2 293 778 312 octets décompressés**. **48/48 origines**, exactement **7 témoignages par origine** ; **48/48 checkpoints `_checkpoint_01.json` à `_checkpoint_48.json`**, 0 partie dupliquée, 0 membre non prévu. Il s'agit d'une vérification des fichiers conservés, **sans exécuter World.step ni rejouer les vies**.
- [Release COLD F1N immuable](https://github.com/josselin-orta-lab/individual-zero/releases/tag/i3-stage8f1n-t60-cold-heldout-once) : `immutable=true`, même commit consommé. `F1N_INDEPENDENT_COLD_T60.json`, SHA-256 **`650aee67b3d356bc4dd359721b0f279e8af6a5648d35bc4de9350aa128ac681b`** (19 567 octets), et `F1N_BYTE_CUSTODY_COLD.json`, SHA-256 `f68df9aa1d111765c5f0c3c0b6924d9e68f0dc4444f3fd2486561028722e77cb`. Le rapport froid indique **7/7 assets RAW** authentifiés, `source_not_reexecuted=true`, 336 gzip et 48 sources.
- Les preuves sont **internes à GitHub** malgré l'immutabilité des Releases ; il n'existe **aucun dépôt de preuve externe indépendant** à déduire de ce résultat.

## 3. Reconstruction indépendante du moteur natif

Le rapport COLD est produit par un auditeur Python 3.12 en lecture seule, **sans importer `Mind`, `World` ni le producteur natif**. Il a reconstruit :

| Indicateur de qualité | Preuve vérifiée |
|---|---:|
| Origines distinctes et préallouées | 48/48 |
| Écologies couvertes | 8/8, six racines chacune |
| Sources T1..T5 authentiques et payées | 48/48 |
| Parité de coûts cognitifs réellement payés à T6 | 48/48 |
| Shams T5 et continuations | neutres pour 48/48 origines |
| Origines et moteurs natifs gzip | 336/336 |
| `World.step` physiques reconstitués | **10 848** |
| Tours délibératifs F1J réellement financés | **50 690** |
| Branches de durée de vie différente à T60 | **0/48** |
| Racines où les deux bras survivent à T60 | **48/48** |

Aucun critère d'éligibilité ni coût n'a été modifié après naissance. Les shams ne sont jamais comptés comme réplications statistiques indépendantes. Un seul génotype `midpoint()` a été utilisé : **48 racines autonomes ne sont pas 48 génotypes**.

## 4. Verdicts M/A/B : seuils prospectifs non atteints

Les seuils sont ceux du **préenregistrement antérieur du 25 novembre**, pas des critères choisis après observation.

| Issue prospective | Seuil de succès avant exposition | Observation originale | Décision scientifique |
|---|---|---|---|
| **M, moteur T6** | ≥8 racines différentes dans ≥3 écologies | **1/48**, dans **1/8** écologies | `NO_REPRODUCIBLE_LOCAL_T6_OWN_MARGIN_MOTOR_EFFECT` |
| **A, survie T6..T60** | ≥8 gains dans ≥3 écologies, **zéro perte** | **0 gain, 0 perte**, sur 48 paires | `NO_REPRODUCIBLE_LOCAL_T60_OWN_MARGIN_SURVIVAL_ADVANTAGE` |
| **B, Pareto corporel secondaire** | ≥12 dominances strictes de la marge dans ≥3 écologies, zéro dominance inverse | **0 dominance marge, 1 dominance contrôle masqué** | `NO_REPRODUCIBLE_LOCAL_T60_OWN_MARGIN_BODY_PARETO_SUPPORT` |

**Verdict global : M négatif, A négatif, B négatif.** La parité de la facturation et la validité des shams sont satisfaites, mais **le fait de calculer, financer et relire une marge ne démontre pas un avantage adaptatif** dans cette cohorte.

## 5. Mécanisme observé : un seul effet moteur, N26

Sur les **48/48** expériences, la valeur `q` personnellement calculée à T5 est **strictement positive** (min ≈ 0,0803 ; médiane ≈ 0,3566 ; max = 1,0). Dans seulement **17/48** expériences, la clé du gagnant mémorisé est encore une alternative scorée à T6. Cet indicateur est descriptif et **ne change pas le dénominateur préenregistré**, qui reste 48.

L'unique action motrice différente concerne **N26**, graine `202611259826`, écologie littérale `n_water_diagonal_finite_food_safe` (eau diagonale finie, nourriture sûre). La mémoire personnelle conserve `q=0.9688204415037732` et la clé `boire`, effectivement proposée parmi les alternatives T6 :

- **Bras `margin`** : `q` réellement lu et appliqué au seul seuil `boire` ; `motor=(boire, null)`.
- **Bras `masked`** : la même valeur a été réellement mémorisée et lue, mais localement masquée à `0.0` avant le seuil ; `motor=(dormir, null)`.
- Les coûts cognitifs T6 sont **identiques et payés** (pour les deux bras : `cycles=8`, `memory_items=70`, `simulated_steps=63`, `replays=0`), et les shams sont neutres.
- **Survie T60** : les deux bras restent vivants, `Δticks=0`. À T60, les cinq différences `margin - masked`, par ordre `énergie, nourriture, eau, intégrité, vigilance`, sont environ **[-2.7698, -0.6200, 0, 0, -1.2080]**. La différence de l'eau `-1.42e-14` est du bruit d'arrondi. Le contrôle **masked** domine le corps de N26 selon le critère Pareto à tolérance numérique du froid ; la marge n'améliore aucun indicateur corporel ici.

Les **47 autres paires** ont la même action motrice T6 et des réserves terminales strictement identiques dans le rapport original. Cela **montre un effet causal local** de la marge sur une action libre, mais n'autorise aucune généralisation d'un avantage robuste, encore moins d'une valeur adaptative démontrée. Il n'est pas acceptable de sélectionner uniquement les 17 clés réutilisées ni le seul N26 pour recalculer rétroactivement les seuils prospectifs.

## 6. Conclusion, intégrité historique et prochaine question

Cette étude tranche une question plus étroite que « la mémoire améliore-t-elle l'individu ? ». Elle établit que **la marge d'une expérience personnelle acquise et effectivement facturée peut parfois influencer la commande motrice suivante**, sans contraindre l'action ; **dans F1N, cet effet n'est ni reproductible au seuil fixé, ni associé à un avantage de survie**, et le seul cas avec changement moteur présente un **coût corporel net** en faveur du contrôle masqué.

**Ne pas réexposer, réexécuter, remplacer ou « compléter » N01..N48.** Le commit `38d1c94...` et les Releases RAW/COLD restent de référence, figés. Tout diagnostic plus fin sur les mécanismes, y compris une hypothèse sur le seuil, doit être nommé **POST-HOC**, exploiter uniquement les témoignages archivés et faire l'objet d'une source préenregistrée **distincte** si une nouvelle cohorte était un jour conçue.

Les résultats originaux F1L et F1M demeurent inchangés et négatifs. La décision Stage2 reste **`NOT_ISSUED/HOLD_NO_VERDICT`**, sans promotion. Aucun essai supplémentaire n'a été lancé pour produire cette note.

**Chaîne de confiance minimale :** [run premier et unique](https://github.com/josselin-orta-lab/individual-zero/actions/runs/45824249204) → [ref consommée F1N](https://github.com/josselin-orta-lab/individual-zero/tree/i3-stage8-f1n-heldout-consumed-once) → [Release RAW immuable](https://github.com/josselin-orta-lab/individual-zero/releases/tag/i3-stage8f1n-t60-raw-heldout-once) → [Release COLD immuable](https://github.com/josselin-orta-lab/individual-zero/releases/tag/i3-stage8f1n-t60-cold-heldout-once).
