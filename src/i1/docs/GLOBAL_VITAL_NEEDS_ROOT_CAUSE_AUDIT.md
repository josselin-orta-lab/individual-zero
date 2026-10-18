# I1 : audit transversal des besoins vitaux

Date : 18 octobre 2026. Diagnostic sur la PR #303. I0 et main inchangés. Aucun réglage expérimental n'est promu.

## Sources exactes

B1000 : Actions #39113415179, moteur 32761a6b715c5763a115522766fa9d9d275b2a7c, 38/40 vies auditées, 9 091 pas, 38 morts. Une archive absente.

Une ressource : Actions #39122746545, moteur b5b4c14bd92938ce12d7821ed5bc2c13faedea1f, 32 vies et WAL. TD actif contre lecture masquée, 0/+10 nourriture.

Traces TD : Actions #39124968808, moteur 26d98c47421d5047ceda37994b9faf61cb1a1aac, 24 vies et WAL, lambda 0 / 0.8 / 0.95 / 1.

Récompense : Actions #39126377429, moteur 6e569fa530f4907566fd36f987029d6c77e9beab, 12 vies, 4/4 jobs réussis. Récompense absolue vs déficit seulement, baies 0/+10, graines 511–513.

## Blocage P0-A : récompense physiologique mal orientée, expérimentalement corroboré

ValueAndNeeds.reward_between pénalise les écarts absolus aux cibles. Quand boire fait passer l'eau de 48 à 87.6 (cible 60), TD de la boisson -15.3; le même événement sous une récompense sur déficits seulement vaut +11.8. Sur trois vies appariées avec baie nutritive, le bras absolu a 51 pas à eau zéro et 127 à énergie zéro, intégrité finale moyenne 86.3; le bras déficit seulement a 0 pas à eau zéro, 0 à énergie zéro, intégrité finale 100. Même horizon 300 et 3/3 vivants dans chaque bras. Le bras baie neutre meurt 6/6 au pas 237 dans les deux représentations. Issue #306. Pas encore de validation long terme.

## Blocage P0-B : hystérésis d'objectifs non comparable à l'échelle vitale, prouvé

ValueAndNeeds.assess normalise pression = clip((setpoint - body)/100 * weight/max_weight). Eau/nourriture 60, énergie 50; donc pressions max <=0.6, <=0.6, <=0.5 et encore réduites par tempérament. GoalManagerConfig fixe replacement_hysteresis=0.1 et critical_pressure=0.9. Le dernier seuil est inatteignable pour faim/soif/énergie. Graine 302, poids intégrité 1.3956016 : quand eau et énergie sont 0, soif 0.4299, manque d'énergie 0.3583; écart 0.07165 < 0.1. L'objectif recover_energy peut bloquer drink malgré eau à zéro. Dans 8 vies avec baie nutritive et TD actif : 459 attentes parmi 462 pas où eau<=15, et 4 vies avec 50 pas eau/énergie zéro en conservant recover_energy. Eau physiquement accessible sur cellule. Issue #307.

## Blocage P0-C : affordances proposées ne franchissent pas Competition

I1PartialEvidenceAdapter attribue 0.25 * prior + 0.75 * evidence TD, borné -1..1. Competition borne l'accumulateur à zéro pour preuves négatives, seuil de référence 0.5. Graine 302, t250 : eau 0, énergie 0, nourriture 15. Une option dormir pour recover_energy est proposée avec Q négatif environ -0.52, evidence environ +0.008, aucun franchissement à c_max=5, action de secours attendre. Dormir rend pourtant +3 énergie physiquement. Cela explique un blocage entre reconnaissance du besoin et exécution, sans prouver que toute option de survie échoue pareillement.

## Blocage P1-D : valeur des étapes préparatoires, partiellement maîtrisée

Collecter consomme de l'énergie et du temps mais ne nourrit pas directement, récompense immédiate négative. Le bénéfice n'arrive qu'après manger. Sur trois graines nutritives, lambda 0 : 6 repas et aucune recollecte; lambda 0.8 : 9 repas et 3 recollectes. Lambda 0.95 et 1 n'améliorent pas cela. Valeur instrumentale existante; le problème reste la robustesse de la politique. Issue #305.

## Blocage P1-E : navigation/exploration, aggravant, pas cause racine unique

B1000 montre un défaut d'accès à l'eau perceptible quand il faut se déplacer et la concurrence avec exploration (issues #299 et #301). Mais dans le monde minimal sans possibilité de se déplacer, on observe encore soif à zéro, objectif verrouillé et attente, ce qui exclut une explication limitée à la navigation.

## Blocage P2-F : sommeil/consolidation, amplificateurs

Une forte fatigue cognitive engendre des proportions de sommeil très élevées dans certaines vies, mais le B1000 présente 38 décès audités, y compris à fatigue nulle. Dans le laboratoire minimal, pression cognitive de sommeil mise à zéro, les défauts restent. Les événements de consolidation ne suffisent pas à établir que les actions sont réutilisées.

## Blocage P2-G : coût métabolique constant

Configuration naturelle : nourriture -0.20 / pas, eau -0.40 / pas ; dégâts intégrité en pénurie alimentaire -0.5 / pas, sans eau -1.0 / pas. Attendre coûte 0.35 énergie, collecter 1, manger 0.5, boire 0.5, dormir procure +3 énergie et attendre/dormir +0.2 intégrité. Ce métabolisme est soutenable si l'acteur exécute une boucle alimentaire/hydrique, mais cause une dégradation irréversible pendant l'inaction prolongée.

## Diagnostic intégré

Déficit corporel perçu -> pression normalisée insuffisante / objectif figé -> possibilité physique proposée -> récompense TD parfois mal orientée -> evidence Competition trop faible, option écartée -> fallback attendre -> poursuite de la consommation passive -> pénurie -> perte d'intégrité -> mort définitive.

## Validation prioritaire

1. Tester à paramètres indépendants une bascule d'objectif quand le besoin vital devient urgent, sans ordre boire/manger imposé. Vérifier qu'aucune oscillation inutile n'apparaît.

2. Tester sur plus de graines et cartes le modèle expérimental de récompense par déficits seulement, en conservant la physique et le TD lambda 0.8.

3. Décomposer causalement proposition -> Q -> evidence -> Competition -> admission -> commande -> conséquence, et tester l'ablation d'une lecture Q négative invalidante sans supprimer le besoin d'apprendre.

4. Reproduire une boucle réellement autonome de 1 000 pas et plus : rapport eau, nourriture, énergie, intégrité, portions de temps en zone critique, taux de décès. Ne pas considérer une survie censurée à 300 pas comme preuve.

5. Seulement après, généraliser à deux baies, cartes avec déplacement, exploration et sommeil/consolidation.

Verdict : NO-GO pour survie vitale autonome durable. Plusieurs défaillances P0 indépendantes et interactions sont étayées; leur résolution prospective ne peut être inférée du seul audit.
