# I1 S1 : investigation de la domination du sommeil et de F_cog (2026-10-18)

**SHA observé** : `11fa9104e7e9d2c7ad70e837c80463fc4cbe4777`, S1 72 vies / 12 983 pas, Actions [#39091868002](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39091868002). **SHA actuel de main à l'audit** : `75762dc476ff56beb2524ff228a48595609ef591`. Les 24 archives sources ont été relues hors du modèle à partir des WAL et rapports passifs ; tous les individus et morts conservés, sans changement moteur.

## Réactivation de F_cog dans la naissance I1

Dans `src/i1/runtime/i1_natural_runtime.py`, `I1Runtime.__init__` applique `enable_natural_sleep_birth` avant construction. `src/i1/runtime/i1_natural_sleep.py` installe explicitement les coefficients suivants, qui ne sont **pas** ceux de la calibration provisoirement neutralisée :
- `fatigue_gain=0.7`, `sleep_fatigue_recovery=0.3`, `fatigue_weight=0.65` ;
- `consolidation_weight=0.25`, `night_weight=0.20`, `intrinsic_weight=0.9` ;
- `waking_recovery_profile_relief=0.0`, réveil naturel <=0.1, maximum de six pas dormis.

Cette politique avait été intégrée au nouveau modèle naturel par #246, puis déplacée sans intention de changement comportemental en #253. L'issue historique [#133](https://github.com/josselin-orta-lab/individual-zero/issues/133) documente une décision de maintenir temporairement `w_C=0` en développement et des tests anciens mettant en doute son poids ; cette archive ne constitue **pas** une référence scientifique normative pour I1 actuel.

Le mécanisme actif est :
`F_cog <- min(1,F_cog + 0.7 * UC_cycle/(C_max*B_cycle))`, puis `F_cog <- max(0,F_cog-0.3)` par vrai pas dormi.
`P_sleep = min(1,0.65*F_cog + 0.25*P_cons + (0.20 si nuit))`.
Le score intrinsèque de `dormir` est ensuite multiplié par 0.9 en compétition.

## Données factuelles S1 (72 WAL)

12 983 actions physiques, dont 10 560 `dormir` (81,34 %).
Sur 10 246 **pas éveillés avec événement de pression gelée**, moyenne `F_cog=0.810`, médiane `1.0`, 7 887 (77,0 %) avec `F_cog>=0.7` ; moyenne `P_cons=0.940` et `P_sleep=0.774` ; 8 350 (81,5 %) avec `P_sleep>=0.5`.

Le sommeil observé se décompose en **7 823 décisions `dormir` en état éveillé (74,1 % du sommeil)** et **2 737 commandes `dormir` en session de sommeil (25,9 %)**. Cette distinction est cruciale : le plafond de six pas de sommeil n'empêche pas une nouvelle décision immédiate de dormir au réveil.

On observe 4 161 entrées en session et 4 156 réveils. Raisons des réveils : `alert` 3 630, `maximum_duration` 526. Après réveil `alert`, **3 486/3 630 (96,0 %) commandes suivantes sont encore `dormir`**. Les observations corporelles après ces réveils montrent le plus souvent une eau sous le seuil critique ; cela signale une boucle alerte -> délibération -> re-sommeil, sans démontrer que l'individu percevait un approvisionnement utilisable.

Sur les 7 823 décisions de dormir, `F_cog` moyen = 0.907 et `F_cog>=0.7` dans 6 919 cas. Les autres options comparables présentes dans les journaux `stage8_option_evaluation` ont un score maximal moyen 0.066 contre 0.358 pour le sommeil. Les choix peuvent dépendre aussi de Competition, des candidats admissibles et de l'histoire ; il ne faut pas assimiler une comparaison de scores à une causalité démontrée.

## Analyse de sensibilité **statique**, non contrefactuelle

Pour les 7 249 décisions `dormir` avec `P_sleep<1` et une option alternative scorée, la soustraction **arithmétique** de `0.9*0.65*F_cog` au score observé ferait passer le score du sommeil sous celui d'au moins une alternative **dans 6 613 cas (91,2 %)**. Soustraire séparément `0.9*0.25*P_cons` donne **2 593 cas (35,8 %)**. Il ne s'agit **pas** de simulations de vie sans fatigue : le changement de paramètre aurait modifié la trajectoire ultérieure, les réveils, la mémoire, les besoins et les options. L'analyse ne prouve donc pas un gain de survie ni 91 % de sommeil en moins.

Une vie peut dormir à pression basse en raison de sa compétition, de ses valeurs ou d'une autre priorité. Même avec `F_cog=0`, la pression de consolidation et l'intérêt physique du repos sont susceptibles de maintenir le sommeil.

## Conclusion et protocole recommandé

**Résultat : forte preuve que F_cog est actif et participe massivement à la domination du sommeil, pas encore preuve unique d'un bug.** La saturation durable de `F_cog`, le backlog élevé et le re-sommeil après alertes critiques sont trois mécanismes à dissocier.

Lancer une **nouvelle campagne d'ablation prospective séparée** à partir du même SHA figé, avec naissances neuves, graines et mondes appariés et paramètres uniquement dans des bras explicitement distincts :
A) référence courante ;
B) `fatigue_gain=0` et `fatigue_weight=0` (désactivation de F_cog pour le sommeil, vérifiée sans changer M11) ;
C) `consolidation_weight=0` seulement ;
D) B+C.

Préenregistrer comme critères : pourcentage de sommeil et ses épisodes, décrochage au réveil `alert`, eau et nourriture, mortalité, exploration, vrais UC, nombre/qualité de consolidations et preuves d'apprentissage, et non un GO sur le sommeil seul. Ne pas créer d'oracle, ne pas bloquer artificiellement l'action dormir, ne pas relâcher la mortalité ou changer les contrats d'admission. Le modèle canonique actuel doit rester inchangé tant qu'un bras n'est pas validé. L'issue #292 reste ouverte.
