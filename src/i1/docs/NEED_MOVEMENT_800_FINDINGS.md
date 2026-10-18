# I1 – Endurance 800 pas : blocage des objectifs physiologiques (2026-10-18)

## Provenance contrôlée

Campagne [Actions #39115850839](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39115850839) : **12/12 jobs PASS** au SHA exact `5a8045baa7ee95ac597585a7a8c6b1b933cc41ae`. Trois mondes (garden/oasis/foraging) × deux poids géographiques (0.3/0.6) × deux poids cognitifs (0/0.2), **deux individus par job**, horizons 800 pas ou mort définitive. 24 nouvelles vies avec cartes/germes appariés, WAL séparée. Tous les jobs ont fini; «PASS» désigne une exécution valide, **pas** une survie réussie ou un apprentissage démontré. Ce rapport ne mélange pas les SHAs avec les 24 vies à horizon 300 pas de la précédente expérience. I0 et main inchangés.

## Démonstration mécanique de concurrence défavorable à l'alimentation

Individu `i1:longlife:longlife-garden:v32:seed886032:born0`, bras curiosité 0.3 / poids cognitif 0 : il boit 2 fois, mange 3 fois, collecte 5 fois, puis meurt au **pas 400** avec eau, nourriture et énergie nulles et **2 baies encore dans l'inventaire**. Commandes au total : **294 déplacements**, 94 sommeils, 2 boissons, 3 repas, 5 collectes, 2 attentes.

La **perception subjective**, et non une vue opérateur, atteste pendant **100 pas consécutifs (301–400)** : faim corporelle <= 15, deux baies dans l'inventaire. Dans ces pas, 98 commandes `se_deplacer` et 2 `attendre`, **aucun repas**.

La WAL établit qu'une option légitime `manger:target=berry_a` est bien proposée et évaluée. Sur cette fenêtre, **234 propositions (59 pas distincts)**, **233 traces Competition de cette option**, **0 franchissement de son seuil**, ratio maximum accumulateur/seuil 0.7008. À l'inverse, la frontière géographique obtient **99 traces de franchissement** et un ratio maximum 1.1247. Au pas 301, l'option de manger ne franchit pas le seuil alors que le déplacement le franchit au quatrième cycle. Le besoin de manger est présent et actif : il ne s'agit ni d'une simple absence de ressource perçue, ni d'une absence complète de capacités alimentaires. Cela démontre un **goulot d'étranglement dans l'arbitrage motivationnel/Competition**, mais pas encore la cause unique de la sous-pondération.

Autre vie : variante garden 31, curiosité 0.3 / cognition 0, 31 déplacements, 1 repas, 0 boisson, mort au **pas 237**, sans aucun indice d'eau visible adjacente sur son parcours. Il faut distinguer ce problème de recherche/revisite de ressource du blocage de consommation d'un aliment déjà détenu.

Les archives de la même campagne documentent aussi dans Oasis des décès très précoces dans certaines variantes, donc **aucune promesse de survie prolongée** ne découle de la curiosité renforcée.

## Investigations suivantes, sans modification arbitraire

1. Analyser la durée d'engagement des options de besoin, la réinitialisation par `t_monde`, les seuils, le budget de cycles et le calcul Stage8 qui transforme la valeur apprise en évidence Competition.
2. Contraster la politique d'inertie et l'accumulation *d'une seule intention déjà fondée sur la perception* avec un témoin. Ne pas coder `if food < X: manger` ni contourner Action Control.
3. Pour la revisite hydrique, étudier les cartes de visites et routes **déjà effectivement perçues** ; jamais l'emplacement de ressources cachées.
4. Sur de nouvelles naissances et nouveaux commits, évaluer les repas sous faim perçue avec baies en inventaire, boissons quand l'eau est réellement visible, détérioration physique, décisions exploratoires, mort et mémoire différée.
5. Ne pas déclarer de GO de survie ou d'apprentissage sur la base des traces Competition seules, ni sur les simples commits Stage10. Pas de rollback, résurrection ni falsification des morts.

Test ajouté : `tools/audit_i1_need_arbitration_wal.py`, uniquement externe/lecture WAL, refuse les journaux non complets et compare l'option alimentaire à la frontière sans agir sur I1. Issue dédiée : [#301](https://github.com/josselin-orta-lab/individual-zero/issues/301).

**Statut scientifique** : `NO-GO` pour promouvoir globalement le nouveau poids de curiosité ; `OPEN` pour le correctif d'arbitrage et de mémoire. Il faut de nouvelles vies de moteur corrigé avant toute intégration.
