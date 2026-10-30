# A2-R : auditeur froid de recevabilite M11, tranche scientifique L1

**30 octobre 2026.** Contrat gelé A2-R : `docs/research/I1_ECO_A2R_REWARD_PREREGISTRATION_2026-10-30.md`. A1-C reste NO_GO et L3 reste NOT_ESTABLISHED.

## Périmètre effectivement implémenté

`tools/research/i1_a2r_m11_cold.py` est un lecteur **hors moteur et en lecture seule**. Il ne crée pas de nouvel individu et ne modifie ni Q, ni récompense, ni Action Control. Il s'appuie sur `SQLiteLifeLedger.audit_read_only` et sur le lecteur de chaînes M11 existant. Il contrôle l'identité, les chaînes cryptographiques canoniques, le hash de l'état courant, le registre d'un propriétaire Value/Needs unique, la version réelle de récompense et le marqueur de recherche du propriétaire, plus le contrat M11 du constructeur. Il reconstruit les commandes physiquement expérimentées, la continuité du corps, la fin de vie et les contributions de récompense calculées sur les états réels.

Pour les événements nativement publiés, il vérifie le retour TD `return_g` contre les transitions physiques du segment, les correspondances Stage8/Competition et l'admission d'une option effectivement proposée. Il détecte les duplications, les pertes d'événements et les différences entre preuves de Q et preuve motrice. Le précontrôle apparié signale les divergences physiques survenues **avant** la première différence de récompense, sans considérer une différence de reward comme une différence de politique ni comme un résultat adaptatif. Un test à horizon court est uniquement un témoin logiciel, exclu des 96 vies.

## Limites scientifiques explicites

Ce livrable **ne reconstitue pas encore les douze composantes des poids Q de A2-R à horizon 192**, et n'établit pas le passage causal complet TD → Q modifié → Stage8 → Competition → commande différente. Il ne mesure pas non plus seul la fréquence d'exposition exigée par le préenregistrement. Les champs `full_q_replay_verified` et `mechanism_exposed` sont donc volontairement `false`. **Il serait incorrect de transmettre directement cette sortie au verdict confirmatoire**, même si les contrôles M11 de base réussissent.

Le lecteur ne vérifie pas à lui seul les 96 ZIP contre un manifeste SHA-256 externe ni l'empreinte source préenregistrée pour une cohorte jamais née. Ces portes restent indispensables avant toute exécution.

## Validation et règle CI

Tests ciblés : `tools/research/tests/test_i1_a2r_m11_cold.py`. Vérification de la formule native et de la formule déficit, des valeurs M11 IEEE-754, du contrat propriétaire et de refus adversariaux (TD falsifié, Competition discordante, continuité physique cassée, décès mal attribué, ordre d'événements incohérent, divergence prématurée). Workflow limité aux tests purs Python 3.11/3.12. Aucun chemin `src/i1/**`, `src/i0/**` ni `tests/i1/**` modifié. Aucune CI naturelle lourde ni campagne 96 vies.

**Statuts :** A2-R PREREGISTERED, naissance expérimentale L1 issue de #626, auditeur M11 partiel seulement; A2-R NOT_EXECUTED; L3 NOT_ESTABLISHED. La prochaine porte est le rejeu numérique complet Q/TD avec état/objectif véritable à H192, incluant les trajectoires terminales, et un manifeste de provenance scellé avant la première naissance.
