# Stage8-E2: transport technique natif G0/G1/G2 et conservation originale

**Etat au 19 novembre 2026:** code de campagne technique **en PR, non exécuté**; aucun nouvel individu, aucune vie, aucun World de l'étude causale n'a été créé par cette PR. La source de développement n'est PAS une source scientifique préenregistrée. Les verdicts Stage7/Stage8-A/B/C, I1 actif et Stage2.1 \`NOT_ISSUED/HOLD_NO_VERDICT\` restent inchangés.

## But

Tester, ultérieurement et sur **de nouvelles populations indépendantes**, si la permutation réciproque du bloc natif \`gamma1,gamma2,gamma3\` modifie la différence de persistance G2 entre les descendants sélectionnés S et leur contrôle M à concentration parentale appariée.

**Unité indépendante**: population \`p\`, n=64. Le futur estimand unique est \`T[p] = (S_sham - M_sham) - (S_swap - M_swap)\`, Student bilatéral alpha 0,025, t critique df63 \`2.2962367715148795\`. L'outil d'exécution technique ne calcule pas ni ne publie ce contraste comme verdict. Ce choix n'identifie pas \`gamma3\` seul.

## Frontières d'exécution

1. \`stage8e2_technical_transport.make_plan(root, HEAD, source_sha, archive_root)\` reconstruit un **plan pur**: 64 populations × 24 fondateurs, trois générations de WorldSpecs F0, six occasions World par génome; 384 WorldSpecs G2 appariés entre quatre bras; empreintes de tous les domaines de graines, génomes fondateurs, 6 144 mutations S/M futures, 3 072 tirages S et 128 clés de permutations M. Le plan est \`scientific_admission=false\`; zéro vie.
2. **La source exacte est obligatoire**: \`git HEAD\`, digest \`source_snapshot\`, checkout propre, horodatage de publication du plan et SHA-256 des octets externes AVANT G0, chemin canonique d'archives hors dépôt, présence de l'ADR propriétaire. Les plans et racines Stage8-C sont consommés et ne doivent jamais être rejoués.
3. Chaque appel technique vérifie de nouveau ces conditions et la chaîne des phases antérieures. L'exécution doit se faire seulement sur le **HEAD exact fusionné**, après revue et CI; pas sur la branche courante.
4. \`G0\` : 1 536 nouveaux génomes v4 fondateurs × six Worlds = **9 216 vies**. Le module natif \`run_life(..., keep_trace=True, decision_policy="reference")\` conserve les traces et la politique moteur/facturation P1.3 inchangées. Chaque vie écrit un gzip JSON original avec deux SHA-256 distincts (compressé et décodé) dans \`PHYSICAL_G0/G0/life-NNN.json.gz\`.
5. **Aucun G1 sans le scellement et l'audit de tous les G0 gzip**. L'auditeur séparé vérifie les fichiers originaux, identité, source, WorldSpec, génome, horizon, morts, traces et facturation corporelle payée. Les scores de chaque parent proviennent exclusivement des six vies déjà authentifiées. Toute erreur stoppe la racine sans correction sélective.
6. \`SELECT_G1\` : génération v4 mutée S, tirage parent selon la persistance, contrôle M score-blind par permutation bijective à multiplicités exactement égales. Un **auditeur de filiations distinct** reconstruit indépendamment le classement, les tirages, les mutations et les 3 072 descendants à partir des originaux. Puis \`G1\` : **18 432 vies**, mêmes contrôles des gzip et des scores. Aucun G2 avant ces preuves.
7. \`SELECT_G2\` : 3 072 descendants v4 S/M issus de G1, puis création des quatre génotypes G2 \`S_sham / M_sham / S_swap / M_swap\` sans modifier les 28 gènes hors bloc gamma. \`G2\`: **36 864 vies** dans les WorldSpecs G2 préalloués, une vraie identité RNG par bras.
8. Chaîne de preuves **neuf phases**: \`G0, SEAL_G0, SELECT_G1, G1, SEAL_G1, SELECT_G2, G2, SEAL_G2, R_FINAL\`. Chaque preuve est liée au SHA-256 du fichier d'origine et au SHA de la phase précédente. Une erreur de source, un enfant sans parent, une vie manquante, un monde non apparié ou un original altéré donne \`TECHNICAL_NO_VERDICT_NO_RETRY\`; pas de tentative compensatoire.

Volume par exécution technique : **64 512 vies originales** (9 216 + 18 432 + 36 864), générées à l'horizon maximal de 400 pas. La taille disque et les coûts GitHub CI ne sont pas encore mesurés. Prévoir les archives ZIP et empreintes pour un stockage durable au-delà des 90 jours de rétention GitHub.

## Utilisation **future**, uniquement après fusion, source figée et archivage du plan

\`\`\`bash
PYTHONPATH=src python -m i3.lab.stage8e2_technical_transport \
  allocate <GIT_HEAD_40HEX> <SOURCE_MAP_SHA256> \
  /tmp/new-stage8e2-technical-originals /tmp/stage8e2-plan.json
# publier le plan+SHA dans un artefact préexposition daté, vérifier le dépôt propre
# après cette publication indépendante (pas durant les tests logiciels) :
PYTHONPATH=src python -m i3.lab.stage8e2_technical_transport \
  run /tmp/stage8e2-plan.json <PUBLISHED_PLAN_FILE_SHA256>
\`\`\`

Ces commandes sont une **interface à valider**, pas un ordre d'exécution immédiate. Le plan ne doit pas être régénéré pour réparer une cohorte partielle. Un nouvel essai scientifique exigera ensuite deux répétitions techniques complètes distinctes Python 3.11/3.12, leurs artefacts et reçus vérifiés indépendamment, puis une **troisième** racine scientifique et une nouvelle préexposition. Les répétitions techniques n'ont jamais valeur de résultat scientifique.

## Restant avant toute naissance technique

- Réussite CI exact HEAD Python 3.11/3.12, audit méthodologique du transport, protection des chemins d'archive et publication indépendante du plan.
- Exécution contrôlée de deux répétitions techniques complètes sur deux racines nouvelles, mesure de coût, durée et taille ZIP, reçus de source/archives exacts.
- Audit rétrospectif indépendant sur **les gzip natifs effectifs** et leurs chaînes, avec témoins de corruption, et contrôle de deux racines disjointes avant le protocole scientifique final.
- Aucun \`GO\` causal, aucune promotion I3 et aucune nouvelle expérience scientifique ne sont autorisés par les fonctions et tests de cette PR.
