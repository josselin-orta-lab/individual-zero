# Stage 12, issue #110 : A2.17, protocole préenregistré de contrastes causaux perceptifs

Date : 2026-10-14. Base vérifiée : `main@e80ed9b2ccbaf0d3f04f05b3342b0be6a4b6e8c3`. Statut scientifique de départ : PARTIAL, sans réception opérateur. La spécification `docs/architecture/reference/en/mvp-specification-v1.3.1.md` est inchangée.

## Observation qui motive l'expérience

Les 16 vies A2.10b déjà scellées (672 pas) ont fourni 22 résultats d'objectifs vérifiés, 14 paires admissibles, 10 paires consommées et zéro fenêtre calibrable à 2 succès + 2 échecs sur 12 diagnostics. A2.16 a prouvé que les huit jugements `unknown` portent sur des **échecs vécus** : six collectes alimentaires avec mécanisme `unresolved`, deux déplacements avec indice spatial ambigu. Ces huit jugements étaient payés et munis de `cue_ref` authentiques. Six autres vies de 600 pas (3 600 pas physiques) n'ont produit aucune fenêtre calibrable. Ce sont des observations, pas la preuve que l'individu doit s'attribuer les échecs.

## Hypothèses concurrentes, avant mesure

- **H1 : abstention justifiée.** Les captures actuellement accessibles ne distinguent pas suffisamment l'effet de la commande des perturbations indépendantes. Dans ce cas, `unknown` est le résultat correct pour l'épistémologie interne, même si l'observateur externe connaît la cause.
- **H2 : indice perceptif manquant dans le modèle.** Une conséquence déjà accessible à la première personne (inventaire, position, ressource/obstacle adjacent) pourrait fournir un indice discriminant, mais la politique `unresolved` ne l'exploite pas. Une modification n'est recevable que si elle résiste aux perturbations extérieures et aux contrefactuels.
- **H3 : attrition temporelle.** Les jugements peuvent être légitimes, mais la fermeture du pas et le sommeil empêchent la consommation au diagnostic suivant ; l'observateur doit comptabiliser les paires expirées sans inventer de diagnostic éveillé.

## Expériences à réaliser sur le vrai runtime

Préalablement à toute modification cognitive, établir une matrice de scénarios **sur plusieurs seeds indépendantes**, avec **600 pas maximum par vie pour la première passe**, et conditions ON/OFF strictement appariées en seed, état initial, budget UC, objectifs et paramètres de sommeil. Les expériences doivent contenir :
1. Collecte volontaire dans une cellule avec ressource perceptible, et collecte volontaire dans une cellule sans ressource. Mesurer les changements d'inventaire, la capture et le jugement sans considérer l'échec comme `world` par défaut.
2. Collecte ou mouvement avec modification extérieure indépendante, temporellement proche. La vérité de cette modification appartient uniquement à l'observateur. Une capture identique ne doit pas donner à I0 une causalité extérieure inférée à partir du seul ordre des événements.
3. Déplacement vers une cible initialement accessible puis bloquée ; cible toujours bloquée ; déplacement réussi ; déplacement ambigu. Contrôler séparément les indices avant/après et les jugements.
4. Cas alimentaires bénéfiques, nocifs et retardés pour empêcher toute généralisation de sécurité Stage9/DC-05 depuis une simple ingestion ou un résultat conforme.
5. Répéter la matrice avec et sans la politique candidate, seulement si H2 est étayée et qu'une correction générale minimale peut être justifiée. Ne pas modifier les règles d'agence au stade du préenregistrement.

## Instrumentation, critères de décision

Tous les journaux doivent être WAL/scellés et vérifiés par les auditeurs indépendants de chaîne, objectif, première personne et jointure GA-06. Capturer les `goal_agency_precommitted`, `goal_agency_judgement`, `goal_progress_followup`, `attribution_pair_admitted`, `attribution_sample_unavailable`, `lived_diagnostics_published`, reçus UC et transitions physiques. Le banc peut étiqueter les interventions extérieures, mais ces étiquettes ne doivent jamais traverser la frontière cognitive.

**Critères de réussite préalables :**
- Intégrité : zéro fuite Oracle, zéro faux reçu, zéro échec d'audit ; rejeter toute vie dont la provenance est incohérente.
- Attribution : conserver `unknown` si les indices accessibles ne discriminent pas réellement ; un succès prédictif ne suffit pas pour `self`, et un échec ne suffit pas pour `world`.
- Discrimination : rapporter les confusions par condition externe, les jugements suspendus et la différence ON/OFF, pas seulement le taux de jugements non-`unknown`.
- Calibration : recalculer les fenêtres complètes de 12 diagnostics, cases vides comprises, sans abaisser le seuil de 2 succès et 2 échecs.
- Compétence : compter uniquement les conséquences alimentaires vécues, les effets nocifs et les effets retardés, séparément des prédictions.
- Diversité/stabilité : comparer les actions distinctes, fixations et régressions sur 600 pas par seed ; prolonger seulement en cas de signal motivé.
- Reproductibilité : conserver SHA du code, seeds, configurations, archives et échecs ; un second Python sur les mêmes seeds est une répétition technique et non de nouveaux sujets.

**Règle de décision :** si les captures ne distinguent pas les causes, maintenir la politique actuelle et le verdict PARTIAL ; si H2 est confirmé par une différence perceptive contrôlée, proposer une correction générale minimale dans une PR distincte avec tests adversariaux et ablation réelle. Aucune modification normative silencieuse. Stage 12 ne peut être déclaré terminé avant réception de l'opérateur.
