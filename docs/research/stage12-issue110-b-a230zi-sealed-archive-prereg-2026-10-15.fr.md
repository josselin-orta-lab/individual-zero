# A2.30-ZI : audit d'archives indépendant du scénario Z, préenregistré après résultat

**15 octobre 2026, après résultats Z connus, AVANT code de l'auditeur ZI.** Nouvelles données physiques **déjà** obtenues dans [run #38760713470](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38760713470), au SHA immuable du runner **\`0d9fd7cd511640103498f037b84cae915169356e\`**. L'étude Z a été préenregistrée au commit \`c046712b97b0e5887dece3b490957123013d7b5e\` et verrouillée en **168 mondes / 244 pas** au commit \`e9543fe0139f719e1d5d71468450532af4266fb7\` avant le runner. CI initiale Z PASS sur Python 3.11/3.12 (15 tests chaque), résultats identiques.

**Résultats connus avant ZI :** 168 mondes physiques, 244 actions, 80 ingestions de \`berry_b\`, 20 terminaisons physiques, 40 succès alimentaires avec survie, 20 non-succès avec survie, 88 abstentions, 80 requêtes du vrai algorithme Stage6 en shadow toutes \`incomplete_model\`; coût UC d'I0 non mesuré. Des alternatives physiques existent, mais les causes cachées d'une autre espèce restent confondues. Aucun succès de plan exécuté par I0 n'est démontré.

## Sources scellées et propriété vérifiable

Télécharger sans modification **les deux artefacts originaux** \`a230z-py3.11\` et \`a230z-py3.12\` du run #38760713470. Les fichiers JSON ont été inspectés avant ZI et sont identiques octet par octet :

- \`a230z-physical-worlds.json\` : SHA-256 **\`09fc343e059eebcd7bee863ca1e93d41a2c606d3afa6636e11f72d89f9f0458d\`**.
- \`a230z-summary.json\` : SHA-256 **\`170c8db38b419a22b63ca0f7493dae0e83d9069b34ad3388c7e9dbaa2d8a783c\`**.

L'auditeur lit les deux archives avec leur hash fixé, **sans importer le runner Z, \`SimulatorPlanner\`, \`FrozenTableEquipment\`, \`WorldBody\`, \`EquipmentCorpusRecorder\` ni un oracle**. Il ne peut donc pas attester indépendamment \`WorldBody.apply\` depuis des JSON seuls. L'audit ZI n'ajoute **aucun nouveau monde ni aucun pas physique**.

## Audits négatifs et recalculs à réaliser

1. Reconstituer les **168 identités distinctes** à partir des facteurs préengagés (5 layouts ×2 politiques ×(5 ou 4 variantes) ×2 faim ×2 positions), et leurs **244 transitions**, y compris les 88 abstentions et les mondes avec zéro action. Contrôler les hash canoniques de chacune des **244 transitions** et l'identité des 11 dimensions \`SimulationState\` des états accessibles avant/après.
2. Réimplémenter indépendamment la règle de la politique de laboratoire **uniquement à partir de chaque capture \`SimulationState\`**, de la présence/absence de \`berry_b\` ici ou à l'est et de la passabilité est, du préfixe physiquement exécuté et du protocole fixe. **Aucune information latente ne peut influencer les actions**. Un obstacle sur la case directement souhaitée doit empêcher l'action correspondante. Les ressources B invisibles à deux cases ne doivent pas apparaître au temps t0.
3. Reconstituer les 40 classes de contextes, et garantir l'**égalité complète des historiques de décisions et des captures AVANT INGESTION** entre variantes cachées, puis les contrastes corps/survie après ingestion. Tester la divergence après sondage physique entre A_ONLY et B_EAST_TWO_STEPS pour des états initialement indiscernables.
4. Reconstituer **indépendamment les racines Stage6** sans appeler le planificateur : depuis les transitions *antérieures du même monde* uniquement, calculer les clés exactes \`SimulationState×PrimitiveCommand\` proposées pour chaque requête réelle. Comparer **les 80 diagnostics** du vrai Stage6 enregistrés par Z, distinguer couverture du modèle exact et capacité de planification, et préserver \`incomplete_model\` si c'est le résultat.
5. Refuser explicitement : variante cachée ou observation future injectée dans la clé, digest d'exemple altéré même si la somme finale reste identique, commande à travers obstacle, ressource fantôme, action après décès, capture postmortem qualifiée de vécue, corpus shadow comportant une transition future ou d'un autre monde, un \`plan_found\` inventé et un \`safe\` certifié.
6. Vérifier que l'**effet alimentaire de B n'est pas traité comme une preuve de sûreté**. Quantifier les 20 groupes d'ingestion où la même capture avant ingestion reste compatible avec une conséquence létale et des réussites.
7. Vérifier l'**identité octet par octet des artefacts originaux 3.11 et 3.12**, produire un rapport JSON vérifiable avec source SHA, verdict borné et zéro nouveau pas scientifique.

**ZI PASS technique** uniquement si contrôles négatifs et recalculs réussissent. Cela ne constitue ni une réplication physique indépendante, ni une preuve causale subjective ou cognitive du Stage12, ni une fréquence naturelle de risque. Le cas échéant, une relecture technique physique du moteur avec des nouveaux \`WorldBody\` sur les mêmes cellules originales sera **préenregistrée après ZI** et comptabilisée uniquement comme validation technique, pas comme nouvelle cohorte.

**A2.30 PARTIELLE ; Stage12 PARTIAL ; issue #110 OPEN ; PR #195 DRAFT. Déploiement cognitif NO-GO. Aucune modification normative.**
