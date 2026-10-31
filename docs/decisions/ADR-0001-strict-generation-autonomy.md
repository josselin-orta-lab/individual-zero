# ADR-0001 - Autonomie stricte des générations architecturales

## Contexte

**Décision explicite du responsable du projet, 31 octobre 2026. Statut : ACCEPTÉ (règle prospective).**

Individual Zero distingue les générations I0, I1, I2, etc. L'héritage de conception et les comparaisons scientifiques n'impliquent pas l'héritage d'exécution. Les modes historiques v1/v2/v3 du banc I2 ont été retirés par la PR #701. La compatibilité maintenue pour une architecture abandonnée multiplie les chemins, fragilise l'unicité du propriétaire d'état et fausse les preuves d'autonomie.

## Options considérées

- Continuer à importer les moteurs, Lab, propriétaires, adaptateurs et schémas de générations précédentes : **rejeté**.
- Conserver des modes de compatibilité/fallback pour exécuter de vieux états dans une nouvelle génération : **rejeté**.
- Développer chaque génération comme une architecture indépendante, en utilisant les précédentes uniquement pour la recherche et la comparaison : **retenu**.

## Décision normative

1. **Autonomie architecturale complète.** Chaque génération I(n) possède son code cognitif, son runtime, son Lab/WorldBody, son ordonnanceur UC, sa sécurité et son admission d'action, ses propriétaires d'état, sa mémoire, son journal/M11, ses schémas, ses identités de vie, ses tests, ses protocoles et ses documents normatifs. Aucun chemin d'exécution de I(n) ne dépend de l'installation, des imports ou du fonctionnement d'une génération antérieure.
2. **Aucun héritage implicite.** Un lien `parent` dans un manifeste désigne une filiation **historique et scientifique**, jamais une dépendance runtime. Sont interdits les imports de code d'une génération précédente, les fallbacks, la délégation à un ancien propriétaire, le partage de tables/états vivants, les anciens identifiants comme nouvelles identités et les politiques ou mémoires héritées.
3. **Pas de compatibilité obsolète.** Un nouveau moteur n'implémente pas des modes hérités destinés à faire fonctionner une architecture remplacée. Il refuse les anciens schémas et snapshots ; aucune migration silencieuse, conversion de naissance, récupération d'une vie d'une génération dans une autre, ni reprise postmortem. Une conversion hors ligne de données historiques éventuellement étudiée relève d'un outil de recherche isolé, jamais d'un chemin du moteur ni d'une réactivation.
4. **Réutiliser des idées, pas des dépendances.** Étudier les travaux antérieurs, copier puis adapter du code lors de la création d'une génération ou employer des utilitaires neutres sans propriétaire d'état reste possible, si les composants résultants sont **détenus et vérifiés dans la nouvelle génération**. Les utilitaires transversaux ne peuvent contenir de cognition active, de physique vivante, d'UC normative ni de journal canonique partagé. Une comparaison expérimentale entre moteurs exécute des individus distincts et isolés.
5. **Aucune rupture rétroactive d'une vie existante.** Cette décision s'applique aux **nouveaux développements et nouvelles générations**. I1 reste le moteur actif, avec ses identités persistées et ses contrats M11 propres. Son espace d'import `i1lab` est construit à partir de sources I1 et ne constitue pas un droit d'I2 à l'importer. Il est interdit de briser I1 ou une identité née pour supprimer une apparence de compatibilité.
6. **Un seul contrat courant par génération.** Les anciennes variantes d'un nouveau moteur sont retirées plutôt qu'entretenues comme chemins d'exécution parallèles. Le contrat courant doit disposer de ses propres tests positifs, tests de refus d'ancien schéma et tests de panne. Pas de GO scientifique déduit des seules vérifications logicielles.
7. **Vérification avant fusion.** Chaque PR touchant à un moteur identifie la génération et prouve l'absence d'import runtime intergénérationnel, de fallback obsolète, de propriétaire mutable partagé, de migration cachée et de dépendance de construction/exécution à une génération périmée. Le propriétaire et les tests de la génération doivent être indépendants. Les écarts bloquent la fusion ; les archives et comparaisons scientifiques restent consultables.

## Conséquences

- La duplication initiale de certains composants est acceptable lorsqu'elle garantit l'indépendance des générations ; simplifier ensuite **à l'intérieur** de la génération.
- Les archives I0/I1 et leurs résultats restent historiques, non prescriptifs pour les générations suivantes. L'autonomie ne supprime ni les citations, ni les comparaisons, ni les exigences de reproductibilité.
- I2 reste `PROPOSAL_ONLY`, non enregistrée et non exécutable. Cette ADR n'autorise ni naissance, ni moteur, ni promotion, ni reprise.
- Si un élément critique ne peut fonctionner sans I(n-1), l'implémentation de I(n) est incomplète : corriger cette dépendance, ne pas créer un adaptateur permanent.

## Portée et statut

**Toutes les générations futures, à commencer par I2. Accepté le 31 octobre 2026.**
Cette ADR fixe une règle d'ingénierie, pas une conclusion de science expérimentale. Toute dérogation exigerait une nouvelle décision explicite ; aucun fallback caché n'est autorisé.
