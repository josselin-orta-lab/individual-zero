# A2-R : vérification bornée d'une revue d'environnement (30 octobre 2026)

Tranche de validation **pure**, sans naissance, sans workflow de cohorte et sans changement du moteur I1/I0.

L'outil `tools/research/i1_a2r_environment_review.py` vérifie un *instantané normalisé* de quatre sources distinctes : run GitHub, configuration de l'environnement, décision de revue et jobs associés. Il rejette la revue absente, ambiguë, autorisant l'auto-approbation, étrangère au run/à sa tentative, ou les jobs extérieurs à l'environnement attendu.

**Limite technique :** l'entrée `approvals` est une représentation normalisée proposée pour un futur collecteur indépendant, **pas** le schéma brut garanti d'un endpoint REST GitHub. Ce composant ne réalise aucune requête réseau, ne prouve ni la véritable origine GitHub des objets ni la configuration effective des règles de protection, et ne délivre **aucune autorisation de lancement**. La connexion à un collecteur API authentifié et à un registre de revue externe immuable reste à implémenter et auditer avant toute utilisation en production.

Le workflow de cohorte `i1-a2r-confirmatory-one-shot.yml` demeure absent. Deux tests ciblés Python 3.11/3.12 vérifient uniquement le contrat de refus. A1-C NO_GO, A2-R NOT_EXECUTED 0/96, L3 NOT_ESTABLISHED.
