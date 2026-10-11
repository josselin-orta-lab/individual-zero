# Stage 11 : procédure de validation par l'opérateur sur 600 pas

**Document opératoire, 11 octobre 2026.** Ce document sépare la complétion **logicielle** du Stage 11 de son **acceptation par l'opérateur** dans le MVP révisé. Il ne remplace pas la spécification anglaise normative v1.2.1 actuellement versionnée dans le dépôt et ne prétend pas fournir une validation scientifique absolue. La validation scientifique séparée de tous les modules reste une tâche de fin de projet. **Stage 9 conserve son NO-GO scientifique.**

## Conditions avant séance

1. Indiquer le **SHA de code exact**, les versions du programme, de Python, des configurations de physique, de tempérament, des budgets P-43 et des politiques de sécurité. Vérifier la CI correspondante et ne pas attribuer à ce SHA les résultats d'un commit précédent.
2. Choisir et enregistrer **avant l'exécution** le monde réel/simulé, la graine, les règles du monde, les contraintes, le mode de sécurité et le nombre **600 de pas physiques**. Ne pas sélectionner rétrospectivement une graine favorable.
3. **Point d'architecture à résoudre avant acceptation définitive :** le code fondé sur la spécification anglaise v1.2.1 comporte toujours un rollback létal. La décision de projet plus récente prévoit une mort définitive et l'absence de rollback, sans neutraliser les conséquences physiques du monde. Ce changement doit être formalisé et implémenté séparément avant qu'une séance ne certifie la future architecture. Ne pas déclarer que le rollback est absent tant qu'il est présent dans le code exécuté.
4. S'assurer que la provenance des observations est réelle et locale, que les informations du banc/oracle restent extérieures à l'individu, et que les journaux restent horodatés et signés par leurs SHA. Un observateur peut accéder à la vérité du monde pour **évaluer**, jamais pour instruire l'individu.
5. Ne pas modifier l'état corporel ni effacer des événements pendant l'essai pour prolonger artificiellement la vie. Si une mort définitive survient avant 600 pas, **enregistrer la terminaison effective**, pas une prétendue séance de 600 pas complète.

## Exécution minimale proposée

- Lancer un exemplaire neuf de l'individu avec le monde, les budgets et les entrées déclarés. Observer les pas 1 à 600 si l'individu reste en vie. Capturer les états complets aux pas **1, 300 et 600** uniquement si ces pas sont atteints. Conserver observations locales, décisions envisagées, actions envoyées et réellement exécutées, états du monde, budgets UC, événements causaux et profils de modulation. Les identifiants d'observation physique et de signaux intrinsèques ne doivent pas se dupliquer dans une même décision.
- Enregistrer explicitement les passages en `normal`, `exploration`, `threat` et `recovery` lorsque leurs **conditions observables** sont réunies. L'absence d'un profil faute d'événement déclencheur n'est pas en soi une régression. La récupération après intervention externe n'est pas comptée comme repos autonome.
- Décrire les sites réellement visités, les impasses et les détours, ainsi que les intérêts informationnels qui ont motivé une action réellement exécutée. Les propositions, simulations et intérêts isolés ne doivent pas être comptés comme visites ou apprentissages.
- Vérifier l'absence de crédit d'information dû à une prévision non vérifiée, à une vérité cachée ou à un test purement simulé ; vérifier le respect des enveloppes de calcul y compris lorsque le budget est nul ou dégradé.
- Rejouer **indépendamment la même configuration et les mêmes entrées**, avec un calendrier de captures identique. Comparer les journaux canoniques, propriétaires causaux, identifiants des captures et SHA. Si la reproduction en conditions physiques réelles ne peut être strictement déterministe, enregistrer cette limitation au lieu d'inventer une preuve exacte.
- En cas de terminaison ou de blocage, conserver la cause, le pas et le dernier état causal. Ne pas faire disparaître la preuve par restauration silencieuse.

## Critères de décision humaine

| Décision | Condition |
| --- | --- |
| **GO opérateur** | La couverture logicielle normative de Stage 11 est démontrée sur un SHA exact, le protocole de 600 pas a été réellement exécuté ou sa terminaison légitime est correctement caractérisée, les comportements mesurés sont jugés conformes par l'opérateur, et les écarts d'architecture (en particulier mortalité/rollback) ont été résolus. |
| **NO-GO opérateur** | Invariant violé, provenance non fiable, décès traité contrairement au mode déclaré, divergence inexpliquée de relecture, comportement jugé insuffisant, ou modification rétrospective du protocole. |
| **EN ATTENTE** | Tests logiciels passés mais absence de séance en conditions réelles, absence de verdict explicite de l'opérateur, ou migration de mortalité non encore intégrée. |

Le verdict de l'opérateur doit comporter : **GO / NO-GO / EN ATTENTE**, date, SHA, version de physique, identifiants de la séance, les preuves et les réserves éventuelles. **Sans décision explicite GO de l'opérateur, ne pas étiqueter Stage 11 comme officiellement terminé.**

### Distinction des preuves

- La CI Python 3.11/3.12 et les tests de 600 pas publics établissent au mieux des **hypothèses logicielles** et des invariants reproductibles dans des conditions contrôlées.
- Une séance opérateur en conditions réelles juge l'**aptitude de Stage 11**, non les preuves scientifiques définitives de chaque module.
- La campagne scientifique indépendante de fin de projet, les Goldens, les preuves du Stage 9 et l'acceptation du Stage 10 restent strictement séparés.

**Aucun changement de `main`, aucune fusion de la PR #25, aucun changement des protections du dépôt ni du texte normatif anglais v1.2.1 n'est autorisé par ce document.**
