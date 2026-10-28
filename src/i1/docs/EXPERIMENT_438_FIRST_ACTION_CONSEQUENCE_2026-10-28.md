# I1 / #438: consequences du premier embranchement moteur Q-Stage8

**Date:** 2026-10-28. **Base de reprise:** `main` `de929a8b0c7424d95052ce9b9dd28d33b5b38705` (merge #592). **Nature:** instrumentation supplementaire **en lecture seule** d'un temoin preexistant, non nouvelle cohorte, non GO adaptatif.

## Ce qui est deja connu (ne pas appeler cela une prediction nouvelle)

Le protocole initial de #592 (`src/i1/docs/EXPERIMENT_438_STAGE8_READ_2026-10-28.md`) a decouvert, sur un meme scenario deterministe `dry-valley` v4 et deux vraies naissances M11, le **premier** changement de commande physique au pas 12: canonique `attendre` contre bras ou le Q lu par Stage8 est masque `dormir`. Meme corps, inventaire, position, image TD, GoalManager, registre Competition et P-40 geles avant le premier embranchement. Les deux jobs Python ont produit la meme trace, **pas deux replicats independants**. L3 local de la disponibilite de Q en Stage8 ne prouve aucune utilite.

La selection de ce cas de sommeil s'est faite apres lecture des resultats. Il est donc **exploratoire** pour l'utilite et ne doit pas etre presente comme une hypothese adaptative preenregistree avant la premiere vie. Le present document fixe uniquement les variables descriptives et controles **avant** une nouvelle lecture instrumentee de ce scenario.

## Question et hypothese

Dans ce seul premier embranchement a contexte pre-action egal, quelles sont les **consequences physiques immediates** de `attendre` et `dormir`, et laquelle rapproche, **sur un pas seulement**, les variables corporelles des consignes homeostatiques effectivement possedees a la naissance par I1 ?

- H0 descriptive: le bras canonique ne presente pas de meilleur resultat sur la distance homeostatique ponderee au pas de divergence.
- H1 descriptive: le bras canonique presente une distance homeostatique ponderee strictement inferieure, **sur le seul pas considere**.
- L'utilite *durable*, l'efficacite instrumentale `collecter -> manger`, la valeur des consolidations du sommeil, la mortalite a long terme et la generalisation sont **hors de portee** de ce temoin unique.

## Mesures prereglees avant relecture

A partir des etats **reellement commits M11**, sans agir sur le monde ni sur les proprietaires:

1. `B_before` identique au pas de premiere divergence et `B_after` authentifie de chaque bras, avec `energy`, `food`, `water`, `integrity`. Mesurer `B_after-B_before`, et `B_after(canonique)-B_after(masque)` composante par composante.
2. Reprendre **les poids et consignes ValueAndNeeds effectivement nes**, et calculer pour chaque corps `D(B)=sum(w_i*abs(B_i-setpoint_i))`. La **variation proxy d'homeostasie** est `D(B_before)-D(B_after)`, et l'ecart entre bras est `D(B_after masque)-D(B_after canonique)`. Positif signifie seulement *plus pres des consignes* pour le canonique, a ce pas. Tolerance de comparaison `1e-12`. **Ne pas confondre ce proxy operateur avec une recompense TD reellement recue ni avec la satisfaction d'un objectif personnel de long terme.**
3. Enregistrer fatigue, mode de sommeil, options payees et rapports `stage8_option_evaluation` / `competition_cycle` au premier pas divergent, les vraies admissions `command_admitted` et les decharges `compute_charge`. N'utiliser **aucun** classement simule ou options fabriquees.
4. Confirmer l'egalite avant divergence des canaux corporels, TD, Competition, GoalManager, P-40, fatigue et mode de sommeil, de la perception initiale et de l'identite physique du monde, ainsi que l'egalite du journal de debits UC jusqu'au pas precedant la premiere lecture Q masquee.
5. Verifier les etapes physiques precedentes comme temoins negatifs: tant que la commande appliquee reste identique, aucun ecart du corps ou de l'inventaire n'est attendu. Si un ecart existe avant la premiere divergence, classer le resultat `INVALID_PREACTION_MISMATCH`, pas `L3`.
6. La comparaison physiologique n'est valide qu'au **premier pas a commandes differentes**. Apres cette action, deux vies se trouvent dans des etats differents. Ne pas apparier leurs pas suivants comme si le monde etait encore identique.
7. Conserver les morts et censures comme donnees, l'empreinte de physique et les hash M11. Aucun `assert` ne doit exiger que le canonique soit le meilleur.

## Critere de rapport

- `IMMEDIATE_HOMEOSTASIS_CANONICAL_BETTER`, `IMMEDIATE_HOMEOSTASIS_MASKED_BETTER`, `IMMEDIATE_HOMEOSTASIS_TIED`, ou `NOT_EXPOSED` / `INVALID_PREACTION_MISMATCH`.
- Mentionner les contributions contradictoires des quatre variables, fatigue et modalites du sommeil, sans reduire le sommeil a une seule consommation energetique.
- `L3_SINGLE_MATCHED_STAGE8_READ_MOTOR_EFFECT` acquis pour #592 si tous les controles restent identiques; ne pas le convertir en `ADAPTIVE_BENEFIT_ESTABLISHED`. **GO adaptatif, robustesse et generalisation restent `NOT_ESTABLISHED`** quel que soit le signe d'un unique pas.
- Si un signal favorable emerge, prochaine comparaison scientifique distincte: variantes **externes** d'effets physiques a la naissance et vies independantes, avec premier embranchement apparié, critères de bénéfice et horizon definis a l'avance, sans lire les effets caches, modifier les seuils/recompenses, donner des UC gratuites ni forcer une action. Aucun GO robuste sans repetabilite sur des circonstances differemment echantillonnees.

## Integration

Reutiliser le test #592 en y ajoutant seulement des observations dans `tests/i1/test_i1_natural_stage8_read_contrast_438.py`. **Aucun changement** de `src/i1/modules/`, `src/i1/runtime/`, `I0`, de la politique motrice, de la naissance, du scenario ou des limites de pas. Validation 4/4 Python 3.11/3.12 sur SHA exact, source I0, parite M11 et diff avant fusion selon #348. La CI ne fournit pas a elle seule un GO.
