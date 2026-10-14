# Stage12 #110 - A2.21 : contrôle d'intégrité par source perceptive scellée séparément

**Préenregistrement du 14 octobre 2026 avant code A2.21.** Base `main 71c44c9b1fe03853838938f8c3834e27ce1046e6`. A2.20 est fusionnée, Stage12 PARTIAL, issue #110 ouverte, MVP v1.3.1 inchangé.

## Question / modèle de menace

A2.20 prouve que l'audit sémantique des captures détecte une révision mensongère rechaînée, **à condition que les captures soient fiables**. A2.21 mesure les limites de cette hypothèse. Une garde *extérieure au registre candidat* scelle les captures, le jugement initial et la chronologie avant toute altération. L'attaquant peut reconstituer à volonté tous les SHA et les captures du **registre candidat**, mais pas modifier la garde indépendante scellée. L'authenticité vient de la séparation et de la chaîne de possession, **pas** de SHA-256 à lui seul. Si le registre et la garde sont compromis conjointement, la détection n'est pas garantie.

## Matrice prospective

Huit seeds 121–128, quatre histoires physiques par seed : origine du premier déplacement `normal` ou `confounded` (commande inhibée puis relocalisation extérieure) × suivi `stay` ou `passive` après une véritable commande `attendre`. Total **32 mondes physiques indépendants, 64 WorldBody.apply**, 16 relocalisations externes initiales et 16 déplacements passifs ultérieurs. Le premier jugement subjectif authentique est `self`. Les 16 mondes `passive` portent une seule révision prudente vers `unknown` en laboratoire, les 16 témoins `stay` n'en portent aucune.

Deux vues strictement séparées :
1. `sealed_source` : reçus de captures complets t1/t2/t3, jugement source exact et SHA des transitions, publiés par le banc **avant la construction du registre**. Les vérités `WorldBody.effects` sont conservées seulement côté évaluateur physique, non transmises au registre.
2. `candidate_ledger` : copie des captures autorisées, jugement initial, événements append-only et chaîne de SHA. Il ne lit ni cause physique ni labels de scénario. Références opaques distinctes des labels de condition.

## Attaques fixées avant expérimentation

- A1 : modifier une capture t3 du registre, réécrire l'événement de révision, recalculer tous les hachages. Le registre interne et son audit sémantique recalculé sur les **captures candidate falsifiées** peuvent accepter, mais la garde indépendante doit refuser.
- A2 : modifier ensemble le premier jugement et son origine dans le registre candidat, recalculer les chaînes : la garde doit refuser.
- A3 : substitution de la capture t3 d'un monde apparié `stay` par un monde `passive` avec rechaînage : garde doit refuser même si la structure est valide.
- A4 : rejouer un épisode complet, signé par son propre registre interne, sous le mauvais identifiant de vie et de scénario : garde doit refuser par liaison stricte d'identité.
- A5 : suppression du dernier reçu avec recalcul du head : garde doit refuser par cardinalité/temps attendu.
- A6 : permutation des observations t2 et t3 et rechaînage : garde doit refuser.
- Contrôles : chaque registre honnête doit passer l'audit du registre et l'audit séparé de la garde, sans faux refus (32/32).

## Critères

T1 exactement 32 mondes / 64 transitions; conditions appariées perceptivement égales jusqu'à t3 malgré causes initiales distinctes. T2 toutes les attaques effectivement exécutées et rejetées par la garde externe, pas seulement par l'auto-vérification. T3 au moins une attaque entièrement rechaînée acceptée par l'audit interne avec ses captures falsifiées et refusée par la garde, démontrant la valeur ajoutée du scellement indépendant. T4 reproduction CI Python 3.11/3.12, artefacts et hashes par monde. T5 zéro cognition I0 modifiée, zéro vie autonome, aucun UC/WAL/GA-06/Oracle/Stage9/normatif changé.

**Limites :** la garde reste celle du laboratoire et non une infrastructure indépendante de la machine. Son modèle de menace n'est pas la preuve d'authenticité d'un système adversarial complet. Tout déploiement doit détailler un propriétaire distinct, une preuve durable, l'atomicité WAL, la mortalité, les UC et l'accès cognitivement licite. Aucun jugement proximal ne prouve un résultat distal. Stage12 PARTIAL, #110 OPEN, réception opérateur non effectuée.
