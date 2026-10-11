# Stage 11 : préconsultation facturée dans Planning Phase 1

**Date :** 11 octobre 2026 (Europe/Paris). **Statut :** diagnostic logiciel public, non held-out. **Verdict scientifique : aucun.**

## Sources et antériorité du contrôle

- La référence normative reste `docs/architecture/reference/en/mvp-specification-v1.2.1.md`, en particulier la table des phases DC-11, §9.4, §16.3, INV-08, et les règles d'état physique et de snapshot.
- [Protocole de facturation v2 déclaré avant les modifications](stage11-geographic-charge-before-consult-protocol.en.md). Sa [campagne v2, CI #38114261848](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38114261848), a **réussi 775 tests**, mais a conduit à une réserve de conformité : elle facturait correctement la consultation mais l'exécutait encore dans le hook de modulation en Phase 0.
- [Révision architecturale v3 déclarée avant nouveau code/test](stage11-phase1-charged-preflight-protocol.en.md) ; [première exécution négative conservée](stage11-phase1-first-pass-test-correction.en.md). Le commit `65162d884ff07e3e6f01e58a3f06bf98bda42359` a [échoué 1 test sur 776](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38114574639) à cause d'une assertion de test trop large : elle interdisait toute direction nord, alors que seule la **case (2,1)** était connue comme létale. Le code de production n'a pas été ajusté pour satisfaire cette assertion ; seule la vérification des destinations proposées et des positions réellement visitées a été corrigée.
- **Commit validé par la campagne finale :** `6a231692aed730ee56d78c5091b90c99996d8997`.
- [GitHub Actions #38114696522](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38114696522) : **776/776 tests unitaires passés sur Python 3.12**, bootstrap smoke réussi. La suite Golden longue et l'environnement normatif Python 3.11 ne sont pas validés par cette exécution.

## Séparation des propriétaires et des phases

| Phase | Responsabilité observée dans I0-vNext |
| --- | --- |
| 0 | Le scheduler fige le cycle et Global Modulation fige son profil ; **aucun** appel de préfiltrage géographique à Action Control, aucune UC Planning dépensée à ce stade |
| 1, Exploration | Le propriétaire Exploration consigne l'observation physique de Perception et l'état causal qu'il est autorisé à lire, sans recevoir une décision de Planning issue de cette phase |
| 1, Planning | À partir des quatre cellules adjacentes et du registre de visites **figés avant la phase 1**, Planning demande et obtient la charge `geographic_admissibility_preflight = 1 UC` avant d'appeler `ActionControl.verifier_admissibilite`. Les directions uniquement `INADMISSIBLE` sont retirées, `INDETERMINATE` reste possible et la capacité maximale des cibles est appliquée **après** le filtre. Puis les éventuelles options demandent leur propre `planning_build` de 2 UC |
| 3, Competition | Competition exerce le service autorisé vers Exploration pour figer uniquement les cibles correspondant à des propositions Planning financées et non dégradées ; la motivation intrinsèque peut ensuite être évaluée |
| 4, Action Control | Le veto final garde son autorité, indépendamment de la consultation facultative en Phase 1 |

Le nouveau paramètre `candidate_limit=4` dans l'API de lecture de la frontière n'élargit pas `max_targets_per_cycle` : il empêche qu'une première direction interdite masque des alternatives lorsque la capacité finale est de **1**. Il lit exclusivement les informations locales issues de Perception et les visites déjà enregistrées. Aucun fait de danger caché n'est communiqué à Exploration.

Le journal `stage11_geographic_preflight_consulted` atteste chaque consultation après une `compute_charge` Planning acceptée, dans la phase 1 du même cycle. Le contrôle automatique rejette toute consultation sans charge préalable, avec un mauvais numéro de phase, ou une discordance des nombres de charges et de consultations.

Les événements `stage11_geographic_budget_deferred` restent au maximum un par cycle et conservent les charges refusées sans inventer de résultat « sûr », « interdit » ou « pas de nouveauté ». La version du budget est explicitement marquée `phase1-charged-geographic-preflight-v3`.

## Budget très contraint : trois pas physiques publics

| Configuration | Préconsultations acceptées | Préconsultations refusées | Constructions refusées | Observations Exploration refusées | Actions géographiques réellement appliquées |
| --- | ---: | ---: | ---: | ---: | ---: |
| Planning 0 UC | 0 | **14** | 0 | 0 | **0** |
| Planning 1 UC | **14** | 0 | **14** | 0 | **0** |
| Planning 3 UC | **3** | 0 | 0 | 0 | **3** |
| Exploration 0 UC | **0** | 0 | 0 | **15** | **0** |

Ce dernier cas est important : contrairement au correctif v2 qui facturait avant que l'échec d'Exploration soit connu, le placement normatif en Phase 1 évite maintenant **14 préconsultations inutiles** dans le scénario Exploration 0 UC. L'observation physique reste valide indépendamment du budget cognitif. Toutes les sorties ont **zéro erreur d'ordre UC/phase**, les refus conservent zéro cible offerte, et toutes les variantes se réexécutent exactement.

**Empreintes SHA-256**, diagnostic `stage11-public-strict-geographic-budget-dev-v3` :

| Variante | Résultat canonique | Tête de journal |
| --- | --- | --- |
| Planning 0 UC | `3af0bf235c07ad9b16ef297da8a8ae21c3e64c5c22f0e28155279296ebaacd1f` | `c587491feaf69ac6e80e8d54264b23b612d2aa39f38d7fefd238eb79825f95d8` |
| Planning 1 UC | `80170f47ca5ff047969bc839ae8702442b03edfded25ce2e9f8609febe67dae4` | `1515bb4960b4e0cc72aa0ee43672dfc9c684c3779e1cf27d52838032deb0ff26` |
| Planning 3 UC | `339d99ff6ed00f7f8e8961882a8ecbb742ec068409c6358ec6535d9294718ec4` | `8c66f38602cc74d5187b495571c770259d132b1f525f1366341f7ab83be88e30` |
| Exploration 0 UC | `bfe38701ab32128ad4c32eac604e2392836eaa7462c9ab191e6e0baac3c9fb15` | `519c57f7aa694c1d8fdd4db988234cfc48b561f1e67a6d2288bf7571eb4ad752` |

## Contrôles des six cartes physiques

Les trois conditions publiques (aucun préfiltre, v3 systématique, v4 à la demande) restent reproductibles sur six pas. Pour **v3 systématique → v4 à la demande**, les UC acceptées tous modules confondus restent :

| Monde | v3 | v4 | Variation v4 moins v3 | Sites perçus avec v4 |
| --- | ---: | ---: | ---: | ---: |
| Voisins tous bloqués | 251 | 222 | −29 | 1 |
| Obstacle au nord | 215 | 195 | −20 | 3 |
| Couloir est | 91 | 91 | 0 | 6 |
| Créature nord | 107 | 102 | −5 | 5 |
| Létal connu au nord | 215 | 215 | 0 | 3 |
| Unique sortie nord létale | 251 | 251 | 0 | 1 |

Les cibles reçues par Exploration en phase 3 correspondent désormais uniquement aux options filtrées et financées par Planning en phase 1. Les déplacements appliqués et les sites physiquement perçus restent identiques au comparateur avant déplacement des phases dans ces petits scénarios. La première option du cas public unitaire à capacité 1 est orientée **est**, et aucune proposition ni visite n'a pour destination létale `(2,1)`. Une orientation ultérieure nord, depuis une autre origine, reste possible et ne doit pas être censurée artificiellement.

**Empreintes des six diagnostics `stage11-public-geographic-demand-preflight-dev-v3` :**

| Monde | SHA-256 de résultat |
| --- | --- |
| Voisins bloqués | `2039fd20bd9707a19ab8bfc5defa752ef4d03cd52ce489167a736a3e3f39d171` |
| Obstacle nord | `18aaa060ead37a4e9346333ced88b29ce3d27b9ff3f54e0fa439d34c88dc01d9` |
| Couloir est | `b151678cf58c51512746487360fbb51e31bb6a42278f45fc5475873706d5c9b9` |
| Créature nord | `3b08f70f16a19a02ceb89245717f406eec7446d196a74aba3e561ebaf44521e7` |
| Létal connu | `b64cc7fc4675bea0ca7af7c93a2a5aef069308ab19c81d7841dd3b32617faa0b` |
| Unique sortie létale | `2731a45294b9ba30cc41cac6e30160cae84fdb7df54eedba06ca01813fcdb4d0` |

Ce contrôle conserve **zéro plan géographique refusé** devant la zone connue létale grâce au préfiltrage, et ne s'attribue aucun avantage scientifique provenant de ces données publiques.

## Limites persistantes

- Le déplacement des responsabilités entre phases est une amélioration de conformité de ce mécanisme ; cela n'est **pas** une preuve de conformité de toutes les composantes du Stage 11.
- Les coûts UC sont abstraits et versionnés, pas du temps CPU ni de l'énergie. La v4 reste parfois plus coûteuse que la voie sans aucune préconsultation lorsqu'aucun danger connu ne justifie ce contrôle.
- Les seuls dangers ici exclus sont ceux **connus** de l'Action Control canonique ou directement visibles par Perception. Aucun mécanisme n'établit qu'un chemin inconnu est physiquement sans risque.
- Le test de restauration de sécurité DC-05 demeure un test unitaire synthétique, non une expérience scientifique ; la propriétaire unique est toujours Causal Model.
- Les trajectoires longues, les impasses après épuisement de toutes les cellules nouvelles, les budgets protégés proches de l'épuisement, la matrice Python 3.11 et les Golden complets ne sont pas encore validés dans cette campagne.

**Stage 11 EN COURS. Stage 9 SCIENTIFIC VALIDATION PENDING / NO-GO. PR en brouillon et non fusionnée.**
