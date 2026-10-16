# A2.30-S : préenregistrement des observations qui discriminent réellement des causes cachées

**15 octobre 2026. Préenregistrement AVANT code ou résultat S.** Source : PR #189, SHA `77a77acb771df7c2b66f4ea4955763b512555332`, campagnes P/Q/R reproductibles; `main` au commit `cb630f6edffab1aecb4630e2b7da2369bb593118`. Issue #110 ouverte et Stage12 PARTIAL. Ce protocole autorise seulement des expérimentations sur des mondes `WorldBody` de laboratoire autonomes, **aucun I0 vivant**, aucune commande imposée à I0, aucun enrichissement de son modèle ou de sa perception.

## Question et prévisions testables

À partir de deux mondes physiquement différents mais **observationnellement identiques avant toute intervention**, quand une différence devient-elle accessible à la perception de Stage3 ? Une observation accessible après avoir pris le risque ne peut pas être présentée comme une information disponible pour décider de le prendre.

Hypothèses préenregistrées :

- **S1, risque alimentaire :** `attendre` puis `collecter(berry_a)` ne discrimine **aucun** effet caché du même fruit avant la commande d'ingestion. Deux mondes survivants (fruit bénin vs fruit `integrity_delta=-7`) divergent **uniquement après `manger` à t3** ; un monde `integrity_delta=-100` devient terminal à t3 et **ne produit aucune observation vécue postterminale**. L'auditeur externe peut prouver la mortalité mais ne l'attribue pas au savoir de I0.
- **S2, risque spatial :** une attente initiale ne distingue pas une case est sûre, une zone de danger cachée (dommage 40 par pas) ou une zone létale immédiate. Le déplacement effectif à l'est à t2 permet de percevoir une perte d'intégrité chez les survivants dans le monde dangereux, **après l'exposition** ; le monde létal s'arrête à t2 et aucune capture postmortem n'est étiquetée vécue.
- **S3, dérive corporelle :** une seule attente permet de différencier au t1 une décroissance cachée de nourriture (0,5 vs 2,5) ou d'eau (0,2 vs 2,2) à partir de la télémétrie **autorisée**. Cette discrimination locale ne renseigne pas sur la toxicité d'un fruit ou une zone invisible.
- **S4, coût et limites :** enregistrer exactement le coût corporel (énergie, nourriture, eau, intégrité), le nombre de commandes appliquées avant la discrimination et les cas où une sonde ne peut rien discriminer sans prise de risque; ne jamais inférer un coût UC de mondes dépourvus de noyau I0.

## Plan factoriel et comptabilité figés

Trois familles de 3 causes physiques, nourriture initiale {35,45}, positions {(5,5),(7,7)} : **36 mondes physiquement indépendants** (3×3×2×2). Physique 32×32 avec `initial_integrity=100`, initial_energy=50, initial_water=20, coût d'action `attendre=0.5`, `collecter=0.75`, `manger=0.5`, `se_deplacer=1.0`; décroissance `food=0.5`, `water=0.2`, repos sans récupération d'intégrité, même configuration d'une famille à l'autre sauf facteur latent explicitement modifié.

1. **FOOD**, causes `benign`, `toxin_7`, `toxin_100`, ressource `berry_a` sur la case de départ ; **préfixe physique identique** `attendre(t1) → collecter(berry_a)(t2) → manger(berry_a)(t3)`, **12 mondes / 36 pas physiques**, dont 4 terminaisons à t3.
2. **MOVE**, causes `clear`, `danger_east_40`, `lethal_east` ; **préfixe identique** `attendre(t1) → se_deplacer(east)(t2) → attendre(t3)`; le monde létal s'arrête immédiatement à t2, **12 mondes / 32 pas physiques** avec 4 terminaisons à t2.
3. **DECAY**, causes `baseline`, `food_decay_25`, `water_decay_22` ; `attendre(t1) → attendre(t2) → attendre(t3)` dans les trois cas, **12 mondes / 36 pas physiques**, aucune terminaison.

**Total : 36 mondes / 104 transitions réellement appliquées**. Chaque scénario enregistre les captures avant la première action et après chaque action tant que le corps est encore vivant, la suite de commandes et les conséquences physiques vérifiées par le laboratoire. La capture technique après une transition terminale peut être conservée dans la preuve externe, **mais ne doit jamais être incluse dans une suite d'observations vécues**. Les commandes sont préengagées au laboratoire; elles ne sont pas des actions spontanément choisies par I0.

## Frontière de l'information, score et contrôles négatifs

Reconstituer chaque état vécu via `SymbolicPerception.capture` et `state_from_capture`, **sans** `WorldBody.ground_truth`, `WorldLayout` caché ou `TransitionResult.effects` dans le score de perception. Le juge externe seul connaît les variantes latentes, les dommages et le pas du décès. Comparer **tous les états accessibles** au sein d'un même triplet physique : pour chaque couple de variantes et chaque préfixe, trouver le **premier pas où les deux individus encore vivants** auraient des observations différentes. Lorsqu'une des branches meurt, marquer `external_terminal_without_postmortem_perception`, pas `I0_observed_hazard`. Exiger les observations identiques initialement, la provenance des captures et un jeu séparé de mesures corporelles et de preuves externes.

**PASS technique** seulement si (i) tous les mondes naissent et finissent dans le schéma fixé; (ii) aucun pas après terminal; (iii) S1 et S2 n'utilisent pas de vérité cachée avant l'action exposante; (iv) S3 observe les deux décroissances après un pas; (v) la mortalité externe n'est jamais requalifiée en perception vécue; (vi) contrôles adversariaux rejetant au minimum une fausse observation précoce, une capture postterminale prétendue vécue, un décès falsifié et une contamination par `ground_truth` ou un champ oracle.

**Conclusion scientifique attendue (non supposée positive) :** le gain d'information dépend du type de facteur et du moment de son observation. Une « exploration » qui exige de manger ou d'entrer dans une zone cachée avant d'obtenir l'information n'est pas une sonde préalable sûre; une attente peut mesurer une dérive physiologique sans rendre une baie moins incertaine. Ces comparaisons portent sur **une matrice déterministe définie par l'opérateur**, pas une fréquence réelle de danger.

La suite éventuelle **A2.30-T** serait un audit *shadow* séparé, comparant plusieurs préfixes alimentaires au regard de ce qui était observable **avant** le choix; aucun modèle expérimental ne devient un `EquipmentModel` ou une politique d'action sans décision opérateur. **A2.30 PARTIELLE, Stage12 PARTIAL, issue #110 OPEN ; toute PR reste DRAFT.**
