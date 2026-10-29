# Individual Zero I1 — A1-C : préenregistrement confirmatoire L3 ciblé

Date de préenregistrement : 29 octobre 2026, AVANT toute naissance A1-C.
Références descriptives : A1-P GitHub Actions #40938021102, lecteur indépendant #40939448759, protocole A1-P et issue #304. Les huit anciennes vies n'entrent JAMAIS dans l'estimateur A1-C.
Ce document constitue un contrat figé : un échec ou un résultat négatif NE permet ni une extension de N, ni un changement de métrique, ni un ajustement d'I1.

## Question, effet et portée

H1 : les lectures des valeurs TD apprises par I1 au cours de sa propre vie réduisent la charge des déficits physiologiques sur les 48 pas, comparées à un témoin à lecture TD masquée dont les mises à jour TD ont TOUJOURS lieu. Le laboratoire conserve l'eau et deux baies aux effets physiques invisibles, avec échange des rôles nutritifs. Les commandes demeurent autonomes; aucune mémoire, récompense, option ou action forcée.

Ce protocole ne valide que le **L3 ciblé TD dans un environnement contrôlé**. Il ne constitue pas une validation du L3 général, de l'ensemble de la mémoire autobiographique, de la consolidation Stage10, ni de la conscience. A2 devra tester la généralisation hors laboratoire.

## Unités, taille fixe et provenance

12 sources de tempérament **nouvelles** : entiers de 101 à 112 inclus, source déterministe i1:research-twin:eco-a1-confirmatory:<seed>. Ces sources ne sont pas celles d'A1-P (1 et 2).
Chaque tempérament passe dans 2 rôles physiques (native, reversed), et chaque rôle dans 2 bras indépendamment nés (canonical, td_read_masked).
Donc **12 blocs indépendants de tempérament × 2 rôles × 2 bras = 48 vies, 24 paires**, horizon maximal 48 pas chacune. Les paires qui partagent un même tempérament dans les deux rôles NE sont pas des réplicats indépendants : l'inférence porte sur les **12 moyennes de blocs**.

Les identités M11 sont toutes différentes et opaques, avec affectation préalable pseudo-aléatoire, reproductible et équilibrée à l'intérieur de chaque paire selon SHA-256 de la chaîne publique i1-a1c-identity-v1|role|seed. Cette affectation est définie AVANT les résultats. Le moteur et les états TD à la naissance sont identiques dans une paire, hormis son identité M11; chaque vie conserve un WAL/M11 distinct et ne reçoit aucune mémoire d'autrui. Aucun rerun, même en cas de mort ou d'incident.

L'expérience et les 48 archives ont UNE seule provenance source SHA; l'agrégateur relit froidement les journaux SQLite M11 de cette même provenance. Les mondes proviennent sans changement de a1_world_parameters de A1-P, y compris la normalisation physiologique native de la baie toxique AVANT permutation. Les deux rôles sont invisibles à la perception. Ne pas modifier WorldBody, Q/TD, sommeil, priorités, UC, compétences, expériences ou conditions de naissance en fonction des résultats.

## Critère principal, fixé avant résultat

Pour chaque vie : S = deficit_area_total / (4 × 48), score dans [0, 1] construit sur les quatre besoins, avec pénalité post-mortem aux pas restant après décès, exactement comme ECO-v1. Un S faible est meilleur.
Pour chaque rôle et chaque seed : D = S(td_read_masked) − S(canonical). D positif est favorable à I1.
Pour chaque source seed : B(seed) = (D(native, seed) + D(reversed, seed)) / 2.
Estimateur principal : moyenne de B sur les 12 sources, **sans inclure A1-P**.

Critères simultanés pour un candidat « L3 TD ciblé confirmé en laboratoire » :
- Les 48 vies et 24 paires existent sur le même source SHA; **48/48 audits froids M11**, appariment exact des naissances, provenance / événements / état physique validés, aucun incident de mesure non résolu. Aucune sélection des survivants.
- Avant la première lecture TD masquée, les préfixes physiques des deux membres sont identiques. Pour chaque rôle, **au moins 9/12 paires** démontrent : lecture TD réellement apprise dans le témoin et masquée, option réellement passée dans Stage8/Competition avec une alternative physiquement disponible, puis une commande physique différente après l'intervention. Toutes les 24 paires restent incluses dans l'estimation, même non exposées.
- La moyenne des 12 B est **au moins +0,0100** (différence absolue de 1 point de pourcentage de charge de déficit), le **borne inférieure de l'IC t bilatéral 95 % sur les 12 blocs est strictement > 0**, et la sensibilité par permutation de signes des 12 blocs donne **p unilatéral ≤ 0,025** (4096 combinaisons exactes, sous l'hypothèse de symétrie nulle). L'IC t est une approximation paramétrique; le p de signes n'est PAS présenté comme une randomisation parfaite des 48 vies.
- Les moyennes D sont **strictement positives dans chaque rôle**, et **au moins 8/12 paires** de chacun des deux rôles ont D > 0. Les contre-exemples et dommages sont toujours publiés, sans exclusion ni « suppression » de seed.

Cette conjonction est **un seuil de décision exigeant, choisi avant les données**, et non une calibration rétroactive sur les huit anciennes vies. Les deux sources d'A1-P étaient insuffisantes pour estimer de manière fiable une variance des 12 blocs, donc N=12 blocs n'est **pas** une garantie de puissance pour un bénéfice faible. Si le résultat est insuffisant, le verdict est NO_GO ou INCONCLUSIVE, pas « preuve de non-apprentissage ».

## Analyses secondaires, hors sélection de GO

Par rôle et par seed : état terminal et décès/censure; 4 déficits par besoin; sommeil, collecte, ingestion et hydratation; identité vraie de la baie bénéfique, consommation toxique; première mise à jour TD; première lecture masquée; premier changement Stage8, Competition, commande et conséquence corporelle. Exposer le nombre de paires sans vraie concurrence ou jamais exposées; préciser que les flottants Q avant masque restent des observations externes, même après rapprochement avec M11.
Aucune conclusion de supériorité de Stage10, de causalité des souvenirs autobiographiques ou de généralisation à d'autres mondes.

## Verdicts sans rattrapage

- INVALID_EXPERIMENT / MEASUREMENT_BLOCKED : naissance ou journal incohérent, source non gelée, une vie absente, altération d'identité, différence physique antérieure à l'intervention ou preuve M11 insuffisante. Jamais réparer en recréant un individu; audit technique en lecture seule autorisé.
- NOT_EXPOSED : preuve d'exposition au TD apprise insuffisante, selon la condition 9/12 par rôle; les résultats physiologiques sont publiés sans GO.
- NO_GO : conditions statistiques ou robustesse des rôles non remplies, même en présence d'un signal ponctuel.
- CONFIRMATORY_TARGETED_SIGNAL_PENDING_REVIEW : tous les seuils atteints, mais examen humain indépendant de la chaîne d'attribution requis avant de déclarer un L3 ciblé.

Aucun statut n'autorise de déclarer le **L3 général**. Le prochain A2 doit être préenregistré séparément et tester la généralisation à de nouvelles cartes/ressources/horizons, sans ré-optimiser I1 à partir de A1-C.

## Politique CI et archivage

Tests ciblés de l'opérateur/statistique/lecteur et tests M11 adversariaux AVANT les naissances. Une seule validation globale du moteur si une modification du moteur le justifie, non une CI lourde à chaque micro-correction. Workflow de naissance A1-C déclenché UNE seule fois sur un commit final gelé, tentative 1, archives immuables et manifestes SHA-256. Séparer les SHA de génération des données et de tout lecteur ultérieur. Rapports agrégés, y compris erreurs, toujours conservés.
