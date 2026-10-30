# A2-R : assemblage des 96 originaux, sans naissance

La présente tranche raccorde le protocole A2-R au garde d'archive de la PR #631. L'assembleur exige les 96 répertoires correspondant aux identités et à l'ordre déterministes, préserve les octets originaux du journal M11 et des rapports, conserve toute naissance échouée et refuse toute omission, substitution, deuxième tentative ou archive déjà existante. Le verrou source/run et son empreinte doivent provenir d'une source extérieure au spool.

La sortie inclut un **SHA-256 à publier indépendamment** : elle n'est pas encore scellée extérieurement. Même une archive complète ne suffit pas : il manque l'audit froid de toutes les trajectoires M11, l'attestation du run réellement exécuté, la preuve comparative et les critères statistiques. Toute archive échouée reste MEASUREMENT_BLOCKED. Aucun moteur I1/I0 modifié, aucune vie H192 lancée, aucune CI naturelle lourde.

Ce composant est un outil de conservation et d'analyse postérieure, pas un lancement automatique. A1-C NO_GO, A2-R NOT_EXECUTED, L3 NOT_ESTABLISHED.