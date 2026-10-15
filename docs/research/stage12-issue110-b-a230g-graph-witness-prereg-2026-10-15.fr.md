# A2.30-G : préenregistrement d'un témoin de graphe indépendant sur les traces A2.30-E

**15 octobre 2026. Avant tout code A2.30-G.** Source immuable des données : GitHub Actions **#38715999434**, artefact \`a230e-py3.11\`, SHA de l'expérience \`2be8008d51ad0d8a02d4795739a828acfba72aac\`. La cohorte indépendante A2.30-E a déjà été exécutée : **8 vies, 192 pas réels, 141 recherches, 121 \`incomplete_model\`, 926 appels d'arêtes, dont 880 indisponibles**. Le présent travail **réanalyse** ces archives, sans créer de nouvelle naissance ni de nouveaux pas expérimentaux. Les données Python 3.12 servent seulement de répétition technique.

## Questions discriminantes

1. Parmi les 121 recherches incomplètes, combien ont **zéro transition disponible dès l'état initial perçu** ? Si toutes les commandes candidates initiales sont indisponibles, aucune trajectoire non vide ne peut être construite avec l'Equipment courant, à **tout horizon** (sous réserve que l'état initial ne satisfasse pas déjà l'objectif). Ceci démontre une frontière du modèle, **pas** que telle commande manquante est nécessaire physiquement, ni que l'objectif serait impossible dans le monde.
2. Pour les autres, à quelle profondeur apparaît la première arête indisponible ? Quelles familles de commandes sont concernées ? Une arête de déplacement non prédite n'est pas équivalente à une méconnaissance de \`manger\`.
3. **H3 : défaut de search / pruning.** Un BFS **indépendant, purement externe**, reconstruit la fermeture de l'ensemble des arêtes connues par leurs empreintes d'état et leurs commandes. Dans toute recherche épuisée (\`incomplete_model\`, \`not_found_within_horizon\`, \`partial_progress\`), les états réellement développés doivent être exactement ceux atteignables sur des préfixes connus à profondeur strictement inférieure à \`max_depth\`. Un désaccord est un suspect H3, **pas** une autorisation de changer un plan vécu.
4. **H2 / impossibilité.** Déclarer un sous-graphe clos seulement si **tous** les états atteignables ont effectivement été développés, toutes leurs commandes candidates ont une prédiction connue, et toutes les destinations restent dans l'ensemble observé. Une recherche bornée avec frontière inconnue reste **indéterminée**. Ne pas invoquer de vérité omnisciente.
5. **Provenance et non-régression** : les archives récupérées sont vérifiées par leurs identifiants de naissance, source SHA, ancrages de journal, empreintes de fichiers canoniques et audits de cohérence; aucune donnée nouvelle n'est introduite dans l'individu.

## Méthode

Télécharger **en lecture seule** l'artefact GH Actions \`a230e-py3.11\` via \`gh run download 38715999434\`, dans la CI déclenchée par la modification de cette étude, avec \`actions: read\` seulement. Échouer si nom du schéma, commit, identités, effectifs ou racines de journal ne correspondent pas. Pour chaque recherche dans les huit fichiers \`a230e-real-search-edges.json\` :

- utiliser exclusivement \`initial_state_sha256\`, \`candidate_states\`, \`depth_limit\`, \`edges\`, \`status\` et les observations d'états accessibles associées; ne pas invoquer le simulateur ni l'Oracle ;
- vérifier l'alignement de chaque arête avec une action candidate du même état, le statut de prédiction, la profondeur, les compteurs et les clés SHA ; reconstruire le graphe des transitions **réellement connues** ;
- utiliser un BFS indépendant avec priorité FIFO et \`visited\` sur l'empreinte des états ; distinguer recherche terminée de recherche censurée par un plan trouvé ;
- classer \`zero_known_first_step\`, \`some_known_first_step\`, \`unresolved_depth_or_unknown\`, \`complete_known_closed_graph\` et étiquettes de motif pour les arêtes manquantes. Ces classes représentent la **preuve du graphe du modèle**, pas une cause globale du comportement ni une responsabilité causale subjective.

## Critères

Toute divergence de graphe, empreinte de journal, statut ou cohorte est FAIL technique. Un résultat numérique (y compris zéro cas clos) est publié sans réinterprétation opportuniste. En cas d'absence des valeurs corporelles des successeurs dans A2.30-E, **ne pas prétendre reconstruire la satisfaction alimentaire ou exclure un défaut de \`target\`** : préenregistrer une capture de conséquence ultérieure strictement externe si nécessaire. Les tests unitaires distinguent graphe fermé, frontier inconnue, plan censurant une recherche et erreur de pruning.

**Aucun changement de runtime, Equipment, cognition, UC, subjectivité, Stage9, Oracle, M11, ni norme MVP v1.3.1.** Ne pas fermer l'issue #110 ni fusionner automatiquement les PR #184-#187; Stage12 PARTIAL jusqu'à réception opérateur.
