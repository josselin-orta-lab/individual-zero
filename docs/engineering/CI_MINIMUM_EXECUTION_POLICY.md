# Règle normative : limiter les CI au strict minimum utile

**Décision explicite du 29 octobre 2026**, campagne scientifique Individual Zero I1, issue [#304](https://github.com/josselin-orta-lab/individual-zero/issues/304). Cette règle s'applique aux agents de développement, aux travaux scientifiques et à l'évolution des workflows, sans diminuer la couverture des tests nécessaires.

## Principe obligatoire

**Ne pas lancer de CI lourde sans justification technique réelle.** La fréquence, le coût et la portée des validations doivent être proportionnels aux fichiers et invariants réellement modifiés. Éviter les exécutions redondantes, les relances sur chaque micro-commit et les vérifications longues sur des artefacts documentaires ou des outils d'observation.

1. **Documents, descriptions, rapports, commentaires, ajustements purement observateurs** : aucune CI naturelle complète automatique requise. Un contrôle de diff/syntaxe ou des tests ciblés suffit quand le contenu est exécutable.
2. **Outils scientifiques, agrégateurs, lecteurs M11, harnais d'expérience sans changement du moteur** : tests unitaires et adversariaux ciblés, audits à froid sur archives authentiques, CI scientifique légère dédiée si nécessaire. Les huit vies A1 ne doivent jamais servir de tests de routine.
3. **Moteur I1, code générateur, apprentissage Q/TD, physiologie, Action Control, UC, persistance M11, sécurité, isolation I0, interfaces ou contrats partagés** : exiger les tests et non-régressions pertinents. Une validation naturelle I1 complète Python 3.11/3.12 est réservée à la **tête stabilisée** avant fusion, pas à chaque itération intermédiaire.
4. **Regrouper les corrections** : tester localement pendant l'édition, préparer un lot cohérent, puis pousser une tête vérifiable. Ne pas multiplier les commits ou PR pour redéclencher des tests identiques. Ne relancer un workflow échoué que si un correctif ou une cause externe vérifiée le justifie.
5. **Traçabilité** : consigner la raison de toute CI lourde, le SHA exact, le périmètre concerné et le résultat. Un succès sur un ancien SHA ne certifie pas le nouveau SHA. Une validation partielle, annulée ou non exécutée n'est pas un succès.
6. **Filtres de workflow** : lorsqu'une règle GitHub Actions déclenche une CI lourde pour une modification sans impact moteur, corriger les filtres/déclencheurs dans un changement dédié, préserver les contrôles obligatoires et vérifier la couverture effective. Ne pas contourner les règles de protection des branches ni désactiver de tests pour obtenir artificiellement un statut vert.

### Fréquence attendue

- À chaque modification : **contrôle le plus petit qui puisse détecter la régression concernée**.
- À la fin d'une tranche scientifique : validation de l'instrument sur des traces M11 réelles et adversariales.
- Avant fusion d'une tranche modifiant le moteur ou exigeant les garanties intégrales : **une seule campagne complète sur le SHA final**, recommencée seulement si le nouveau contenu peut invalider la preuve précédente ou si les règles de protection l'exigent.
- Après fusion : pas de nouvelle CI lourde simplement pour répéter une validation déjà authentifiée, sauf nécessité justifiée.

## Garanties non négociables

La réduction des CI ne doit **jamais** supprimer la vérification pertinente de la mortalité, de M11, des UC, des protections, de la parité des sources ou de la non-régression I0. Elle supprime les exécutions **inutiles**, pas les preuves nécessaires. Toute affirmation scientifique doit rester liée aux journaux et aux commits effectivement audités.

**État technique à la date de la décision :** cette règle est normative; elle ne change pas automatiquement les déclencheurs actuellement codés dans `.github/workflows/i1-current-ci.yml`. Tout resserrement de ces déclencheurs doit être réalisé et vérifié explicitement, en évitant d'introduire une lacune de couverture.
