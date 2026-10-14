# Stage12 issue #110 : A2.20, registre probant et limites de l'auto-vérification

**14 octobre 2026. Statut de la validation finale : en cours.** Préenregistrement préalable au code `87555873`, puis correction numérique avant instrumentation `f5f586d1`. Le protocole prévoyait 64 mondes, 192 transitions physiques, 48 reconsidérations et 16 événements d'indice supplémentaire.

## Résultats expérimentaux vérifiés

[CI #38639327252](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38639327252) : **SUCCESS Python 3.11 et Python 3.12** au commit expérimental `39b489ded02a5e4ebe7d37cb80599108c56f2ad3`, mêmes huit seeds 111–118 rejouées sous deux Python. **64 mondes physiques, 192 vrais `WorldBody.apply`, 32 relocalisations externes initiales, 64 déplacements passifs ultérieurs**, 16 mondes par famille `stay_stay/passive_stay/stay_passive/passive_passive`. **48 jugements historiques reconsidérés**, dont **24 initialement corrects et 24 initialement faux** ; **16 événements de renforcement** distincts sans seconde reclassification. **0 vie autonome, 0 révision du système cognitif I0, 0 couple GA-06** issu du laboratoire.

Les 32 paires normal/confondu présentent des captures t1..t4 et statuts de révision identiques, alors que le premier effet physique est causalement distinct. La vérité de l'intervention reste accessible uniquement à l'évaluateur externe. Le nouveau doute n'établit donc pas la cause passée et frappe autant de premiers jugements corrects qu'incorrects sur ce dispositif.

## Garde-fou et objection adversariale

Le registre candidat est **append-only en laboratoire**, enregistre le jugement initial, les étapes, les références de perceptions et les SHA chaînés, puis refuse des altérations, doublons et violations temporelles. L'auto-vérification d'un tel registre ne prouve pas la vérité de la catégorie déclarée : un adversaire capable de réécrire un événement *et toute la chaîne* pourrait lui attribuer `revision_to_unknown` même sur un épisode sans déplacement passif. Le correctif A2.20 introduit donc un **audit de sémantique indépendant des événements**, recalculant les catégories depuis les quatre captures réellement archivées, sans effets du WorldBody ni Oracle. Il teste expressément une chaîne forgée puis recalculée dont l'audit interne accepte les hachages mais dont l'audit contre les captures doit refuser la fausse assertion.

Ce contrôle protège les résultats **dans la mesure où les captures sources proviennent d'une archive de confiance indépendante**. Il n'est pas une signature cryptographique de la physique ou une protection contre la réécriture simultanée de toutes les sources. Le résultat de la CI pour ce correctif sera noté séparément : ne pas confondre le PASS initial du commit `39b489de` avec le statut du correctif `ca1af054`.

## Conclusions et décision

Un modèle de révision subjective non destructif et auditable paraît **faisable hors ligne**. Aucun degré probabiliste de confiance n'a été calibré, aucune étiologie physique cachée n'est devenue perceptible, aucun apprentissage rétrospectif d'I0 n'a été prouvé. La future intégration exigerait des contrats nouveaux de mémoire, de propriétaire, de coût UC, de WAL et de mortalité. La responsabilité du résultat distal, notamment alimentaire, ne découle pas de l'agence proximale de l'action. Cette séparation reste à arbitrer explicitement par l'opérateur **avant** changement du MVP normatif v1.3.1.

**Stage12 PARTIAL ; issue #110 OPEN ; pas de réception opérateur ; aucun changement de production cognitive, Oracle, Stage9/DC-05, sécurité ou seuil 2+2/12.**
