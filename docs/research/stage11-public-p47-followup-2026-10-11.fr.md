# Stage 11 : diagnostic public de prévision prospective, 24 et 32 pas

**Date :** 11 octobre 2026 en Europe/Paris (exécutions GitHub du 10 octobre en UTC). **Classification :** développement logiciel public seulement. Aucune validation scientifique held-out ou INV-25.

## Provenance

- Code réellement testé : `57f9dcd79fd98106cae5f04cd0e648bc06bf6c77`.
- [GitHub Actions #38091997219](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38091997219), Python 3.12 : **727 tests réussis** ; job complet Python multi-versions non exécuté.
- Protocole du troisième essai déclaré avant l'exécution : [protocole 24 pas](stage11-three-visit-public-development-protocol.en.md).
- Extension à 32 pas déclarée séparément avant l'exécution : [protocole 32 pas](stage11-public-32step-followup-dev-protocol.en.md).
- Configuration de curiosité distincte : `p48-three-visit-window-dev-v1`, limite de **3 visites stagnantes** au lieu des **2** de la référence. Ces seuils sont des paramètres de développement, pas une calibration scientifique.
- Monde : `small_water_gain` ; graine publique : `41` ; prévision issue de Memory explicitement activée. Le Stage 9 reste le contrôle inchangé dans chaque exécution.

## Résultats mesurés

| Indicateur | 24 pas | 32 pas |
| --- | ---: | ---: |
| Commandes de test Stage 9 appliquées | 0 | 0 |
| Commandes de test I0-vNext appliquées | 3 | 3 |
| Visites d'Exploration I0-vNext | 3 | 3 |
| Prévisions prospectives gelées avant envoi | 1 | 1 |
| Comparaisons P-47 | 1 | 1 |
| Rapports d'agence publiés | 1 | 1 |
| Actions causales avec épisode physique fermé encore en attente | 2 | 1 |
| Paires action physique fermée + rapport P-47 correspondant | **0** | **0** |
| Interventions causalement admises | **0** | **0** |
| Statut causal final | `hypothese_causale` | `hypothese_causale` |

Dans les deux exécutions, P-47 a comparé une valeur d'eau **prédite 100,0** à une valeur **observée 100,0**, tolérance **0,0**, et émis `conforming / self_compatible`. Le niveau 100 est la borne de saturation : ce résultat conforme ne permet pas de conclure seul que l'action cause la variation. Le modèle causal n'a créé aucun crédit d'intervention.

### Deux trajectoires différentes, et non une continuation

**Limite importante identifiée après l'exécution :** `preregistered_food_rewards(seed, steps)` prépare une population de valeurs de taille `steps - 1` avant de la mélanger. Passer de 24 à 32 pas change le nombre de valeurs et peut donc modifier les événements dès les premiers pas. Les calendriers ont effectivement des empreintes différentes. Ce ne sont pas deux préfixes identiques d'une même trajectoire prolongée ; aucune différence entre les deux ne peut être attribuée seulement au temps ajouté.

Empreintes de scénario :
- 24 pas : `d979224caa50aae5b62308247491f09e1fbbecaf12e4f02890e48ed89e69c4a1`.
- 32 pas : `244b4cbb82b3c674987fc05fdfdaab0f1253cb4261afb1e35b1e775860c33c99`.

Empreintes des résultats (calculées sur le diagnostic canonique) :
- 24 pas : `c9e52425c6fe15222e1dbb6ab35b893a45c0317bc309869c47c95d6aba162533`.
- 32 pas : `66bf5a05f7c2e0430bc89160a5abeddcbfa08c1fc646792e8c965333a9b42c33`.

Empreintes des journaux I0-vNext :
- 24 pas : `50c3cd2d928b285d1846cb857fe3fa704c4cb5c9c43a7921cfa3593c7b1af6d9`.
- 32 pas : `cab8ab2e29a7e3ca2105b3a85153f0ed7c0c9cfa400fb4fb819be2aa9ae1d3e7`.

## Interprétation et suite

Le passage au troisième essai a permis de traverser, dans le vrai runtime public, la chaîne `Memory antérieure → prévision prospective → Action Control → observation suivante → rapport P-47 publié`. Il **n'a pas** permis une intervention canonique : aucune paire « épisode physique fermé + même commande et même temps observé dans P-47 » n'était disponible pour promotion dans le Causal Model.

Un nouveau diagnostic de garde, **développé après ce résultat**, répertorie les pas des commandes appliquées, les épisodes physiques avec ou sans fermeture, les prévisions antérieures et les pas des rapports P-47, pour identifier la disjonction exacte. Ce diagnostic additionnel n'était pas contenu dans les 727 tests ci-dessus et doit être vérifié séparément.

Ne pas assouplir les invariants de preuve, ne pas injecter de résultat et ne pas modifier les seuils P-35 pour obtenir artificiellement `testee_par_intervention`.

**Stage 11 : EN COURS. Stage 9 : SOFTWARE IMPLEMENTED / SCIENTIFIC VALIDATION PENDING / NO-GO.**
