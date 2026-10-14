# Proposition normative conditionnelle : planification progressive bornée (Stage 6)

Date : 2026-10-14. **Statut : candidate, non normative.** L'opérateur autorise l'évolution du MVP si nécessaire. Le document de référence `docs/architecture/reference/en/mvp-specification-v1.3.1.md` demeure immuable pendant l'expérimentation ; cette note anticipe un éventuel addendum à examiner après preuves.

## Réutilisation du contrat existant

v1.2.1 §8.11 exige de conserver un but actif, de rechercher avec budget et de ne pas considérer un échec à horizon fini comme une impossibilité. §12.4 impose des budgets cohérents entre options et l'indisponibilité d'une simulation incomplète. La v1.3.1 exige la conservation du journal exhaustif, la mortalité et l'absence de fuite Oracle. Une recherche de segment de progression **à horizon borné, selon des observations accessibles** peut donc être expérimentée sans changer ces principes.

## Addendum candidat uniquement si la réception le justifie

- Planning peut proposer un **segment intermédiaire**, payé dans son budget existant, lorsqu'aucun plan complet atteignant le critère de but n'est trouvé. Ce segment est issu d'une transition prédite par le modèle Equipment gelé, à partir de la capture accessible, sans comparaison oracle.
- Le segment contient une commande exécutable, garde l'identifiant de but et le motif `active_goal`, mais ne change **jamais** la condition de satisfaction finale. Sa condition locale `step_completed` ne peut être prise pour une preuve `goal_satisfied`.
- Après chaque commande, une nouvelle capture permet de proposer un autre segment. Aucune nouvelle commande n'est envoyée sans choix Competition et admission/veto Action Control. Si la commande ou le critère est ambigu, le système diffère et peut s'abstenir.
- Les résumés de progrès et les révisions restent causaux, persistés et repris via M11, sans rejeu d'une action déjà validée. Les échecs moteurs et les contraintes externes restent distingués des jugements d'agence.
- Une étude expérimentale doit démontrer amélioration réelle, absence de régression, stabilité UC et absence de biais induit. Si le contrat présent suffit, **ne pas publier de nouvelle norme inutilement**.

## Limite importante

L'option actuelle est derrière `Stage6PlanningConfig.progressive_subgoals` (désactivé par défaut). La campagne comparative à 8 vies indépendantes n'est pas une démonstration scientifique complète. Le paramètre ne doit pas être activé globalement dans `main` avant analyse des résultats, tests de reprise M11 et arbitrage explicite de réception. Préserver les documents normatifs historiques.
