# A2.30-N : évaluation physique hors I0 d'un prédicteur d'intervalles incertains

**15 octobre 2026.** Autorisation opérateur explicite reçue pour **l'évaluation** du prédicteur, pas pour sa mise en production. Préenregistrement antérieur au code au commit `ef93099693e9a1b3bc6f3ab5f7f6d9717fde034b`. Prédicteur `bf8f8bae50ad071ee9f7c904057c5a59d96bacf4`, runner `8424e2c6ab2c01b32e924162c879dbc78522d9ea`, tests `15efe42c16ccd5ef0d0804974d01b320f38f9d6a`. [GitHub Actions #38726664498](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38726664498) **SUCCESS 3.11/3.12**, deux exécutions de **la même** matrice déterministe, artefacts JSON strictement identiques octet pour octet.

## Question et prototype

Peut-on élargir prudemment la couverture des prédictions à des positions et états corporels inédits sans présenter comme « sûrs » des effets observés uniquement en situation bénigne ?

Le prototype `LaboratoryUncertainDeltaPredictor` n'est **pas** un `EquipmentModel` : il **ne renvoie aucun état suivant complet**, aucun `Plan`, aucun statut `plan_found`, aucune probabilité prétendument calibrée et aucun certificat de sécurité. Il regroupe 42 véritables observations de commandes cibles pré-natales selon l'identité exacte de la commande et des préconditions **accessibles** (obstacle/créature du voisin concerné, ressources locales, inventaire, eau visible, abri/nuit). Il produit un **intervalle empirique de 11 deltas** (position x/y, 4 variables du corps, 5 inventaires) uniquement pour les groupes observés. Les coordonnées et niveaux corporels ne servent pas de clé de groupement, mais les variations de ces niveaux sont conservées dans les sorties.

Les étiquettes sont exclusivement `observed_harm` (nocivité observée dans le corpus) ou `unknown_hidden_risk` (absence de preuve de sûreté), ou `unavailable` quand il s'abstient. Il n'existe **aucune** sortie `safe`. Le comparateur est le `FrozenTableEquipment` exact appris du même corpus et une référence d'abstention permanente.

## Données séparées et authentifiables

**42 mondes d'entraînement indépendants, 54 transitions physiques appliquées** : 7 commandes (attendre, dormir, se déplacer est, collecter berry_a, manger berry_a, manger berry_b, boire) × 3 niveaux de faim × 2 positions. Les 12 collectes préparatoires aux commandes d'ingestion sont comptées parmi les 54 transitions, mais **seules les 42 commandes cibles** forment les exemples de modèle. Les modèles sont figés avant l'instanciation du moindre monde de test.

**62 nouveaux mondes indépendants de test, 82 transitions physiques appliquées**, répartis selon six strates fixées avant le code : 28 interpolations/positions inédites, 6 zones létales invisibles, 12 ingestions `berry_a` avec toxicité invisible (dont 6 létales), 4 obstacles visibles inédits, 4 commandes inconnues et 8 décroissances alimentaires cachées modifiées. Aucune de ces 104 instances `WorldBody` n'est une vie I0 ; **zéro nouvel individu, zéro pas autonome I0**, aucun Oracle ou banc dans la boucle cognitive. Le traitement n'a changé ni le runtime ni les normes.

**SHA-256 du corpus** : disponible avec les 42 entrées signées causalement dans l'artefact `a230n-training-manifest.json` du run. L'archive originale contient aussi les **62 entrées observables, commandes, sorties physiques et empreintes d'exemples**, et une synthèse. Les 3 JSON sont strictement égaux entre Python 3.11 et 3.12, et leurs hashes sont contrôlés dans A2.30-O.

## Résultats préenregistrés

| Strate de test | Mondes | Intervalles disponibles | Intervalles de deltas intégralement exacts | Terminalités hors ensemble observé | Refus |
|---|---:|---:|---:|---:|---:|
| Positions et faim inédites, contexte connu | 28 | 28 | **28** | 0 | 0 |
| Zone létale invisible | 6 | 6 | 6 sur les 11 deltas | **6** | 0 |
| Toxicité cachée `berry_a` | 12 | 12 | **0** (intégrité hors bornes) | **6** | 0 |
| Obstacle visible inédit | 4 | 0 | s.o. | s.o. | **4** |
| Commande jamais démontrée | 4 | 0 | s.o. | s.o. | **4** |
| Décroissance alimentaire cachée modifiée | 8 | 8 | **0** (nourriture hors bornes) | 0 | 0 |
| **Total** | **62** | **54** | **34** | **12** | **8** |

Les **20 manquements d'intervalles** sont 12 écarts d'intégrité sous toxicité cachée et 8 écarts de nourriture sous dérive physique. Les **12 terminalités hors ensemble** ne constituent pas 12 autres cas indépendants : 6 sont également des écarts d'intégrité sous ingestion mortelle. Les mouvements létaux peuvent respecter **tous les deltas numériques** tout en violant la terminalité. La condition de fin de vie doit être testée séparément des métriques corporelles.

**Comparaison d'utilité :** sur les 28 cas d'interpolation (pas d'augmentation des dangers cachés), couverture des 11 deltas `28/28` pour le prototype, aucune prédiction disponible `0/28` pour la table exacte, et `0/28` pour l'abstention systématique. Sur **tout** le jeu de 62 cas, la table exacte est disponible sur 18, et le prototype sur 54; ce dernier ne prédit toutefois **que des deltas incertains**, pas des transitions `SimulationState` complètes.

**Comparaison de sécurité :** les 18 cas adversariaux issus d'une clé exacte bénigne correspondent à une conséquence réelle nocive malgré une sortie exacte de confiance nominale 1,0. Le témoin **naïf externe** qui inférerait `sûr` de ce match se trompe **18 fois**, dont 6 létalités cachées et 12 toxicités de `berry_a`. **Ce témoin externe n'est pas le moteur de sûreté actuel de Stage6**, qui marque les risques « unknown »; ces 18 cas ne sont donc pas 18 actions dangereuses exécutées par I0.

Le prototype maintient **0 certificat de sûreté pour 62 cas**, comme l'abstention systématique. Parmi **22 cas réellement nocifs**, il possède `observed_harm` pour les **4 cas connus de `berry_b`**, mais les 18 autres sont `unknown_hidden_risk`. Il ne les détecte pas positivement : son abstention à certifier la sûreté est seulement la protection épistémique appropriée.

## Confrontation aux hypothèses

**N1 soutenue localement :** les intervalles conditionnels couvrent toutes les dimensions choisies des 28 transitions ordinaires inédites malgré l'absence de matching exact. Cela **ne** démontre pas une amélioration de Stage6 réel : aucun état suivant complet, aucune précondition d'un plan multistep, aucune décision, aucun repas vécu n'est obtenu.

**N2 soutenue comme discipline d'incertitude, pas détection du danger :** le prototype s'abstient de certifier la sécurité partout; la comparaison adversariale démontre pourquoi il ne faudrait pas convertir `confidence=1.0` en vérité physique.

**N3 confirmée :** les bornes empiriques manquent 20 valeurs de conséquence et 12 terminalités dans des mondes contrastés ou dérivés. La projection ne capture pas les effets cachés. Aucune calibration de probabilité, invariance, impossibilité physique globale ni garantie universelle n'est prouvée.

## Décision

**VALIDATION TECHNIQUE DU BANC : PASS. DÉPLOIEMENT DU PRÉDICTEUR DANS I0 : NO-GO.** Les résultats sont reproductibles et discriminants, mais la compétence de prédiction des conséquences dangereuses **n'est pas suffisante**. Ne pas relâcher Stage9/DC-05 ni modifier la spécification normative v1.3.1. **A2.30 PARTIELLE ; Stage12 PARTIAL ; issue #110 OPEN ; PR #188 DRAFT empilée sur #187.**

**Prochain test prioritaire :** construire un *ensemble de conséquences conditionnelles* explicitant les branches terminales possibles, ou une politique robuste d'abstention en cas de causes cachées, puis confronter des prédictions ex ante à des mondes tenus hors entraînement (y compris les risques différés, zones létales et effets cumulés). Un modèle seulement « plus couvert » ne doit pas devenir une politique d'action avant preuve prospective de sécurité et décision opérateur.
