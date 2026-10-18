# Validation prospective de la récompense TD fondée sur les déficits

Date : 18 octobre 2026. Issue #306. Base de travail : PR #309, SHA `f92dafbe9cb3b0cee643ac16e817f8328f64ab26`, car la naissance naturelle doit déjà recevoir les seuils `0.04 / 0.35`. Cette branche n'est pas une promotion de la nouvelle récompense au canon.

## Motivation et contrôle

L'expérience initiale (PR #303, Actions #39126377429, SHA `6e569fa530f4907566fd36f987029d6c77e9beab`) rapporte dans la strate nutritive trois vies appariées, 51 pas eau zéro et 127 énergie zéro sous récompense absolue contre zéro dans les deux cas sous déficit seul; 3/3 survivants dans chaque bras. Cela reste un pilote non généralisable.

Contrôle historique : `sum(w * abs(body - setpoint))` avant moins après. Signal candidat : `sum(w * max(0, setpoint - body))` avant moins après. Seul `ValueAndNeeds.reward_between` est modifié **dans la construction isolée de l'expérience**, avant le premier pas; `ValueNeeds.assess`, `reward_for`, la physique, les actions, Competition, les objectifs, les tempéraments, λ TD 0.8 et I0 restent identiques. Les surplus sont neutres pour le nouveau signal, sans présumer qu'une consommation excessive serait physiologiquement sans risque.

## Cohorte

Seize naissances indépendantes, 2 mondes (oasis et foraging), 4 graines appariées 811–814, 2 récompenses, maximum 300 pas. Chaque bras utilise le même `life_id` dans une exécution distincte, sans partage d'état ni de WAL. Le moteur calibré est vérifié à la naissance. Les journaux WAL intégraux, hachages, transitions corporelles, changements de buts, décisions Competition et mises à jour TD sont archivés.

## Conditions GO/NO-GO

Vérifier la cohérence mathématique et TD, les actions proposées et appliquées, boissons/repas réellement bénéfiques, réserves et pas à zéro, choix après apprentissage, mortalité et absence de nouvelles stratégies nocives. Un GO scientifique exige une amélioration répétée de la survie et des besoins sur des horizons plus longs et des environnements alimentaires contrôlés, et non seulement une métrique de récompense positive. Ne pas modifier I0, ni intégrer la récompense candidate sans évaluation indépendante. Ne jamais ressusciter ou relancer une identité morte.


## Première réplication prospective complétée (pas de promotion canonique)

**Actions #39134383627**, source physique `e408a9ce0c0de3bd958a4736da2d4438b447c41a`. Les 16/16 jobs ont réussi et déclaré `COMPLETED_WITHOUT_SCIENTIFIC_VERDICT`, chaque job ayant archivé sa WAL. Chiffres ci-dessous : extraction de la sortie terminale des 16 jobs (les rapports WAL demandent toujours un audit transversal indépendant).

| Monde / récompense | Naissances | Morts avant 300 | Pas à eau 0 | Pas à food 0 | Boissons appliquées | Repas appliqués |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| oasis / absolue | 4 | 1 | 223 | 0 | 9 | 16 |
| oasis / déficit seulement | 4 | 0 | 226 | 0 | 10 | 16 |
| foraging / absolue | 4 | 4 | 483 | 0 | 0 | 4 |
| foraging / déficit seulement | 4 | 4 | 492 | 16 | 0 | 0 |

Strate `oasis` : le contrôle absolu graine 812 est mort au pas 297; le traitement par déficits atteint 300 mais passe 113 pas avec eau zéro. Aux graines 813 et 814 les deux bras montrent respectivement le même comportement de boisson et de faim; la graine 811 gagne une boisson par déficit. Le contraste n'est pas uniformément bénéfique. Strate `foraging` : **8/8 décès** à pas 213–230 (absolue) et 228 (déficit), **aucune boisson dans aucun bras**. La récompense déficits produit quatre vies avec zéro repas appliqué et quatre pas nourriture à zéro chacune; le témoin totalise quatre repas. Ce défaut ne peut pas être masqué par l'amélioration du signal théorique. Aucune preuve de généralisation ou de survie autonome n'est acquise.

Décision provisoire : **GO mécanistique limité / NO-GO scientifique** pour une promotion de la récompense seule. L'expérience suggère un effet positif possible en oasis et un obstacle de navigation/Competition indépendant dans foraging. Les nouveaux témoins de source effective, de stabilité par vie et de distinction `td_applied_reward` versus récompense contrefactuelle sont engagés dans une seconde exécution; ses cohortes seront analysées indépendamment et ne doivent pas être additionnées sans vérifier la comparabilité de leur code physique.
