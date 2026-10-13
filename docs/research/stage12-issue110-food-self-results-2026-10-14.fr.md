# Individual Zero #110 : résultats expérimentaux de l'attribution subjective `self` vécue

**Date de rédaction : 14 octobre 2026.** Expérience prospectivement préenregistrée dans `stage12-issue110-food-self-agency-prereg-2026-10-14.fr.md`, commit `641d9844`, **avant** le runner. Branche scientifique PR #152 issue de la PR technique #147, non fusionnée. Spécification candidate GA-01..GA-07 PR #148 non fusionnée. Aucun GO opérateur ou scientifique final.

## 1. Campagnes, provenance et incident de sommeil

Première exécution [38475956220](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38475956220), SHA `4b021a04` : échec **de l'audit final** de la vie `physical_food_corpus/h_eff=3` malgré une commande `manger` physiquement appliquée, un critère `success`, un jugement `self` et l'enregistrement d'une jointure UC. Cause : le pas 6 est une continuation de sommeil sans cognition ; le premier diagnostic suivant, pas 7, ne doit **pas** consommer le couple produit au pas 5, mais l'ancienne intégration l'expirait silencieusement. L'auditeur refusait donc légitimement l'absence de reçu de péremption.

Correction logicielle sur PR #147 et #152 : expiration une fois, avec reçu technique `stage12_attribution_sample_unavailable`, `reason=no_waking_diagnostic_at_due_step`, `due_world_step=6`, émis au premier prochain cycle métacognitif éveillé et facturé. **Aucune cognition créée durant le sommeil, aucun diagnostic rétroactif**, fenêtres et seuils inchangés. L'auditeur externe distingue une expiration dûment liée au sommeil d'une simple absence de diagnostic. Un test de régression construit un journal techniquement rechaîné après suppression du reçu et exige son refus sémantique. Un second test rechaîné supprime la capture réduite de sommeil et exige son refus.

Première campagne corrigée avec régression physique et CI **SUCCESS** sous Python 3.11 et 3.12 : [38476358433](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38476358433), SHA exact `dc65ccf9b26ac76b5d17ef68e6404b74cd895042`. Un renforcement supplémentaire de l'audit pour exiger la capture réduite de sommeil est appliqué ensuite et doit faire l'objet d'une CI exacte distincte avant toute revendication de conformité de la révision finale.

## 2. Résultats mesurés sur la campagne corrigée `dc65ccf9`

| Mesure, par interpréteur | Python 3.11 | Python 3.12 |
| --- | ---: | ---: |
| Vies neuves, auditées indépendamment | 4/4 | 4/4 |
| Pas physiques réellement appliqués | 200/200 | 200/200 |
| Propositions de plans d'objectif | 20 | 20 |
| Critères préenregistrés | 3 | 3 |
| Non-gains corporels vérifiés | 2 | 2 |
| Gains corporels vérifiés | 1 | 1 |
| Préengagements d'agence | 3 | 3 |
| Jugements cognitifs `unknown` | 2 | 2 |
| Jugements cognitifs `self` | **1** | **1** |
| Jugements cognitifs `world` | 0 | 0 |
| UC de jugement facturées | 3 | 3 |
| Couples `(success,self)` admis | **1** | **1** |
| UC de jointure facturées | 1 | 1 |
| Couples réellement appliqués au détecteur | **0** | **0** |
| Couples expirés pour sommeil | 1 | 1 |
| Diagnostics de biais positifs ou négatifs disponibles | 0 | 0 |
| Refus UC sur ces opérations | 0 | 0 |

Les quatre journaux canoniques ont été comparés **octet par octet** entre les archives des deux versions Python et leurs SHA-256 sont identiques. Les deux versions sont un contrôle de reproductibilité technique, **pas huit individus scientifiquement indépendants**.

### Résultats par configuration (50 pas physiques chacune)

| Équipement | Horizon d'évaluation | Propositions de plan de but | Actions significatives |
| --- | ---: | ---: | --- |
| Référence exacte peu couverte | 2 | 0 | exploration, sommeil |
| Référence exacte peu couverte | 3 | 0 | exploration, sommeil |
| Corpus pré-natal d'actions physiques alimentaires | 2 | 17 | exploration, sommeil, aucune ingestion |
| Même corpus physique | 3 | 3 | **1 collecte et 1 ingestion réelles**, librement choisies |

Le corpus de transition comporte `north`, `south`, `collecter berry_a`, `manger berry_a`, enregistrés avec `EquipmentCorpusRecorder` sur un **WorldBody d'entraînement distinct et antérieur à la naissance** ; ce n'est pas un apprentissage autonome pendant la vie d'I0. Le contexte `food=35`, `water=70`, quantité de baies=2 et gain énergétique alimentaire sont des paramètres physiques préenregistrés et versionnés, pas des résultats cognitifs injectés.

### Provenance de la vie ayant produit `self`

Au pas 2 : Action Control admet une étape de déplacement associée au but `eat`, avec intention de progrès alimentaire préenregistrée.

Au pas 3 : aucun gain de `food` lié au déplacement, `criterion_outcome=failure` et `subjective_agency=unknown`. Une collecte de baie est ensuite exécutée dans un plan physiquement enregistré.

Au pas 4 : absence de gain corporel encore vérifiée, `unknown` toujours légitime. I0 choisit et applique `manger berry_a` ; Action Control préenregistre, **avant WorldBody.apply**, la copie efférente du geste, la quantité d'inventaire accessible et le mécanisme `ingested_from_inventory`.

Au pas 5 : capture corporelle et perceptive suivante. `body.food` a augmenté, d'où `success` selon le critère préenregistré **sans contribution du jugement d'agence**. La baisse d'une unité de baie dans l'inventaire observé, sans déplacement spatial, fonde séparément le **jugement subjectif `self`** selon la politique cognitive versionnée. La journalisation et le coût UC permettent la jointure indépendante des deux origines et l'admission de **un** couple `(success,self)`.

Au pas 6 : `stage10_sleep_entered`, capture réduite `stage10_reduced_capture`, commande réelle `dormir`, aucun diagnostic cognitif. Le couple du pas 5 **ne peut pas être appliqué** hors de sa fenêtre ; au pas 7 il est expiré avec un reçu indépendant vérifiable. La sortie du détecteur demeure `None`.

## 3. Détails reproductibles

GitHub Actions : [run 38476358433](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38476358433). Archives techniques : `issue110-food-self-science-py3.11` et `issue110-food-self-science-py3.12`, chacune avec quatre WAL, journaux JSONL, rapports individuels et synthèse `summary.json`.

Empreintes SHA-256 des quatre journaux canoniques (identiques sur les deux versions) :

- Corpus alimentaire, horizon 3 : `a8287b126886bc07454c5ff950460e5d3c161669a32e7b9e1f849d498d62ad12`
- Corpus alimentaire, horizon 2 : `0bac646a036c4d820199216ecde0a54d455418395639b661beec493c5db59993`
- Équipement référence, horizon 3 : `09559a5400e864602adf3ddb6e0e9f13837f818032d5c9c995f9f217491f768f`
- Équipement référence, horizon 2 : `09559a5400e864602adf3ddb6e0e9f13837f818032d5c9c995f9f217491f768f`

Les audits `audit_export_bytes`, `audit_stage12_goal_progress`, `audit_stage12_first_person_agency`, `audit_stage12_attribution_pairs` et `audit_stage12_diagnostics` ont réussi sur ces vies, puis les tests de falsification ont été ajoutés à la CI suivante. Les rapports sont des vérifications de provenance et de cohérence sémantique, **pas** une vérité physique indépendante déduite de la seule chaîne SHA-256.

## 4. Verdict et blocages persistants

**Niveau logiciel/expérimental exploratoire : première observation positive d'un jugement `self` réellement produit dans une vie autonome sur un critère d'objectif indépendamment vérifié.** Le résultat existe avec une provenance et un UC authentiques. Il ne faut PAS dire que le détecteur de biais a diagnostiqué une préférence auto-complaisante, car le couple n'a pas pu être appliqué au diagnostic avant la continuation du sommeil.

**Non démontré :** une politique générale d'agence `world` perceptivement légitime ; plusieurs couples uniques succès/échec admissibles dans les fenêtres et les seuils du détecteur ; validité scientifique générale ; acquisition autonome d'Equipment ; audit M-11 `os._exit` sur la nouvelle image d'état ; réception opérateur du Stage 12. Le Stage 9 conserve son NO-GO.

### Évolution minimale recommandée pour étudier `world` (non normative)

Les critères actuels mesurent un **gain corporel immédiat** et le vocabulaire de Perception ne donne pas de preuve externe à la première personne qui relie de façon unique un obstacle à un non-gain d'eau ou de nourriture. Inférer `world` d'un échec du gain serait circulaire. La prochaine étude doit préenregistrer une **sous-étape spatiale de but** (par exemple réduction de distance perçue jusqu'à la source identifiée) et enregistrer séparément un indice de **contrainte spatiale extérieure** perçue avant/après la commande, avec admission de commande, disponibilité d'action et provenance propre. Une absence de déplacement ne suffit pas : la perception doit attester l'obstacle pertinent et le mécanisme de responsabilité subjective, indépendamment du comparateur de succès. Aucun jugement `world` n'est donc fabriqué dans cette campagne.

Le dossier doit rester attaché à l'issue #110 ; norme MVP v1.3.2 et PR #147/#152 en revue, aucun merge ni clôture avant preuve opérateur.
