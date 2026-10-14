# Issue #110 — compte rendu scientifique intermédiaire vérifié, 13 octobre 2026

**Statut : protocole expérimental en cours ; aucune réussite du détecteur d'attribution démontrée.**
**Ce document consigne exclusivement les résultats observés, pas des sorties anticipées.**

## 1. Campagne de base, 600 pas, PR #147

Source exacte : `f0f4b72ab9cfacff8843dd26d75ef5734cf69c43`. GitHub Actions [38468100393](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38468100393).

| Mesure canonique vérifiée | Python 3.11 | Python 3.12 |
| --- | ---: | ---: |
| Tests préalables | PASS | PASS |
| Pas physiques réellement appliqués | 600 | 600 |
| Occurrences du journal causal | 48 650 | 48 650 |
| Audit WAL/export/packet | PASS | PASS |
| Engagements d'attribution GA produits | 0 | 0 |
| Jugements `self` | 0 | 0 |
| Jugements `world` | 0 | 0 |
| Jugements `unknown` | 0 | 0 |
| Couples résultat/attribution admis | 0 | 0 |
| Couples appliqués | 0 | 0 |
| Diagnostics `attribution_bias=None` | 600 | 600 |

Empreinte de chaîne vérifiée dans les deux exécutions : `3e8216224ba1b698bcd03fcb02014a6ba8b253e63e94a3658019e5ef6306e419`. Les deux exécutions à graine identique montrent une cohérence inter-version de cette trajectoire ; **elles ne sont pas des réplications statistiques indépendantes**.

**Verdict H1/H2 : inconclusif sur la capacité positive**. L'agent n'a pas produit un seul engagement de jugement, donc ce banc ne sollicite pas la chaîne end-to-end. Le fait que le détecteur reste indisponible est le bon comportement épistémique, mais pas une validation positive.

L'inspection du runtime montre que le préenregistrement GA-01..GA-04 exige simultanément : diagnostic UC déjà accepté au pas, but actif et mesure principale compatibles, `goal_ref` de l'option identique au but actif, motivation de type `active_goal`, valeur initiale corporelle accessible. La campagne n'établit pas lequel de ces filtres empêche l'émission. Ce point devra être mesuré **sans changer les critères ni forcer le choix moteur**. Aucun des 600 pas ne doit être maquillé en engagement a posteriori.

## 2. Contrôle des premiers runs contrastés, PR #150

Préenregistrement préalable : `docs/research/stage12-issue110-ga-contrasted-prereg-2026-10-13.fr.md`, commit `54dbd20c`. Protocole : 12 vies × 50 pas maximum, trois environnements, deux eaux initiales, deux profils de sommeil, analyse indépendante des vrais WAL/exports. Python 3.11 et 3.12 comme test de reproductibilité logicielle, pas doublement artificiel des vies.

Les premiers runs GitHub [38468101453](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38468101453) échouent **après leurs suites de tests** lors de la synthèse. Cause reproductible : `KeyError: 'verified_strict_gains'`. L'instance dataclass possède bien `verified_strict_gains`, mais `Stage12GoalProgressAudit.as_dict()` exporte contractuellement `verified_one_step_resource_gains` (et `verified_one_step_no_gains`). Il s'agit d'une incompatibilité de schéma du script de reporting, non d'une preuve de défaillance cognitive. Les archives des vies échouées sont conservées sur GitHub Actions.

Correctif de reporting : faire dépendre la synthèse des **champs exportés et versionnés**, et non des noms internes de dataclass ; compter les vies rejetées, les inconnues, les coûts UC, les jugements et les diagnostics. La synthèse doit refuser un schéma inattendu et ne jamais substituer zéro à une preuve manquante. Un test indépendant des schémas protège cette règle. Le protocole expérimental, les seuils et les configurations physiques restent figés.

**Verdict scientifique actuel : INCONCLUSIF**. Ni l'échec de synthèse ni 600 pas sans attribution ne justifient une réception Stage12. Attendre les résultats de la campagne contrastée corrigée, effectuer ensuite l'analyse des engagements et des couples sans relabeliser les expériences négatives.

## 3. Limitations et conservation

- La politique cognitive actuellement mise en œuvre dispose d'un indice `self` par ingestion volontaire et décrément d'inventaire perçu, mais pas d'un producteur `world` démontré pour les résultats corporels. L'échec ne vaut jamais `world`.
- La conséquence physique attestée par la trace interne n'est pas une vérité causale externe indépendante.
- Stage 9 conserve son NO-GO, M-11 et sommeil exigent leurs validations distinctes.
- Aucune mutation des spécifications historiques, aucun changement de seuil et aucune nouvelle commande forcée.
- L'issue #110, les PR #147/#148/#149/#150 et la réception du Stage 12 restent ouvertes.

**Règle de révision :** compléter ce rapport seulement avec les nouveaux SHA, exécutions et artefacts réellement obtenus ; conserver les échecs originaux sans les effacer du bilan.
