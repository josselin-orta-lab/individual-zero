# A2.30-H : préenregistrement de la divergence des états de départ

**15 octobre 2026 ; avant le code de l'analyse H.** Réanalyse externe sans exécution physique additionnelle. Sources scellées identiques à A2.30-G : huit vies A2.30-E, run #38715999434, artefact \`a230e-py3.11\`, SHA \`2be8008d51ad0d8a02d4795739a828acfba72aac\`. Résultat A2.30-G désormais connu **avant** ce préenregistrement : 121/121 recherches \`incomplete_model\` sans aucune première transition prédictible, 0 divergence BFS. Le travail ne compte pas de nouvelle naissance.

## Hypothèses spécifiques

- **H_missing_primitive** : certaines commandes candidates, notamment \`dormir\`/\`attendre\`, n'ont jamais été montrées dans le corpus prénatal. Les tentatives en refus sont qualifiées de \`unseen_command\` relativement au modèle courant, sans conclure que ces actions seraient utiles à manger.
- **H_exact_state** : une commande enregistrée est refusée à cause d'un \`SimulationState\` complet différent de l'exemple physique prénatal. Comparer l'état initial réellement accessible, avec ses champs (position, corps, inventaire, ressources locales, voisinage, nuit/shelter), à toutes les entrées physiques de **la même commande exacte**. Sous-classement facultatif des champs \`body.<variable>\`, \`inventory.<ressource>\`, \`adjacent.<direction>.<champ>\` pour rendre le problème inspectable.
- **H_temporal** : les refus de clés entraînées pourraient apparaître principalement **après** des transitions physiques et l'évolution du corps. Comparer les pas du monde sur lesquels le refus survient, sans déclarer cette concomitance causalement nécessaire.
- **H_projection** : une mauvaise projection ou une frontière sensorielle incorrecte ne peut pas être exclue par un simple écart de clés ; conserver \`unresolved\` faute d'un témoin physique indépendant.

## Protocole et anti-surinterprétation

Vérifier à nouveau les empreintes SHA du journal canonique, les identités et la chaîne indépendante à partir des fichiers A2.30-E, puis uniquement les **121 recherches** incomplètes et leurs appels à la racine. Recalculer l'empreinte d'entrée sur état accessible et commande ; vérifier \`known_exact_in_prebirth_corpus = false\` pour chaque refus et confirmer \`category\` par recherche exacte de la commande dans le corpus.

Pour les commandes déjà observées, rapporter une matrice de **différences descriptives** et le nombre de racines où chaque champ diverge d'un exemple le plus proche, choisi avec un ordre stable. Les écarts imbriqués ne doivent jamais être vendus comme une causalité, ni un modèle sûr de généralisation. Surtout, \`nearest_differing_fields\` de l'instrument A2.30-E utilise un ordre de sélection déterministe mais arbitraire : une différence de nourriture ne prouve pas qu'on peut effacer nourriture de la clé sans fausser la physique.

Comparer sous forme descriptive les refus par primitive, par profondeur (racine seulement), par profil et par pas physique, et le nombre de recherches avec/sans commande alimentaire candidate. Une absence d'arête alimentaire candidate peut résulter de préconditions accessibles non satisfaites, sans être une preuve de défaut algorithmique.

Les deux versions Python réanalysent exactement les mêmes données. Aucun apprentissage nouveau, inférence de transition, modification d'Equipment, du runtime, de Stage6, d'Oracle, de Stage9 ou de la norme. Rapport publié seulement après CI et contrôles négatifs. **A2.30 PARTIELLE, Stage12 PARTIAL, #110 OPEN.**
