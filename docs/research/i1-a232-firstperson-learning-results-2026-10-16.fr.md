# A2.32 — audit des occasions d'apprentissage vécu d'I1 (2026-10-16)

**Statut : NO-GO pour la généralisation cognitive ; apprentissage non démontré, et volet indice perceptible en échec de validation.** La campagne a été enregistrée avant exécution au SHA `c637f6e27d64c4b7cc8ab732c793469ab802debc`. Le runner a été créé ensuite (`69d19611e16633ce033d4c98a5ee8ba2dc3c772c`), workflow `8f5b4467feda1a79966de52ef2e3b778cbd38f4f`. [Exécution CI 38860987817](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38860987817) : jobs Python 3.11 et 3.12 PASS, archives par vie et journaux WAL. Les deux environnements répètent la même cohorte déterministe ; ce ne sont pas des réplications scientifiques indépendantes.

## Effectifs et résultats

- 32 paires / 64 vies mortelles distinctes ; 232 transitions réellement exécutées, 0 exception et 0 journal invalide.
- Corpus d'entraînement **externe**, physiquement exécuté, séparé des vies test : SHA-256 `032fa892665ea626d6d8ff5cad209a77e1f3113c49cb2dfa0c9d3101a10d1203`. Il ne constitue pas une mémoire vécue de I1.
- `CUE` : 8/8 paires, premiers déplacements est égaux, 0 alerte locale observée dans les événements ciblés, 0 décès. **PERCEPTION_PASS non atteint** (seuil : 8/8 alertes). L'éventuelle absence de branchement de `local_threat_alerts` dans la configuration doit être diagnostiquée avant d'affirmer une déficience sensorielle.
- `INJURY` : 8/8 paires avec capture de suivi dans les deux bras, 0 mort, premières commandes est identiques. Aucun événement de preuve vécue parmi les trois types ciblés par l'audit. La valeur de dommage et la présence d'une preuve cognitivo-mnésique admise ne sont pas encore croisées de façon indépendante dans le résumé ; **ne pas déclarer LIVED_OBSERVATION_PASS** sur cette seule sortie.
- `FAILURE` : 8/8 paires avec capture de suivi, premières commandes `collecter` identiques, 0 mort. 0 événement de preuve causale vécue parmi les trois types comptés. Le résumé ne mesure pas directement la quantité réellement collectée à t=1, la restitution d'inventaire, ni les actions successives par paire : **LEARNING_NOT_DEMONSTRATED**, et seuil de preuve d'occasion d'apprentissage **non évalué complètement**.
- `INDISTINGUISHABLE` : première commande `se_deplacer` dans les deux bras de chacune des 8 paires ; 0/8 morts dans les témoins et 8/8 dans les mondes mortels cachés. Pas de capture postmortem ni de journal invalide. Le résumé n'a pas encore établi l'égalité binaire complète des captures autorisées et des prévisions ; **indiscernabilité attendue par construction**, égalité intégrale à auditer sur les fichiers bruts. La mort n'est pas à elle seule un échec cognitif.

**Épistémologie déclarative :** 0 fausse assertion explicite de sûreté, terminalité, voisinage futur ou causalité distale détectée par le scoreur. Cela ne certifie pas une politique de sûreté opérationnelle.

## Écarts et limites du protocole

Le runner mis en œuvre conserve les valeurs corporelles du script A2.31 (`energy=60+i%3`, `food=14+i`, `water=75+i%4`) alors que l'enregistrement A2.32 prévoyait `65+i%3`, `13+i`, `72+i%4`. Cet **écart technique aux entrées préenregistrées** est important : la campagne observée est une **exploration avec déviation documentée**, et non une confirmation conforme du protocole gelé. Aucun dénominateur ni seuil ne doit être recalibré pour la présenter comme confirmatoire. Les sorties initiales du scoreur ne croisent pas non plus intégralement les événements perceptuels, l'intégrité observée, le contenu des épisodes mémoriels et la décision de suivi.

La présence d'un corps blessé ou d'une collecte échouée peut être visible au niveau WorldBody sans être structurée par Stage 9 comme une preuve discriminante du danger. Les journaux techniques ne sont pas automatiquement des souvenirs vécus. Inversement, l'absence des événements ciblés n'est pas une preuve que tout apprentissage est impossible.

## Décision et prochaines exigences

1. **Conserver la totalité des données et des morts** ; ne pas transformer les 8 morts indiscernables en erreur cognitive ni en connaissance préalable de I1.
2. Diagnostiquer pourquoi le commutateur `local_threat_alerts` n'a produit aucune alerte visible, sans lire une carte de zones cachées depuis la cognition.
3. Mettre en place un **audit hors ligne des artefacts existants** : perception avant/après, dommage du corps réellement observé, référence de commande, épisode autobiographique clôturé, preuve causale admise/refusée, décision ultérieure, budget UC, et provenance. Aucun label du laboratoire ne doit rejoindre la mémoire.
4. Créer un protocole confirmatoire séparé ou un amendement enregistré comme déviation, avec les paramètres initialement prévus, de nouveaux mondes, contrôles et critères figés avant génération des résultats.
5. N'implémenter une mémoire ou une politique adaptative I1 supplémentaire **qu'après** avoir localisé une lacune réelle de représentation ou de récupération de vécus ; ne pas modifier Stage 9, WorldBody, I0, les lois de mortalité, les seuils ou l'isolation Oracle.

**PR #219 : conserver en Draft. Main I0 : inchangé. Scientific cognitive release : NO-GO.**
