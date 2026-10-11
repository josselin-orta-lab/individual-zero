# Protocole logiciel Stage11 autonome sur 600 pas physiques

**MVP v1.3.1, développement public uniquement.** Ce diagnostic ne redémarre
ni Stage10 ni Stage11. Il exécute 600 décisions cognitives dans le monde
physique officiel du fixture Stage11, en mortalité irréversible, **sans
importer ni instancier** l'oracle, le banc ni les traces scientifiques.

Lancer :

```bash
python -m lab.stage11_autonomous_600_step_probe --steps 600
```

Une exécution produit une réception JSON préfixée
`stage11_autonomous_600_step=` et la CI complète conserve l'artefact.
Elle atteste structurellement le nombre de vrais pas exécutés,
600 captures perceptives, 600 transitions, 600 engagements autobiographiques,
les empreintes et le total du journal exhaustif, ses préfixes (pas 1/300/600)
et l'audit indépendant final. Aucun snapshot de vie passée, restauration,
masque de rollback, oracle ou EvaluationBench n'intervient.

Une mort ou une erreur interrompt et fait échouer ce **scénario de stabilité** :
elle ne déclenche jamais de tentative de résurrection ou de masquage du
résultat. Les morts dans d'autres scénarios restent des résultats valides.

Il s'agit **uniquement d'une hypothèse de bon fonctionnement logiciel**,
sans vérité physique attestée par une source externe, sans Golden et sans
validation scientifique définitive. Le NO-GO historique Stage9 demeure.
La validation par l'opérateur des stages et la campagne scientifique finale
restent requises.

Ce diagnostic dépend de la propagation `autonomous_mortal=True` à toutes les
fixtures de référence Stage5–Stage11 (PR #58).
