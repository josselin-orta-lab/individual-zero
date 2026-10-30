# A2-R : verrou de provenance des runs GitHub Actions, sans naissance

30 octobre 2026. L'auditeur hors moteur compare des données reçues **indépendamment** de l'API GitHub : workflow, chemin, dépôt, HEAD, arbre Git, run ID, numéro de tentative, historique des dispatchs, statut et verrou externe SHA-256. Le workflow confirmatoire réservé n'est **pas créé ni déclenché** ici.

Une première tentative unique dans l'API n'établit pas une unicité historique immuable : des runs peuvent être effacés. Le journal de verrou extérieur, la préservation des artefacts, l'authentification du code réellement exécuté et l'audit complet M11 sont encore nécessaires. L'auditeur retourne obligatoirement `immutable_once_only_guaranteed=false`, `runtime_executed_source_independently_proven=false`, `study_admissible=false`. Il n'autorise aucune exécution et ne revendique aucun GO.

Tests ciblés Python 3.11/3.12, scénarios de provenance falsifiée, source/fork non concordants, relance, tentative 2, état incomplet et résultat négatif. Aucun changement I1/I0. A1-C NO_GO ; A2-R NOT_EXECUTED ; L3 NOT_ESTABLISHED.
