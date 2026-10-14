# Issue #110, Stage 12 : préenregistrement prospectif A2

Date : 2026-10-14. Décision opérateur : A2 explicitement autorisée. Cette note est committée **avant** le code A2, le runner et toute nouvelle exécution. Elle ne modifie pas la spécification normative v1.3.1.

## Hypothèse falsifiable

Une intervention extérieure **préprogrammée**, appliquée *après une admission et un engagement moteur libres, mais avant l'unique transition WorldBody.apply*, peut rendre non passable une destination de but qui était directement perçue passable lors de l'admission. À la capture suivante, I0 peut produire un jugement subjectif `world` si et seulement si l'engagement, l'immobilité et le changement de passabilité pertinent sont effectivement vécus et facturés. L'évaluateur vérifie séparément la chronologie physique ; le modèle cognitif n'accède ni à la vérité cachée ni aux événements du scénario.

## Contrastes préspécifiés

- A2 libre : aucune intervention, même disposition eau/nourriture. Résultat `self` possible si le mouvement est effectivement vécu.
- A2 obstacle émergent : intervention fixe `set_obstacle` à `t_monde=2`, phase `after_admission`, position (3,1), uniquement après l'admission, avant l'application physique ; aucune condition sur le sens de la commande ni sur la décision de l'agent.
- Contrôle obstacle préexistant : la même cellule est non passable dès la première capture ; le planificateur doit préserver son veto.
- Contrôle échec sans nouvel obstacle : immobilité sans nouveau changement perceptif ; `world` interdit.
- Contrôle confusion temporelle : nouvelle obstruction sans commande engagée ni capture adéquate ; pas de couple d'attribution.
- Contrôle falsification : journal rechaîné modifiant ordre, phase, position ou passabilité ; audit indépendant doit rejeter.
- Cohorte : identités de naissance uniques et journaux WAL intègres ; Python 3.11/3.12 comme contrôle de déterminisme, pas doublement d'effectif.

Le pilote autonome reprend le corpus Equipment formé **avant naissance**, par vraies transitions WorldBody, et les scénarios spatialement situés de la PR #155. Quatre vies (eau/nourriture × libre/intervention) jusqu'à 50 pas chacune, sans commande forcée, sans contournement Stage6, sans changement de seuil du détecteur : `window=12`, `bias_min_outcomes_each=2`, `threshold=0.75`. Si aucune commande n'est engagée vers la destination lors du pas fixé, le résultat est négatif, pas une invitation à déplacer la date après observation.

## Critères d'analyse préalables

Séparer les transitions physiques effectives, captures accessibles, pré-engagements de critère spatial, UC acceptées, jugements cognitifs, jointures, couples appliqués au diagnostic, abstentions et étiquettes causales *externes* vérifiées. Enregistrer numérateurs et dénominateurs, journal intégral, SHA-256 et CI exacte. Le succès logiciel de fixtures n'est jamais une vie autonome. Une observation `world` isolée n'est pas une preuve du détecteur de biais ; l'absence de `world`, une erreur d'audit ou une collision d'identité reste un NO-GO explicite. Stage12 attend la réception opérateur, Stage9 reste NO-GO.

## Discipline d'architecture

L'extension physique autorisée utilise le propriétaire WorldBody déjà existant, l'injection de scénario atomique et journalisée, le même expéditeur Action Control, le propriétaire GA Action Control, l'unique registre Metacognition, les coûts P43 et les garanties M11. Aucune nouvelle seconde autorité d'action, de restitution du passé ou de lecture oracle. Toute incompatibilité normative explicite bloque l'extension, à soumettre à l'opérateur.
