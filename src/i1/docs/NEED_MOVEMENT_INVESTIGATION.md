# I1 : investigation prospective du blocage de déplacement et besoins (2026-10-18)

## Question
I1 dispose-t-il d'une opportunité de déplacement réellement perçue et admissible mais incapable de franchir le seuil de Competition ? Le sommeil amplifie-t-il seulement l'immobilité en masquant ce problème antérieur à toute consolidation ?

## Hypothèse préalable fondée sur WAL
Lot #39112892319, monde longlife-garden, variante 1, graine 773001, w_F=0.0 : source hydrique au nord à une case visible, 1113 propositions géographiques, aucun franchissement du seuil de Competition ; ratio maximal accumulation/seuil = 0,889845 ; mort au pas 232, sans déplacement, boisson, collecte ni ingestion. Les IDs d'options changent par pas et les modèles Stage6 n'offrent pas de première prédiction utilisable. La faible motivation est une hypothèse, pas un défaut démontré causalement.

## Intervention unique, quatre bras
Nouvelle branche issue du moteur I1 (PR #297) et de son correctif de sommeil PR #296, sans toucher I0. Reproduction exacte des paramètres de naissance géographiques naturels (`intrinsic_weight=min(base,0.35)`, avertissements locaux, capacity guard et configuration v1 de Exploration) avant la naissance ; seul `GeographicExplorationConfig.novelty_weight` est varié dans le domaine scientifique `0.15` (référence), `0.3`, `0.6`, `0.9`. Cette valeur représente un **intérêt subjectif pour une frontière réellement perçue**, pas une information sur la valeur nutritionnelle de l'eau ni une action imposée. `w_F=0.0` est figé pour isoler cette étape préliminaire ; les effets de sommeil seront étudiés seulement après correction. Chaque bras naît dans son processus et son journal WAL irréversible avec graine et layout appariés ; aucun rollback ou reprise de vie.

## Première matrice
3 mondes (`longlife-garden`, `oasis`, `foraging`) × quatre poids géographiques × deux variantes (1,2) = **24 vies**, horizon 300 pas ou mort définitive. Nouveau commit et résultats séparés de B1000. Sources hydriques, nourritures et dangers demeurent dans le monde physique ; seule la Perception ordinaire les observe. La règle qui perturbe les cartes n'assure **pas** de ressource au spawn dans garden. Les différences de mouvement/boisson seront donc stratifiées par opportunité réellement visible.

## Observables et décision
Analyse WAL externe et fail-closed : nombre de pas où une source d'eau adjacente est réellement visible, propositions géographiques, franchissement de seuil, mouvement effectivement admis, boisson/collecte/manger, durée de vie, décès et reçus de consolidation. Les séquences `Perception → Proposition → Competition → Action Control → monde` sont prises dans les événements causaux, jamais reconstruites par un oracle. L'objectif mécanique immédiat est de permettre un déplacement librement choisi lorsque motivé, sans créer de nouveau comportement forcé. Un succès moteur exige choix/admission/issue réelle et tests de non-régression. Le bénéfice hydrique, la survie durable et l'apprentissage restent séparés et NON ÉTABLIS jusqu'aux nouvelles mesures et aux tâches différées.

## Garde-fous
I0 inchangé ; `main` inchangé ; aucune priorité artificielle boire/manger ; aucune information cachée transférée ; chaque mort est terminale ; le contrôle à poids 0.15 doit reproduire la configuration naturelle avant toute conclusion ; aucun mélange de commits, ni de séries à cartes fixes et perturbées. Le verdict initial restera INCONCLUSIVE en l'absence de résultats.
