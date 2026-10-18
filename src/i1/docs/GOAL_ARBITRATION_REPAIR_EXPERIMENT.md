# I1 : étalonnage expérimental des objectifs vitaux

Date : 18 octobre 2026. Issue #307. PR #308. Branche I1 dédiée; baseline source PR #303 (moteur I1, pas main). La cible scientifique est l'arbitrage entre besoins réellement vécus, jamais un réflexe imposé vers la nourriture ou l'eau.

## Hypothèse préenregistrée

Avec les cibles corporelles actuelles, la pression relative est bornée à 0,6 pour eau/nourriture et 0,5 pour énergie, et peut être encore réduite par la pondération innée de l'intégrité. Le GoalManager a pourtant un seuil critique de 0,9, et exige un écart absolu 0,1 pour basculer de but. Certaines vies ont eau=énergie=0 tout en conservant recover_energy et en choisissant attendre. L'hypothèse est qu'une hystérésis moins rigide et un seuil critique accessible permettront la reprise de la délibération sur boire/énergie, sans modifier la valeur des actions.

## Trois configurations étudiées

| Bras | Hystérésis de remplacement | Pression critique de sortie réfractaire |
| --- | ---: | ---: |
| baseline | 0,10 | 0,90 |
| calibrated-004 | 0,04 | 0,35 |
| responsive-002 | 0,02 | 0,25 |

À chaque naissance, le contrat GoalManager est reconfiguré dans le sous-arbre Stage4 des configurations Stage11/Stage10 synchronisées. Les paramètres effectivement reçus par le GoalManager vivant sont enregistrés dans le résultat de vie et vérifiés. L'action réelle demeure choisie par le chemin Value/Needs → GoalManager → options → Competition → Action Control. Aucun ordre manger, boire ou dormir n'est ajouté. La représentation des récompenses TD reste celle de référence (écarts absolus), λ TD=0,8, sélection des options inchangée, physique naturelle conservée, mémoire et tempérament inchangés.

## Plan physique

Exécution : [workflow I1 goal arbitration sensitivity](https://github.com/josselin-orta-lab/individual-zero/actions/workflows/i1-goal-arbitration.yml), lancement initial #39130169691 (défaut technique d'import des tests; **aucune observation scientifique**), relance corrigée [#39130241700](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39130241700), commit physique 288dbcb4c98c6bff4f41ea4943adc3f4286a5723.

3 bras × 8 nouvelles vies / bras, graines 501-504 et 601-604, appariées sur les mêmes world layouts et tempéraments déterministes, horizon maximal 300 pas, arrêt mortel irréversible. Monde enregistré learning-cell-one avec baie_a nourrissante (+10), eau physiquement disponible sur la cellule de naissance, obstacles sans navigation possible, pas de danger ni toxine. Pression cognitive de sommeil nulle uniquement dans ce laboratoire, la récupération physique et métabolisme sont inchangés. Chaque vie produit une WAL chaînée et scellée (pas de reprise d'identité).

## Endpoints et critères de décision

Primaires : nombre de basculements de but pendant une eau <=15 et alors que le but principal est recover_energy; nombre de cycles boire effectivement proposés et franchis dans Competition; consommation d'eau réellement appliquée et gain corporel confirmé; temps eau/énergie/nourriture à zéro; morts/temps de survie; comparaisons appariées avec contrôle baseline.

Secondaires : oscillation d'objectifs (nombre de changements successifs sans progrès du besoin), temps de panne malgré eau perceptible, actions attendre, épisodes de satisfaction des cibles et intégrité. Un gain de nombre de basculements sans gain d'actions utiles **n'est pas un GO**; des valeurs Q négatives peuvent encore bloquer Competition indépendamment de ce test. La crise de soif n'a pas de connaissance innée de l'emplacement de l'eau : elle choisit un but selon son propre corps seulement.

**NO-GO** si la baisse de l'hystérésis n'augmente pas les actions utiles ou amplifie le chattering; **INCONCLUSIVE** si manque de situation critique ou données insuffisantes; **GO local** seulement avec basculements authentiques, exécutions utiles réellement observées et meilleur maintien des besoins sans oscillations induites, puis à confirmer sur plus de graines, 1000+ pas, autres mondes et récompense TD corrigée indépendamment. Aucun merge vers main avant preuve robuste, I0 strictement préservé.
