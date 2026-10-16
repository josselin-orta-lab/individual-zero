# A2.30-ZA : audit indépendant du banc alimentaire Z, des perceptions et de Stage6

**15 octobre 2026.** Audit ZA **préenregistré APRÈS connaissance des résultats originaux Z mais AVANT son code** au commit `ddc2cfe69e1e296581140acc3d73d98944bce029`. Code de recalcul indépendant `c853808f101a1af79f2ce4ccd9a656b938e3a7d2`, tests adversariaux `7bf8d615ba80a02458d7deb6a0f019fc80cd4d61`. [GitHub Actions ZA #38762998118](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38762998118) : **PASS Python 3.11/3.12**, **20 tests de falsification** par version, résultats identiques. Le premier job 3.11 a échoué **pendant le téléchargement source** sur une HTTP 503 temporaire « Egress is over the account limit », avant tout test scientifique ; [sa relance seule](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38762998118) a réussi **sans modifier le protocole, le code ou les données**. Le job 3.12 avait réussi dès la première tentative.

## Sources et périmètre, aucune nouvelle physique

ZA lit **uniquement** les deux artefacts originaux de la campagne Z, [run #38760713470](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38760713470) au code **`0d9fd7cd511640103498f037b84cae915169356e`**. Les deux archives Python 3.11 et 3.12 contiennent des JSON **identiques octet par octet**, vérifiés aux SHA-256 complets :

- `a230z-physical-worlds.json` : `09fc343e059eebcd7bee863ca1e93d41a2c606d3afa6636e11f72d89f9f0458d`.
- `a230z-summary.json` : `170c8db38b419a22b63ca0f7493dae0e83d9069b34ad3388c7e9dbaa2d8a783c`.

**ZA n'a créé aucun nouvel I0, monde de laboratoire, pas physique ou événement cognitif**. Il ne réutilise **ni le runner Z, ni `WorldBody`, ni `SimulatorPlanner`, ni le modèle `FrozenTableEquipment`** ; ses décisions accessibles et sa vérification des racines de Stage6 sont réimplémentées dans un auditeur de lecture seule. Seule la fonction normative de sérialisation causale/empreinte est conservée.

### Transparence sur la révision pré-code du protocole

Le protocole Z initial `c046712b97b0e5887dece3b490957123013d7b5e` prévoyait les catégories de scénarios et imposait de verrouiller les quantités avant l'expérience. Une première déclinaison à **68 mondes/160 transitions** a été enregistrée au commit `70b4e066` le 15 octobre **15:19:46 UTC**, puis remplacée **avant toute implémentation ou observation** par le plan factoriel étendu à **168 mondes/244 transitions** du commit `e9543fe` à **15:20:30 UTC**. Le premier code Z n'est apparu qu'au commit ultérieur `33e2d1c`, 15:26:02 UTC. **La cohorte de 68 mondes n'a jamais été exécutée comme résultat Z ; son protocole reste visible pour audit.** Le plan 168/244 est celui qui gouverne la CI physique originale. Aucun ajustement de protocole post-résultat n'est ainsi revendiqué.

## Recalcul sans informations cachées dans la décision

L'auditeur reconstruit l'état Stage6 accessible complet, les actions physiques avant/après, les historiques vécus uniquement avant mortalité, les prédécisions de la politique de banc et le SHA causal de chaque transition. Une action non autorisée par les informations locales visibles est rejetée. La politique de **laboratoire** est une règle first-person prédéfinie qui **a réellement dirigé des `WorldBody.apply`** ; ce ne sont pas des actions choisies par l'I0 cognitif. Le **véritable Stage6**, en revanche, n'a été sollicité **qu'en shadow mode**, et aucune de ses commandes potentielles n'a été appliquée.

| Scénario physique et bras | Mondes Z | Pas physiques Z | Ingestions B | Repas physiques avec survie | Décès externes | B non ingérée |
|---|---:|---:|---:|---:|---:|---:|
| A uniquement, observation seule / une sonde est | 40 | 20 | 0 | 0 | 0 | 40 |
| B locale, deux politiques | 32 | 64 | 32 | 16 | 8 | 0 |
| B visible à l'est mais case bloquée, deux politiques | 32 | 0 | 0 | 0 | 0 | 32 |
| B à l'est accessible, deux politiques | 32 | 96 | 32 | 16 | 8 | 0 |
| B à deux cases, visible après une sonde est seulement | 32 | 64 | 16 | 8 | 4 | 16 |
| **Total** | **168** | **244** | **80** | **40** | **20** | **88** |

En plus des 40 succès alimentaires avec survie, **20 ingestions B non létales ont eu un gain insuffisant**. Parmi les 40 contextes d'observation initiale communs aux effets cachés, **20 contextes alimentaires effectivement engagés contiennent chacun deux issues de succès avec survie, une mort et une absence de gain suffisant**, pour une perception antérieure strictement identique. Les **huit paires de contextes A seule / B distante** ont exactement la même observation initiale : la B éloignée n'est pas magiquement visible avant déplacement. Les différences de `passable` et de ressource visible sont, au contraire, exploitées par la règle d'accessibilité sans fuite de la configuration cachée.

### Stage6 réel, mais uniquement passif

Pour les **80 recherches** exécutées dans le runner Z avant ingestion B, l'auditeur reconstruit indépendamment les commandes permises par l'état courant et les clés exactes `SimulationState × PrimitiveCommand` issues des **seules transitions déjà vécues dans le même monde**. Aucune prédiction extérieure, aucun événement futur ni observation de la mort après ingestion ne rejoint le corpus. Résultat : **80/80 recherches `incomplete_model` à zéro première arête connue**, recalcul indépendant identique aux diagnostics de `SimulatorPlanner.search`. Le résultat signale une limite des tableaux exacts, pas une impossibilité physique de manger.

Une action alimentaire sélectionnée par le laboratoire ne constitue ni un `Plan` Stage6, ni une preuve de compétence alimentaire d'I0, ni une expérience d'attribution d'agence au Stage12. **Les UC cognitives réelles n'ont pas été mesurées**. L'optimisme d'une branche favorable ou la visibilité de B n'est jamais certifiée « safe ».

## Témoins adversariaux

**20 tests adversariaux PASS par interpréteur**, dont : champ caché injecté dans les perceptions, B inaccessible pourtant collectée, ressource future falsifiée avec empreinte recalculée, chaîne physique interrompue même avec SHA d'exemple recalculé, faux décès, impression d'une perception vécue postmortem, mémoire Stage6 alimentée par une transition future ou par un autre monde, première arête artificiellement connue, fuite Oracle, UC=0 artificiel, certificat alimentaire sûr inventé, dénominateur tronqué, monde dupliqué et résumé agrégé falsifié. La validité des tests ne transforme pas les données préenregistrées en nouvelles naissances.

**Limite de l'audit :** ZA valide la cohérence physique *rapportée* dans les archives, pas **indépendamment l'exécution** historique de `WorldBody.apply`. L'application physique est attestée par le runner original Z ; une nouvelle implémentation de replay, sans import du runner, renforcerait cette frontière dans une campagne technique séparée. La fréquence 20/80 morts reflète un **échantillonnage factoriel intentionnel** de quatre effets possibles, pas une fréquence naturelle de toxicité.

## Décision

**ZA : PASS de validation d'archives, NO-GO de déploiement cognitif.** Une alternative accessible peut fournir réellement de la nourriture dans certains mondes ; ni sa présence perceptible ni une exploration d'une case ne certifient son effet toxique, et Stage6 reste incapable de prédire une première étape avec cet Equipment exact dans toutes les 80 recherches testées.

**A2.30 PARTIELLE ; Stage12 PARTIAL ; issue #110 OPEN ; PR #195 et #196 DRAFT non fusionnées.** Aucun changement de la spécification normative `mvp-specification-v1.3.1.md`, des modules de production, de l'Oracle, du WAL, de la mortalité, de la sécurité alimentaire Stage9/DC-05 ou de l'agence subjective.
