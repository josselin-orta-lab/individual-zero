# A2.30-N/O : consolidation chronologique de recherche externe

Date : 15 octobre 2026. Intégration des observations A2.30-N/O après #187 sur `main be9df8771ad493c5aafce5ec8339cdc551518dd5`, sans inclure les travaux déjà fusionnés dans #184–#187.

## Portée stricte
Seuls les onze fichiers N/O (deux workflows, quatre préenregistrements et résultats, trois scripts détachés, deux batteries de tests) sont repris de #188. Les triggers CI ciblent désormais `main`; un workflow O indépendant télécharge et audite les artefacts physiques originaux N du run #38726664498. Aucun changement `src/`, paramètres UC, WAL, Stage9, Oracle ou spécification v1.3.1.

## Validité scientifique
42 mondes d'apprentissage détachés et 62 mondes de test hors échantillon ont servi à comparer la table exacte, une enveloppe de 11 deltas visibles et l'abstention. L'enveloppe donne 54/62 prédictions disponibles, 28/28 couvertures nominales, mais manque 20 valeurs corporelles de toxicité/décroissance et 12 issues létales. Le statut de risque conserve `unknown_hidden_risk`; un proxy optimiste qui confond correspondance et sûreté ferait 18 fausses certifications. **Candidat laboratoire non déployable**, aucun I0 né dans cet essai, aucun gain de repas démontré.

Les versions Python 3.11 et 3.12 répètent les mêmes mondes. A2.30 et Stage12 restent PARTIAL ; #110 reste ouverte. Ne pas interpréter `confidence=1.0` comme sécurité. Ne pas modifier, fusionner ou inclure indirectement la PR #199.

## Validation exigée
Deux jobs N physiques + deux jobs O archivistiques sur la tête exacte de #188 ; contrôle du `main` réel après fusion, tests de séparation du modèle, absence de régression Stage6 et Stage9. Toute anomalie bloque la fusion.
