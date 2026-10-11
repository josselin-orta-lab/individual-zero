# Individual Zero — MVP v1.3 (PROJET) : développement pragmatique, validation opérateur et science différée

**Statut : PROPOSITION NON EN VIGUEUR.** L'opérateur doit approuver explicitement son adoption.
**Date :** 11 octobre 2026.
**Référence architecturale héritée :** [MVP v1.2.1 anglais](../en/mvp-specification-v1.2.1.md).
**Document normatif proposé :** [delta v1.3 anglais](../en/mvp-specification-v1.3-draft.md), qui prévaut en cas de divergence de traduction.

## 1. Objet

Terminer les treize stages du logiciel Individual Zero sans exiger, à chaque stage, les preuves statistiques ou scientifiques complètes. Conserver la vérification des contrats techniques, de la sécurité et de l'intégrité. Autoriser une hypothèse de bon fonctionnement fondée sur une observation reproductible de **600 pas du monde**, puis réserver **la validation scientifique séparée de chaque module et du système intégré à la fin du MVP**.

Une preuve de développement n'est jamais une preuve scientifique absolue. Une hypothèse peut être plausible, réfutée ou indéterminée. La validation d'ingénierie ne transforme jamais un NO-GO scientifique en GO scientifique.

## 2. Deux axes indépendants

**État d'ingénierie d'un stage :** EN_COURS, PRET_POUR_OPERATEUR, TEST_OPERATEUR_REQUIS, REFUSE_PAR_OPERATEUR, ACCEPTE_PAR_OPERATEUR.

**État scientifique :** NON_TESTE, NO_GO, NON_CONCLUANT, ETAYE_AVEC_LIMITES, NON_ETAYE.

Seule une décision explicite, traçable et attribuable de l'opérateur donne à un stage l'état ACCEPTE_PAR_OPERATEUR. Aucune IA, PR fusionnée, CI verte ou exécution locale ne vaut signature. Un stage terminé est **terminé en ingénierie**, pas scientifiquement certifié. Les statuts d'ingénierie et scientifiques doivent pouvoir diverger, notamment pour le Stage 9.

## 3. Déroulement standard : observation sur 600 pas

Les **600 pas** désignent des pas du monde validés, et non 600 cycles cognitifs. Avec 300 pas par jour simulé dans la v1.2.1, ils correspondent à **deux jours simulés**.

Avant le test, l'agent fixe et consigne : commit complet, configuration et équipement, graine de développement publique, état initial, scénario, stimulus attendu, comportement observable, compteur de réponses, critères qui infirmeraient l'hypothèse. Il n'utilise jamais de données held-out indépendantes dans un essai de développement.

L'essai se déroule dans le runtime intégré réel. Il doit provoquer le comportement central du stage. Les événements, décisions, erreurs, journaux intègres, compteurs de sécurité, paramètres, empreintes et résultats sont conservés. La réexécution déterministe et les contrôles techniques pertinents doivent réussir. Une absence de stimulus est NON_OBSERVE, pas REUSSI. Une interruption dangereuse n'est pas masquée par la concaténation silencieuse de plusieurs vies.

À l'issue de l'observation, l'agent peut seulement conclure : **« Dans ce scénario de 600 pas, le comportement observé est compatible avec l'hypothèse de fonctionnement »**, ou signaler un échec / résultat non concluant. La robustesse statistique, le transfert à d'autres mondes, la stabilité sur 60 jours, les effets rares et les comparaisons interindividuelles restent à démontrer.

Les tests unitaires, contractuels, de sécurité, de causalité du runtime, d'isolation de l'oracle, de déterminisme, de rejeu et d'invariants applicables **ne sont jamais dispensés** par une réussite sur 600 pas.

## 4. Passage d'un stage au suivant

1. Implémenter la fonction et les contrats décrits dans la spécification héritée.
2. Vérifier les invariants applicables et les régressions, sans masquer les échecs.
3. Observer le comportement cible sur 600 pas avec stimuli et mesures interprétables.
4. Livrer un dossier court : commit, objectif, protocole, observations, erreurs, indicateurs, limites et questions scientifiques différées.
5. **Demander explicitement la validation de l'opérateur.** L'opérateur peut accepter, refuser ou imposer une vérification dans ses conditions réelles d'exécution (machine, dépendances, scénario, observabilité). Un test physique ou manuel demandé fait partie de la décision et le stage demeure ouvert tant qu'il n'est pas examiné.
6. Un stage ACCEPTE_PAR_OPERATEUR peut être déclaré « terminé (ingénierie) » et le travail progresse. L'opérateur n'est jamais réputé avoir accepté par silence.

Un résultat scientifique manquant ne bloque pas **le développement expérimental** du stage suivant. En revanche, une violation d'invariant technique ou de sécurité applicable bloque sa validation technique. Si l'absence d'un résultat scientifique limite l'interprétation du comportement, l'écart reste affiché et ne devient pas un succès tacite.

## 5. Adaptation de la feuille de route

Les objectifs et interfaces des **Stages 1 à 12** hérités de la v1.2.1 ne changent pas. Leur clôture suit maintenant les règles ci-dessus.

**Stage 1 :** substrat, contrats et déterminisme.
**Stage 2 :** monde, corps et banc d'évaluation.
**Stage 3 :** réflexes et veto.
**Stage 4 :** boucle cognitive minimale.
**Stage 5 :** tempérament et premiers individus.
**Stage 6 :** équipement, simulateur et planification.
**Stage 7 :** mémoire.
**Stage 8 :** apprentissage et calibration.
**Stage 9 :** modèle causal et agency.
**Stage 10 :** sommeil et consolidation.
**Stage 11 :** exploration et modulation.
**Stage 12 :** métacognition, santé et garde-fous.

Le **Stage 13** devient **intégration et réception opérationnelle du MVP complet** : tests intermodules, vérification technique exhaustive, observabilité, parcours intégré d'au moins 600 pas, manuel de lancement et réception explicite de l'opérateur. Il ne vaut pas homologation scientifique.

L'ancienne campagne MVP du Stage 13 est déplacée vers une **Phase S : validation scientifique post-MVP**, avec données indépendantes et protocole préenregistré. La numérotation historique reste lisible dans l'ancien document.

## 6. Phase S : validation scientifique complète

La campagne finale doit mesurer **chaque module séparément**, avec contrôles et métriques dédiés, puis tester **l'architecture intégrée**. Les hypothèses H1 à H6, les batteries de tempérament, mondes/graines multiples, comparaisons de copies, ablations, vie longue (60 jours simulés selon protocole), erreurs causales, Brier, fausses mémoires, calibration, consolidation, sécurité et stabilité restent au programme.

Exemples de comparaisons obligatoires :

- Mémoire : tâches dépendant du passé, mémoire activée/désactivée et erreurs de rappel.
- Apprentissage : courbes indépendantes, contrôle sans apprentissage et calibration.
- Modèle causal : mondes à causes connues, interventions réelles, faux liens et superstition.
- Sommeil : consolidation activée/désactivée, rétention, stabilité et interruption.
- Exploration : couverture, bruit sans information utile, contrôle sans exploration.
- Métacognition : détection d'anomalies, coût logique, endurance longue.
- Ensemble : H1 à H6, variantes/ablations, cohérence, reconnaissance des profils et robustesse.

Cette liste complète les exigences scientifiques de la v1.2.1, elle ne les affaiblit pas. La phase S exige code et paramètres figés, préenregistrement antérieur aux données, séparation développeurs/évaluateurs, graines tenues hors de portée des développeurs, conservation des échecs et conclusions explicites pour chaque module. Elle peut se terminer par des résultats positifs, négatifs ou non concluants, jamais par une fausse certification.

## 7. Frontières et compatibilité

Cette version **ne modifie aucun algorithme cognitif**, aucune hypothèse de fond, aucun contrat, aucune interface, aucune règle d'accès à l'oracle ni aucun invariant applicable de la v1.2.1. Elle change seulement l'organisation des preuves et les conditions administratives de passage d'un stage.

Les sujets distincts comme la suppression éventuelle du rollback, des sauvegardes d'événements ou le statut de la mort exigent des décisions architecturales spécifiques et ne sont **pas approuvés implicitement** par cette proposition.

La spécification v1.2.1 reste inchangée et normative tant que l'opérateur n'a pas validé formellement le delta v1.3. Les branches et PR de développement actif ne sont pas modifiées par ce document. Le NO-GO scientifique antérieur du Stage 9 demeure en place.

## 8. Décision

**Adoption de cette politique v1.3 : EN ATTENTE DE L'OPERATEUR.**
**Signature, date et référence de décision : NON DEFINIES.**
