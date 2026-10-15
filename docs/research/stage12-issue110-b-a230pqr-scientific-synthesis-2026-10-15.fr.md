# Individual Zero : synthèse scientifique A2.30-P/Q/R, ensembles de conséquences et risques différés

**15 octobre 2026, bilan après preuve physique et trois CI.** Branche : `science/stage12-b-a230p-multiconsequence-delayed-20261015`, PR [#189](https://github.com/josselin-orta-lab/individual-zero/pull/189), empilée sur #188, #187, #186, #185 et #184. `main` n'est pas modifiée. La norme `docs/architecture/reference/en/mvp-specification-v1.3.1.md` et toutes les décisions de Stage6, Stage9 et Stage12 restent inchangées.

## Résultat positif réel mais circonscrit

L'expérience P [run #38730415503](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38730415503) démontre la possibilité **technique** de conserver, hors I0, un ensemble de **12 branches de trajectoires conjointes physiquement observées** (quatre branches par préfixe MOV/EAT/WAIT), y compris les décès après deux ou trois pas. Les **48/48** transitions de séquences ordinaires sur de nouveaux états observables sont reconnues par les branches entraînées; **8 décès différés** ont une temporalité qu'un témoin strictement premier pas ne peut attester. Ce n'est pas une preuve statistique générale d'exactitude ou de sûreté.

## Limite négative irréductible par ce protocole

**24/24** variantes à conséquences physiques cachées inédites ne sont présentes dans aucune branche du même contexte observable, et **8** terminent à un pas absent de l'ensemble empirique. Un modèle ne peut certifier exhaustivement des événements qui demeurent physiquement compatibles avec des observations identiques et n'ont jamais été vécus. Le prototype maintient **zéro** certification `safe`, refuse les **8** contextes/prefixes inédits, mais la gestion des risques inconnus reste une **abstention de certitude**, pas une prédiction de danger. En général, garder la liste des risques déjà observés ne prouve pas qu'une action sans risque observé soit sûre.

## Validations complémentaires

A2.30-Q [run #38731532528](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38731532528) réimplémente **sans modèle ni runner P** la projection et le calcul des 80 scores depuis les deux archives SHA-256, avec contrôles négatifs de falsification. A2.30-R [run #38732185501](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38732185501) rejoue **avec un code physique distinct du runner P** les 128 mondes, en réappliquant 352 transitions aux conditions originales, et confirme **zéro divergence physique**. Les répétitions R sont **techniques**, non de nouvelles conditions scientifiques indépendantes. Les CI Python 3.11/3.12 ont les mêmes résultats, pas des graines indépendantes.

## Conséquences architecturales et choix opérateur ultérieur

Le modèle P n'est pas un `EquipmentModel`. Il ne peut **pas** fournir les `SimulationState` futurs complets requis par `Simulator`, ni construire un plan alimentaire exécutable ou justifier une décision de sécurité. Le raccorder directement à Stage6 pour remplacer `FrozenTableEquipment` serait trompeur et probablement dangereux. L'absence de conséquence cachée parmi des branches observées n'est jamais un certificat.

**Prochaine priorité scientifique proposée A2.30-S**, sans autorisation de déploiement implicite : (i) formaliser un contrat « conséquences possibles connues / causes cachées non exclues / inconnue » avec une séparation de risque terminal immédiat et différé; (ii) étudier les **informations activement observables** qui pourraient discriminer les dangers sans Oracle (préconditions réelles, observations autorisées, effets corporels déjà vécus), et les coûts/risques d'acquisition de ces observations; (iii) tester une politique de planification **en shadow mode seulement**, sans envoyer d'actions ni modifier les jugements subjectifs; (iv) décider avec l'opérateur si une révision normative de l'Equipment/Stage6 est justifiée. Éviter d'augmenter l'horizon ou de libérer un `confidence=1.0` comme preuve de sûreté.

**Décision : A2.30 PARTIELLE, validation technique P/Q/R PASS, modèle expérimental en NO-GO cognitif, Stage12 PARTIAL, issue #110 OPEN, PR #189 DRAFT non fusionnée.** La validation opérateur de Stage12 et la science finale du projet restent ultérieures.
