# A2.30-ZR : préenregistrement d'une relecture physique indépendante des scénarios Z

**15 octobre 2026, après résultats Z et ZI, AVANT code ou exécution ZR.** Origine physique : [Z run #38760713470](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38760713470), code immuable \`0d9fd7cd511640103498f037b84cae915169356e\`, **168 mondes/244 applications WorldBody.apply**. Audit autonome de fichiers ZI : [run #38762136606](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38762136606), PASS sous Python 3.11 et 3.12 : 17 contrôles négatifs par version, tous les comptes confirmés et 80 premières arêtes Stage6 exactes inconnues.

**Limite de ZI déjà établie :** un fichier de reçus ne démontre pas, à lui seul, la vérité de l'application physique par \`WorldBody\`. ZR est une validation **technique** utilisant de nouvelles instances de \`WorldBody\` et un runner reconstruit **indépendamment** du runner Z. Les scénarios répètent exactement les mêmes cellules déterministes; ils ne sont **PAS** 168 nouvelles conditions scientifiques statistiquement distinctes, même s'ils créent 168 nouvelles instances techniques.

## Sources originales et hashes, déjà connus avant ZR

Les deux archives \`a230z-py3.11\` et \`a230z-py3.12\` du run Z original contiennent les mêmes octets :

- \`a230z-physical-worlds.json\` SHA-256 \`09fc343e059eebcd7bee863ca1e93d41a2c606d3afa6636e11f72d89f9f0458d\`.
- \`a230z-summary.json\` SHA-256 \`170c8db38b419a22b63ca0f7493dae0e83d9069b34ad3388c7e9dbaa2d8a783c\`.

L'auditeur doit refuser toute source dont l'un des octets ou hashes a changé. Il doit **refaire lui-même** les configurations/layouts Stage2 d'après le préenregistrement Z et vérifier \`config_sha256_external_only\` et \`layout_sha256_external_only\` **avant toute transition** de chaque monde. La physique de base est la fixture pure \`stage12-a230l-standalone-physics-v1\`, avec initiale énergie 50, nourriture 60 (remplacée par 35 ou 45 selon cellule), eau 20, intégrité 100, coût des actions explicite, deux baies, décès irréversible. Ne pas importer le runner Z, ses règles de sélection, \`EquipmentCorpusRecorder\`, un modèle de conséquences, le vrai planificateur Stage6, un I0, l'Oracle ou Bench.

## Protocole de relecture physique

Pour les **168 identifiants originaux**, créer un **nouveau monde de test détaché** sans modifier une vie I0. Réinstancier le scénario seulement à partir des facteurs de la matrice préenregistrée, et non d'une conséquence archivée. Capturer la perception disponible via \`SymbolicPerception.capture\` et \`state_from_capture\`; reconstituer la procédure de laboratoire \`OBSERVED_ONLY\` ou \`SINGLE_EAST_PROBE\` **indépendamment**, à partir du seul \`SimulationState\` courant et des actions locales passées, puis appeler directement \`WorldBody.apply\`. Comparer à chaque pas l'action proposée et physiquement appliquée, l'état avant, l'état après (reçu **externe uniquement** si terminal), la terminaison et le hash canonique de l'exemple original. La capture post-terminale d'un décès ne doit jamais être ajoutée comme mémoire vécue, et une instance terminale n'est jamais poursuivie.

**Prédiction bloquée avant test :** il doit y avoir **168 nouvelles instances techniques, exactement 244 nouvelles applications physiques techniques** (y compris 88 mondes sans ingestion et plusieurs sans action), **20 terminaisons**, **0 différence de conséquence ou de digest**, **0 reprise après mortalité**, et 40 succès avec survie dans les variantes connues. Une autre valeur entraîne **FAIL**, aucune correction rétrospective de matrice ni suppression des scénarios discordants.

## Contrôles négatifs

Rejeter au minimum :
1. Un SHA de configuration ou de layout physique falsifié.
2. Une conséquence corporelle manipulée, **même si son hash est recalculé**.
3. Une commande enregistrée différente de la procédure first-person.
4. Un flag terminal modifié même accompagné d'un nouveau SHA.
5. Un effet latent changé sans annoncer la modification de configuration.
6. Un acte ajouté après la mort.
7. Une perception future ou un résultat Oracle injecté dans la décision.

Aucun audit ZR ne peut prouver qu'un résultat contrôlé par le banc a été effectivement décidé par l'I0 vivant. Les répétitions entre Python 3.11/3.12 ne multiplient pas le nombre d'échantillons scientifiques. Aucune mesure d'UC cognitive n'est effectuée.

**Conclusion anticipée seulement conditionnelle :** ZR PASS si tous les témoins sont strictement concordants; une fois validé, le résultat Z reste **physique positif** pour certaines alternatives visibles, **négatif** pour une sûreté universelle, et **négatif/non démontré** pour la planification cognitive autonome. **A2.30 PARTIELLE, Stage12 PARTIAL, #110 OPEN, PR #195 DRAFT**, aucun déploiement ni modification normative.
