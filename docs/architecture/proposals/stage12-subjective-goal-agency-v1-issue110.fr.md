# Proposition non normative — Attribution subjective d'un résultat d'objectif (issue #110)

**Proposition** `stage12-subjective-goal-agency-v1` ; **NON APPROUVÉE**, non exécutable et sans modification des spécifications de référence.

## Constat ancré dans `main` du 13 octobre 2026

La norme v1.2.1 §9.6 permet au comparateur P-47 d'indiquer qu'un effet est `self_compatible`, `world_justified` ou `uncertain`. `self_compatible` correspond à une conséquence *compatible avec* une attribution personnelle ; `world_justified` est justifié perceptivement seulement pour une discordance et une cause extérieure identifiable. Aucune de ces catégories n'est une déclaration générale « je suis responsable de la réussite de mon objectif » ou « le monde est responsable de mon échec ».

`Stage12GoalProgressLedger` préenregistre et vérifie déjà un gain strict de ressource sur un pas réel. `Stage12LivedDetectors` sait traiter des triplets vérifiés, mais le runtime publie actuellement `outcome=agency=unknown`, et l'audit refuse à raison toutes les affirmations non justifiées. Le nombre de pas ne remédie pas à ce manque.

## Options soumises à l'opérateur

**A : conserver la sémantique actuelle, refuser la calibration (choix conservateur par défaut).** Aucun nouveau producteur, `attribution_bias=None` et issue #110 ouverte. Pas de biais artificiellement inventé ; Stage12 non réceptionné sur ce critère.

**B : définir explicitement un jugement subjectif *du résultat* dans Action Control (recommandé uniquement si la norme est amendée).** Introduire un enregistrement signé par provenance logique `subjective_goal_agency_v1` : identité de vie, commande admise et exécutée, `goal_ref`, `intent_ref`, `comparison_ref` éventuelle, `judgement_ref` unique, horodatage d'émission, `self|world|unknown`, provenance cognitive et incertitude. Le producteur doit émettre son appréciation à partir de variables accessibles à I0, sans recevoir ni la classification `success/failure` du registre de progression, ni Oracle/Bench/causes cachées, ni un résultat de détection. L'absence d'indice distinct conduit à `unknown`. Il faut définir précisément les conditions perceptives d'un `self` authentique plutôt que convertir `self_compatible` mécaniquement ; si aucun tel indice n'existe, la sortie `self` reste indisponible. Les étiquettes P-47 sont conservées sans changement.

**C : étendre explicitement la sémantique P-47 existante.** Modifie le contrat de comparaison et tous ses consommateurs, notamment modèle causal et κ ; migration plus risquée, susceptible de casser les barrières DC-05 et DC-06. Déconseillée pour un correctif minimal.

## Préconditions impératives de B

1. Approuver une évolution normative versionnée, puis fixer par contrat les indices autorisés et leurs règles de décision `self/world/unknown`. Un succès ou un échec d'objectif n'est **jamais** un indice d'agence à lui seul.
2. Définir une publication Action Control indépendante, à la fermeture de la fenêtre perceptive, avec coût UC explicitement facturé si le calcul est cognitif. Pas d'étiquette forgée par Lab ou par l'auditeur.
3. Metacognition rejoint uniquement `goal-progress-intent` préaction, `goal-progress-followup` vérifié et jugement original d'Action Control, après tous les événements sources ; le résultat admis attend le diagnostic suivant, sans modifier rétrospectivement celui déjà publié.
4. Protéger la jointure dans la custody unique Metacognition et sa génération transactionnelle M-11 : unicité par référence, identité de vie, tentative, pas, cycle, fenêtre, contexte de mortalité, refus UC, aucune duplication par cycles supplémentaires et aucune restauration d'historique.
5. L'auditeur externe reconstruit chaque lien depuis les événements canoniques et refuse une assertion dont les sources ont été modifiées malgré une chaîne hash valide. Le journal seul atteste la cohérence de la trace, **pas** la vérité physique indépendante.
6. Préenregistrer deux résultats réellement indépendants par classe, des jugements distincts et des contrôles négatifs ; publier les refus, inconnus, mortalité et résultats nuls. La réception scientifique finale appartient au Stage 13 global.

## Arbitrage nécessaire

Tant que les indices subjectifs `self` et `world` ne sont pas définis et acceptés, **option A** est le seul comportement défendable. Ce document ne crée ni nouveau composant, ni seconde custody, ni diagnostic positif artificiel. La PR #110 peut améliorer le contrôle technique des absences sans fermer l'issue.
