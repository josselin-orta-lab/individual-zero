# Issue #110 : préenregistrement prospectif du trajet partiel évaluable Stage6/8

Date : 2026-10-14. Travail approuvé par l'opérateur à la suite du funnel Competition (commit de référence `147e50684f10aba07affd0f00c21e6b3e42101ee`).

## Hypothèse falsifiable

Dans le monde sustained, le Stage6 trouve un chemin réellement simulé vers une augmentation d'inventaire comestible, mais conserve seulement la première commande de déplacement. Stage8 évalue donc un coût corporel immédiat, son evidence est négative et Competition ne sélectionne jamais l'option. **Sans modifier Competition**, étudier si présenter la séquence de prédictions déjà calculée comme horizon d'**évaluation** du plan permet de mesurer sa vraie valeur prospective. L'exécution reste limitée au **premier** geste suivi d'une nouvelle capture autorisée, nouvelle dépense UC et replanification. Une capacité de stock comestible **n'est pas** l'atteinte du setpoint alimentaire. Aucun bonus intrinsèque ou facteur ad hoc ne doit être attribué au segment dans cette expérience.

## Bras et scénario

- **P (témoin)** : Stage6 `progressive_subgoals=True`, `progressive_evaluation_prefix=False`, plan de longueur 1 comme actuellement.
- **F (hypothèse)** : Stage6 `progressive_subgoals=True`, `progressive_evaluation_prefix=True`. Seulement pour un `partial_progress` réellement trouvé, le plan proposé conserve toutes les commandes de l'itinéraire prédit de longueur **<= max_depth** pour la valuation par le Stage8 standard, tandis qu'Action Control ne peut en exécuter que la première commande, et le segment est invalidé/recalculé au pas physique suivant. Dans les deux bras, le but reste actif, seul `step_completed` qualifie le segment, et les prévisions ne sont pas des résultats vécus.
- Profils pré-naissance `restored` et `sustained`, chacun avec contrôle libre et intervention A2 déterministe après admission. **8 vies uniques × jusqu'à 36 pas = 288 pas**, sous Python 3.11/3.12, réexécutions non cumulées.
- `H_eff=3`, `max_depth=3` et `simulator.h_max=3` invariants. Stage8 évaluera au plus 3 transitions (budget déjà prévu), `R_eff` et charges UC inchangées. Aucun accès supplémentaire à Equipment au moment du choix d'option n'est autorisé hors son évaluation habituelle; les prédictions initiales du Stage6 sont des simulations déjà faites.
- Les configurations sont versionnées et OFF par défaut; Stage6 de référence, Stage8, Competition, Action Control, journal mortalité, Oracle et détecteur Stage12 restent inchangés quand le drapeau est false.

## Mesures adversariales

Vérifier dans les journaux : `stage6_planning_result`, `stage8_option_evaluation` (valeur prédite, `status`, evidence), `competition_cycle` (`crossed`), choix réellement attesté `active_goal`, premier geste effectivement appliqué, `stage6_progress_segment_closed` avant une éventuelle deuxième commande, sommeil, interventions A2, WAL et audits d'attribution. Prouver par test l'équivalence byte-identique du bras P à son comportement antérieur. Faire échouer le scénario si le second pas d'une même proposition `partial_progress` est physiquement appliqué, si le plan est pris pour un succès final, si un obstacle préexistant contourne le veto, ou si le budget de simulation est dépassé.

Comparer les propositions, évaluations, décisions, résultats d'objectif et paires, les coûts UC facturés et les temps mesurés hors I0. Aucun regroupement des vies pour remplir artificiellement `bias_min_outcomes_each=2` de Stage12.

### Critères négatifs

Si l'évaluation de toute la trajectoire reste négative, déclarer que la valeur prospective corporelle ne suffit pas, et envisager séparément une **valeur cognitive de capacité** (inventaire), seulement avec une justification normative/expérimentale indépendante. Ne pas ajuster ce signal post-hoc. Si l'Equipment exact est incomplet, ne pas inventer de transition. Ne pas annoncer de gain d'agence à partir du nombre de plans seulement.

Ne pas fusionner PR #155 ni fermer issue #110 sans preuves et réception opérateur. La spécification normative v1.3.1 demeure inchangée tant qu'une évolution n'est pas démontrée nécessaire.
