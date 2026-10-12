# EXP Stage12 #133 : sommeil / consolidation, préenregistrement (2026-10-12)

**État initial : hypothèses gelées AVANT toute nouvelle exécution.** Campagne exploratoire uniquement ; Stage 12 non accepté, M-11/Stage12 non certifié. Source de référence `main` : `335956f1fadcbae4259e73d986125b6938e00bf4`.

Références : `docs/architecture/reference/en/mvp-specification-v1.3.1.md` (hérite §15 du MVP v1.2.1) et `docs/architecture/reference/fr/architecture-v2.md` §43. Aucune modification normative n'est autorisée ; aucune action ni connaissance Oracle n'est injectée dans I0.

## Constat historique motivant l'étude (pas une preuve prospective)

Les archives de PR #131 montrent après réveil (world-step 9) une fatigue cognitive 0, une pression de consolidation 1.0 et une pression de sommeil 0.5. La formule P-40 calcule une motivation par F_cog, p_cons et contexte nocturne. Après un réveil par durée maximale, la pression de consolidation reste élevée tant que les épisodes ne sont pas consolidés. La fixture Stage10 intégrée utilisée dans #131 n'a pas les politiques optionnelles `selection_policy` et `semantic_policy` : aucune passe h ne peut être lancée. Le cap 2 → 18 réduit les réentrées, pas le nombre total d'actions dormir (47/50).

## Facteurs expérimentaux gelés

Plan fixe **2 × 2**, quatre nouvelles vies mortelles indépendantes par version Python, **50 transitions physiques maximales chacune**. Source physique/Stage11 identique : fixture de référence, aucune action imposée à l'individu.

1. `consolidation_enabled` : configuration Stage10 standard contre `sixpass_enabled` (BatchSelectionPolicy, SemanticPassPolicy et vrais coûts UC P-42 d'après `tests/test_stage10_live_sixpass_runtime.py`).
2. `weight` : `reference` (w_C=0.5) contre `zero` (w_C=0.0). Le poids nul désactive seulement la contribution motivationnelle de p_cons à P-40 ; il **ne doit pas** désactiver la sélection/consolidation sous sixpass.

Les quatre combinaisons ont sommeil normalement autorisé, même max_consecutive_sleep_steps=2, même fatigue_gain, valeur intrinsèque, cycle plafond, demandes UC et corps. La condition `sixpass_enabled` active les mêmes mécanismes de mémoire réels que la suite d'intégration, pas une fausse version h ou une injection manuelle de fatigue.

## Hypothèses / critères de réfutation avant mesures

H133-A : sans sixpass, les événements `stage10_consolidation_version_activated` sont nuls même si les épisodes non consolidés et p_cons augmentent. Ceci représente un **contrôle négatif de configuration**, pas une preuve d'échec algorithmique.

H133-B : avec sixpass et épisodes éligibles, une transaction doit enregistrer des passes réelles et éventuellement activer h si les six validations aboutissent. Si `selection_policy` active mais aucune passe malgré épisodes accessibles et budgets suffisants, enquêter sur la sélection ; si pas d'épisodes éligibles ou budgets réellement insuffisants, **INCONCLUSIVE**, pas un succès inventé. Une version h activée sans six checkpoints est FAIL sécurité.

H133-C : poids nul doit abaisser la composante p_cons de la motivation dormante, mais n'oblige pas I0 à rester éveillé. Comparer les **actions effectivement appliquées**, et la première décision `dormir` si elle existe, pas seulement des scores calculés.

H133-D : une réduction de p_cons après consolidation véritable peut diminuer la pression motivante, sans garantie de sortir du sommeil. Comparer la série de `stage10_sleep_pressure_frozen` aux événements de commit et aux épisodes vus, sans inférer que la simple répétition dormir était une consolidation.

H133-E : tout essai doit posséder une seule naissance, WAL fsync, journal avec chaîne valide, décès non rejoué, 50 pas fermés ou arrêt explicite, et aucune mutation après arrêt. Les interruptions et vies incomplètes restent au dénominateur.

**Verdicts** : `SUPPORTED`, `NOT_SUPPORTED`, `INCONCLUSIVE`. Décrire toutes les cellules, effets par vie et cas manquants, sans p-valeur sur des pas corrélés. Python 3.11/3.12 sont des répliques techniques, pas de nouvelles graines expérimentales. Ces quatre configurations déterministes ne suffisent pas à une confirmation scientifique ou à valider l'opérateur.

La campagne produit preuves brutes, audit indépendant et bilan après résultats dans une révision ultérieure distincte. Tout changement de configuration, seuil ou code survenu après les résultats impose une autre expérience gelée et non une édition rétroactive de ce protocole.
