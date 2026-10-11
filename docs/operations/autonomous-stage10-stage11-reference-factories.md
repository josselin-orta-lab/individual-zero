# Dépendances des fixtures de référence en mode autonome (MVP v1.3.1)

Le chemin cognitif `Stage2Runtime(..., autonomous_mortal=True)` ne charge plus
l'oracle ou le banc. Un verrou résiduel subsistait dans les *fixtures de
référence* : pour créer un Stage10 ou un Stage11, les constructeurs de
paramètres commençaient par bâtir des instances des Stages antérieurs avec
leur mode de laboratoire historique, créant brièvement Oracle/Bench.

Chaque constructeur de fixture Stage5 à Stage9 accepte désormais
`autonomous_mortal=False` par défaut pour ne pas invalider les anciens
résultats et peut propager `True` jusqu'au Stage4. Les fixtures Stage10/11
propagent aussi l'option à leurs dépendances préparatoires.

Ainsi, un opérateur peut construire **directement une véritable instance
Stage10/Stage11 autonome** sans même initialiser le banc ni l'oracle, ni
dans les étapes préalables de fabrication des configurations.

La physique, les paramètres de recherche, la mémoire et les décisions
cognitives restent identiques dans des mondes et conditions non mortelles
équivalentes. Des tests en processus neuf bloquent explicitement les trois
modules `lab.oracle`, `lab.bench` et `lab.evaluation_trace` pendant la
construction et l'exécution des deux Stages.

Cette modification concerne des **fixtures de développement**, et n'est pas
une promotion scientifique. Le NO-GO du Stage9 est inchangé.
