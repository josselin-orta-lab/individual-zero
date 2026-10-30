# A2-R : classement observable des admissions Competition (30 octobre 2026)

## Question et premier maillon manquant

Après #645, la provenance du gagnant Action Control et sa commande physique sont reliées, mais l'auditeur acceptait encore une admission d'un candidat de rang inférieur en présence d'un candidat déjà au-dessus du seuil. Ce manque est un contrat du lecteur externe, **pas une preuve de bug moteur**.

## Nouvelle vérification bornée

Depuis les traces Competition M11 et les signatures Stage8 établies par le rejeu froid Q/TD, le lecteur calcule l'ordre des options effectivement au-dessus du seuil : marge normalisée `(accumulator_after - threshold) / threshold`, puis signature et identifiant comme départage déterministe. Il contrôle les valeurs finies, les seuils positifs, la présence de chaque candidat et la cohérence du booléen de franchissement. Les tentatives Action Control provenant de la sélection doivent suivre le préfixe de cet ordre, en conservant les éventuels veto avant l'admission. Les chemins de repli après épuisement des candidats franchis sont uniquement bornés, **pas certifiés** comme étant les vrais plans engagés ou le vrai maximum de cycles.

Le calcul dépend des compteurs et des marges **publiés** par Competition, pas d'une reconstruction indépendante des états historiques du propriétaire, de sa fonction d'urgence, du bruit, de la fuite, du résiduel ou des décisions de sécurité de Causal Model. Le booléen `full_rank_order_independently_recomputed` reste donc `false`. Le signal `native_crossing_and_rank_prefix_consistent` ne doit jamais être présenté comme une preuve de médiation causale Q→action.

## Falsification et limites

Cas adversariaux : admission hors ordre, candidat manquant, faux franchissement, marge inférieure au seuil, seuil nul, flottant M11 non canonique, accumulateur négatif, candidat non évalué mais modifié, références de source et ordre des commandes. Vérifications ciblées et quatre vies M11 techniques uniquement. Aucune naissance H192 confirmatoire, aucun changement I1/I0, UC ou physique. Les portes `veto_truth_independently_recomputed`, `full_rank_order_independently_recomputed`, `Q_to_action_counterfactual_proven`, `preregistered_mechanism_exposed`, `study_admissible` restent fausses.

A1-C = NO_GO ; A2-R = NOT_EXECUTED (0/96) ; L3 global = NOT_ESTABLISHED.
