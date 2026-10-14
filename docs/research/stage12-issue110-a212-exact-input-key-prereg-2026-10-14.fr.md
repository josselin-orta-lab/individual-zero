# A2.12 : protocole préenregistré de diagnostic des clés Equipment

Date : 2026-10-14. Base main 461bc552fa20f95bcc59b6319e3e9050d9ea1036. Issue #110 ouverte. Stage12 PARTIAL.

## Question
Pourquoi l'ajout de transitions physiques prénatales dans A2.11b ne change-t-il aucune des 4 paires de vies ? L'hypothèse d'un décalage des empreintes complètes SimulationState x PrimitiveCommand est plausible, non prouvée.

## Instrumentation autorisée
Créer un auditeur externe en lecture seule qui, à partir des entrées effectivement soumises au simulateur, calcule l'empreinte canonique et la compare aux empreintes du corpus OFF/ON. Pour chaque refus, rapporter séparément commande absente, état différent, et champs divergents (position, corps, inventaire, localité, temporalité). Ne jamais injecter les résultats dans I0, ni lire les vérités cachées Oracle pour entraîner un modèle.

## Contrôles préalables
Les deux Equipment conservent leurs refus pour toute clé non apprise. Tester des états physiquement distincts, y compris ressources dangereuses ou non observées, sans déduire une équivalence sûre. Auditer provenance, coûts UC, journaux et mortalité. Comparer OFF/ON sur les mêmes huit vies, 42 pas maximum chacune. Un résultat négatif doit être conservé.

## Critères
T1 : métriques de clés réellement tentées, pas une extrapolation depuis incomplete_model. T2 : zéro fuite Oracle et aucune généralisation des conséquences inconnues. C3/C4 : exploration et ingestion réellement vécues, pas de proxy. C1/C2 : agence subjective indépendante des prédictions. C7 : reproduction technique sur deux Python ne vaut pas seeds indépendantes. C8 : aucune modification normative v1.3.1 ni changement du modèle par défaut.

La modification du prédicteur ne sera envisagée qu'après ce diagnostic et une analyse adversariale séparée. Stage12 ne peut être clos sans validation opérateur.
