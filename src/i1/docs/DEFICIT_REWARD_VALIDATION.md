# Validation prospective de la récompense TD fondée sur les déficits

Date : 18 octobre 2026. Issue #306. Base de travail : PR #309, SHA `f92dafbe9cb3b0cee643ac16e817f8328f64ab26`, car la naissance naturelle doit déjà recevoir les seuils `0.04 / 0.35`. Cette branche n'est pas une promotion de la nouvelle récompense au canon.

## Motivation et contrôle

L'expérience initiale (PR #303, Actions #39126377429, SHA `6e569fa530f4907566fd36f987029d6c77e9beab`) rapporte dans la strate nutritive trois vies appariées, 51 pas eau zéro et 127 énergie zéro sous récompense absolue contre zéro dans les deux cas sous déficit seul; 3/3 survivants dans chaque bras. Cela reste un pilote non généralisable.

Contrôle historique : `sum(w * abs(body - setpoint))` avant moins après. Signal candidat : `sum(w * max(0, setpoint - body))` avant moins après. Seul `ValueAndNeeds.reward_between` est modifié **dans la construction isolée de l'expérience**, avant le premier pas; `ValueNeeds.assess`, `reward_for`, la physique, les actions, Competition, les objectifs, les tempéraments, λ TD 0.8 et I0 restent identiques. Les surplus sont neutres pour le nouveau signal, sans présumer qu'une consommation excessive serait physiologiquement sans risque.

## Cohorte

Seize naissances indépendantes, 2 mondes (oasis et foraging), 4 graines appariées 811–814, 2 récompenses, maximum 300 pas. Chaque bras utilise le même `life_id` dans une exécution distincte, sans partage d'état ni de WAL. Le moteur calibré est vérifié à la naissance. Les journaux WAL intégraux, hachages, transitions corporelles, changements de buts, décisions Competition et mises à jour TD sont archivés.

## Conditions GO/NO-GO

Vérifier la cohérence mathématique et TD, les actions proposées et appliquées, boissons/repas réellement bénéfiques, réserves et pas à zéro, choix après apprentissage, mortalité et absence de nouvelles stratégies nocives. Un GO scientifique exige une amélioration répétée de la survie et des besoins sur des horizons plus longs et des environnements alimentaires contrôlés, et non seulement une métrique de récompense positive. Ne pas modifier I0, ni intégrer la récompense candidate sans évaluation indépendante. Ne jamais ressusciter ou relancer une identité morte.
