# Individual Zero / Issue #110, campagne A2.13 : sécurité des projections d'état du modèle Equipment

**Préenregistrement : 14 octobre 2026, avant tout script de campagne ou exécution A2.13.**

Base vérifiée : `main@747cbd44ac89ace066d9bbbc0a527cf5ccb47913`. Stage12 scientifique **PARTIAL**, issue #110 **OPEN**, réception opérateur absente. Aucune modification normative MVP v1.3.1.

## Hypothèses issues de A2.12

A2.12 a observé directement **1 178 clés de simulation refusées** sur 8 vies de 42 pas, dont **610** commandes sans exemple comparable et **568** états complets absents pour une commande déjà vue. Ajouter des exemples à un tableau de correspondance exacte a réduit les refus OFF/ON de 592 à 586 sans nouveau repas ni amélioration de trajectoire. Les refus ne prouvent pas que supprimer un champ de l'état est sûr.

**H0-sûreté :** des états différents uniquement dans un champ prétendument « secondaire » pourraient néanmoins produire deux résultats réellement incompatibles pour la même commande. **H1-projection :** certaines projections peuvent ne présenter aucune collision contradictoire dans le corpus, mais ce résultat empirique borné ne suffit pas à établir une équivalence causale universelle. **H2-indiscernabilité :** deux mondes de conséquences nocives différentes peuvent produire un **état complet observable identique**, ce qui interdit au modèle d'inférer une étiologie cachée depuis la seule observation.

## Plan physique préenregistré

Construire des mondes `WorldBody` **externes** et ne recueillir que les entrées `SimulationState`, commandes et sorties de `WorldBody.apply` réellement appliquées. La vérité cachée peut servir **uniquement à l'évaluateur externe**, jamais à I0 ou à la production de prédictions cognitives. Aucun individu mortel de A2.12 ne sera restauré ni réentraîné après naissance.

Six familles de contrastes, chacune reproduite avec **8 seeds déclarées (41..48)** pour des paramètres corporels/positions explicitement tirés par PRNG indépendant par famille et seed. Deux mondes par contraste. Un résultat déjà calculé ne change ni les seeds ni les seuils.

1. **BODY_CAP** : deux états corporels initiaux différents, même baie et commande `manger` après une collecte réellement exécutée, l'un assez proche de 100 pour saturer `food`, l'autre non. Un modèle qui omet `body` ne doit pas attribuer arbitrairement les mêmes valeurs finales.
2. **INVENTORY** : un monde permet une collecte avant `manger`, l'autre n'a pas de baie à collecter. Les entrées post-collecte sont appariées sur corps et localité, mais pas inventaire ; les ingestions physiques doivent différer. Attention : `effects.ate="unavailable"` ne compte pas comme repas.
3. **ADJACENT_PASSABILITY** : déplacement vers une cellule libre versus bloquée ; un modèle supprimant `adjacent` ne doit pas dire qu'il connaît le résultat.
4. **NIGHT_CREATURE** : même cellule et créature physiquement adjacente, `attendre` en journée versus de nuit ; l'effet sur `integrity` doit être traité comme distinct.
5. **HIDDEN_TOXICITY** : deux configurations physiques avec même capture locale et même baie `berry_a`, l'une inoffensive, l'autre avec `integrity_delta<0`, et même commande de consommation physique. Tester explicitement l'égalité de l'état observable complet, tout en conservant la différence des effets nocifs techniques **hors cognition**.
6. **HIDDEN_EXTERNAL_HAZARD** : juste avant `manger`, un des mondes reçoit une zone dangereuse externe non perceptible sur sa cellule. L'observation corporelle et spatiale avant consommation peut rester identique; la sortie physique doit différer. Ne pas conclure que l'aliment est la cause du dommage.

Les contrastes collecter→manger comportent des transitions préparatoires ; toutes les transitions sont physiquement appliquées, sans fabrication de `observed_next_state`. Un vrai « effet retardé de l'aliment » n'est **pas** simulé par cette campagne : une zone extérieure activée un pas ultérieur serait un autre scénario, et ne doit pas être imputée à l'aliment. Les restrictions de Stage9/DC-05 restent inchangées.

## Mesures, seuils et décisions fixés avant les résultats

- **T1 réalité :** 6 familles ×8 seeds = **48 paires**, **96 mondes physiques** distincts, avec traces et hashes d'entrée/commande/sortie, et nombre exact de transitions réellement appliquées; zéro erreur de test de provenance et aucun résultat prophétisé.
- **T2 collision :** pour chaque paire, comparer `FrozenTableEquipment.input_digest(SimulationState, command)` et les faits physiques `position_after, body_after, inventory_after, terminal, effects`. Conserver les cas où le même **input complet** mène à des conséquences divergentes dans des mondes cachés différents : ils sont un signal d'incertitude irréductible, pas une erreur à « corriger » en donnant l'Oracle à I0.
- **T3 projections :** diagnostiquer les candidats `drop_body`, `drop_inventory`, `drop_adjacent`, `drop_night`, `drop_absolute_position`. Chaque collision de clé projetée associée à des effets physiques contradictoires entraîne le verdict **UNSAFE** pour le candidat, indépendamment de son gain apparent de couverture. Une absence de collision est **INCONCLUSIVE**, pas PASS de sûreté.
- **T4 adversarial :** pour les familles hidden toxicity et hidden external hazard, exige au moins **8/8** paires de conséquences incompatibles à entrée observable complète identique, faute de quoi la démonstration d'indiscernabilité échoue. Un désaccord d'effet toxique sans concordance d'état n'est pas une preuve suffisante.
- **T5 garanties :** le modèle `FrozenTableEquipment` doit conserver le refus `LookupError` sur les clés inconnues. Aucun changement dans `Stage9`, `Safety`, `Competition`, `Oracle`, les UC, le journal causal, la mortalité ou le contrat v1.3.1. Tests Python 3.11 +3.12, fichiers par seed, versions/config hash, audit indépendant des sorties et résultats négatifs.
- **C1/C2 :** aucune prédiction favorable, collision ou intervention externe n'est automatiquement un jugement subjectif d'agence.
- **C3/C4/C5/C6 :** cette première phase est une **expérience externe de sémantique Equipment**, pas une preuve de diversité/exploration, d'ingestion autonome ni de stabilité à 600 pas. Ne pas attribuer PASS de ces critères.
- **C7 :** reproduction inter-Python exigée ; huit seeds contrôlées dans les mondes physiques sont de véritables tirages reproductibles mais ne constituent pas huit vies cognitives indépendantes.
- **Décision :** si une projection est contredite, ne pas la déployer. Si des états observablement identiques ont des effets différents, préserver `unavailable` ou une représentation explicite de l'incertitude, jamais une « toxicité connue » tirée de la vérité externe. Toute proposition de mécanisme apprenant l'incertitude sera préenregistrée séparément et confrontée au delta normatif DC-05 déjà proposé pour v1.3.2, jamais appliqué silencieusement.

**Verdict global Stage12 conservé à PARTIAL** jusqu'à nouveaux résultats autonomes puis validation opérateur. L'issue #110 reste ouverte.
