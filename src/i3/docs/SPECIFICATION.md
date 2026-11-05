# I3 — Spécification v1 (référence exécutable)

**Décision :** [ADR-0014](../../../docs/decisions/ADR-0014-i3-lignee-enjeu-de-soi.md), accepté le 5 novembre 2026. La version illustrée et commentée de cette spécification vit dans le document partagé « I3 — ADR-0014 et spécification » ; ce fichier fixe ce que le code doit respecter et consigne les écarts d'implémentation.

## Objet

Un individu mortel dont l'enjeu est sa propre organisation, dans une lignée où seule la persistance individuelle sélectionne des paramètres innés génériques. Aucune expérience n'est transmise.

## Ce que le code doit garantir

| Exigence | Où |
| --- | --- |
| Monde séparé ; l'individu ne lit que `World.capture()` (corps, inventaire, case courante, 4 voisines) | `modules/world.py` |
| Physique v4 (nourriture −0,2, eau −0,4 par pas ; morts `zero_food`, `zero_water`, `zero_integrity`) | `modules/body.py` |
| Cinquième canal **vigilance**, usé par le travail cognitif, restauré par le sommeil | `modules/body.py` |
| **Monnaie vitale** : cycles, pas simulés, souvenirs et rejeux coûtent énergie et vigilance | `modules/body.py` |
| **Capacités vulnérables** : énergie → cycles ; vigilance → horizon de simulation et oubli ; intégrité → bruit perceptif | `modules/body.py`, `modules/mind.py` |
| Génome fermé `i3-genome-v1`, bornes déclarées, aucun champ indexé par le monde | `modules/genome.py` |
| Jetons renommés par ordre de première perception ; positions relatives à la naissance | `modules/mind.py` |
| Détresse innée D(h) = Σ w_c · max(0, (θ_c − h_c)/θ_c)^p_c ; récompense r = −D ; aucun surplus pénalisé | `modules/mind.py` |
| Choix : scores continus, accumulateurs à identité sémantique stable, aucune option privilégiée, jamais d'abstention par défaut | `modules/mind.py` |
| Rejeu exact : (code, génome, monde, graine de vie) → même vie | `runtime/life.py` |
| Mort irréversible : aucune action après décès | `modules/world.py` |

## Écarts d'implémentation v1 (décidés pendant P1, sur mondes de développement uniquement)

Le développement s'est fait sur `lab/dev_worlds.py`, jamais sur les mondes du test G2. Cinq défauts d'architecture y sont apparus ; chacun a reçu une correction de principe, sans règle propre à une action ou à un monde.

1. **Auto-projection innée.** La valeur d'amorçage n'est pas seulement apprise : l'individu projette sa propre dérive passive sur 255 pas (blocs 1, 2, 4… 128) pour les canaux qui dépendent du monde (nourriture, eau, intégrité). Énergie et vigilance restent constantes dans la projection, car le sommeil est toujours disponible au corps. La valeur TD apprend un résidu au-dessus de cette projection. Sans elle, l'individu ne voyait ni la mort lointaine ni l'urgence de chercher.
2. **Curiosité pertinente pour le besoin.** Le bonus d'exploration lié au besoin ne s'applique qu'aux options qui pourraient y répondre (boire pour la soif, manger pour la faim, explorer pour les deux) ; le reste ne reçoit qu'une curiosité générale κ₀. L'urgence se calcule sur le corps projeté, pondérée par 1 − (croyance qu'une source connue fonctionne).
3. **Valeur informative de l'exploration.** Explorer une frontière vaut le nombre de cases révélées × le taux de cases à ressource que l'individu a lui-même observé (Laplace).
4. **Prudence proportionnée à la vulnérabilité.** La pénalité d'incertitude d'un repas inconnu croît avec la détresse d'intégrité, au lieu d'être constante.
5. **Croyance de présence par lieu.** La carte retient l'historique des observations de chaque case ; un trajet vers une source est évalué par son espérance (source présente ou trajet pour rien). Un trajet est simulé par blocs de pas dont la taille est bornée par l'horizon, lui-même borné par la vigilance.

Autres écarts : le gène `v_s` est absorbé par `w.vigilance` (même rôle) ; le tempérament agit par l'exploration (β_u, κ₀), la sensibilité à la menace (λ_r) et la protection du but (inertie) — `reward_sensitivity` et `affiliation` n'ont pas d'effet en v1 ; le réflexe inné se limite à un veto de repas nocif quand l'intégrité est ≤ 10 (aucune action forcée) ; l'échec d'action lié à l'intégrité basse n'est pas encore implémenté ; les modules sont des fichiers de `modules/` plutôt que des dossiers.

## Hors v1

Générateur de familles de mondes (P2), lignée et registre (P3), étude 2 × 2 et ablations (P4), allostasie (révision des seuils θ_c en cours de vie).
