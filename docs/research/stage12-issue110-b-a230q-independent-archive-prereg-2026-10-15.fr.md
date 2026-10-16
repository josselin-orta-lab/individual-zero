# A2.30-Q : préenregistrement de l'audit hors ligne indépendant des preuves P

**15 octobre 2026, après résultats P, avant le code d'audit Q.** Source déjà connue et figée : [run GitHub Actions A2.30-P #38730415503](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38730415503), code source **`3ab03a90b38d6c968cddcd9ed699c3f089d0544c`** ; artefacts `a230p-py3.11` et `a230p-py3.12`. L'accord entre deux Python est connu **avant** l'audit ; ne pas le présenter comme une nouvelle cohorte. Fichiers d'origine identiques octet par octet, SHA-256 complets vérifiés avant codage Q :

- `a230p-training-manifest.json` : `f706cd25a31b8f716c4bb0a5a7e617bed87c0b8b47577d8b9dd31221cf23839e`.
- `a230p-heldout-physical-results.json` : `570713d9a44c55a13482dba3d5e9b2f8095df8ba8f487f22d5aa917db8bc3514`.
- `a230p-summary.json` : `45167e3bd7be3827f2839208aa8bfe2e316e6b4f110106b94d68bf32a3fea0e0`.

Ces empreintes ne prouvent **pas** physiquement ce qui s'est passé dans le monde ; elles ancrent la cohérence des données enregistrées. Un recalcul sans simuler de nouvelles actions ne constitue pas une réplication physique supplémentaire.

## Tâches indépendantes strictes

1. Télécharger exclusivement les deux artefacts originaux du run précité ; comparer les **trois JSON octet à octet** et aux SHA-256 ci-dessus. Rejeter toute ambiguïté de chemin, tout identifiant de monde répété, faux pas physique, ou partage entraînement/test. Contrôler 48 mondes et 132 pas d'entraînement, 80 mondes et 220 pas de test, cumul 128/352. Les preuves émanent de `EquipmentCorpusRecorder` et du runner P ; un témoin JSON seul **ne valide pas indépendamment WorldBody.apply**.
2. Sans importer le module du prototype P ni son runner ni aucune API de prédiction, reconstituer **autrement** les contextes accessibles (première commande, préconditions visibles et préfixe exact) et les 11 deltas cumulés des états `SimulationState` consignés pour chaque monde. Reconstruire le SHA des exemples enregistrés, le chaînage `after_i == before_(i+1)`, le nombre d'étapes, la terminalité finale et les branches conjointes de l'entraînement. Toute transition après mort => FAIL.
3. Recalculer les quatre trajectoires distinctes et le pas terminal par contexte, avec flottants arrondis à 1e-8 **uniquement pour la suppression des erreurs de représentation**, et comparer **chacune** des 80 prédictions publiées par P aux branches issues exclusivement des 48 mondes d'entraînement, aux comptes de support et aux étiquettes `observed_terminal_possible` / `unknown_hidden_risk`. Le label `safe` est toujours interdit. Mesurer 48/48 correspondances ID, 24/24 traces OOD nouvelles et 8/8 abstentions comme **hypothèses connues à vérifier**, pas comme résultats indépendants nouveaux.
4. Contrôles de falsification : altération du SHA d'un exemple, fausse terminalité, pas ajouté après terminal, invention d'une branche dans un contexte vide, promotion `certifies_safe=true`, modification du nombre de mondes et contamination entraînement/test **doivent provoquer FAIL**.
5. Confirmer la **portée** : un catalogue de branches finies n'est pas un ensemble complet des résultats possibles. Un danger physique non entraîné n'est pas détecté par la forme de ses conséquences ; aucune probabilité de mortalité, capacité alimentaire vécue ou responsabilité causale subjective n'est démontrée.

**A2.30-Q = relecture sans nouvelle naissance, sans pas physique additionnel, sans Oracle, sans aucun effet sur Stage6/Stage9/Stage12 ou norme v1.3.1.** Verdict PASS uniquement si tous les recalculs et contrôles négatifs sont verts, sinon documenter le blocage sans modifier rétrospectivement P.
