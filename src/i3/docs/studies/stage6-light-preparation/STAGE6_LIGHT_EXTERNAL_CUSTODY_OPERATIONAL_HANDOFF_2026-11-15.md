# I3 / Stage 6 légère : transfert de custodie indépendante (15 novembre 2026)

**Statut vérifié sur `main 60fb593b66712c834e592c9105f9a305de4f0112` : `OPERATION_NOT_CONFIGURED / NOT_RUN`.** Ce document est un contrat de **préparation opérationnelle**, pas une autorisation, un plan de lancement, une preuve horodatée ou un nouveau protocole scientifique. Les contrôles #1397–#1405 utilisent des originaux et/ou signatures **fabriqués pour les tests**. Aucune nouvelle vie, aucun World, aucune graine physique de Stage6 et aucun dépositaire extérieur ne sont créés ici.

Sources de référence : [méthode v1 non exécutable](STAGE6_LIGHT_PROTOCOL_METHOD_V1.json), [vérificateur signé #1405](../../../lab/stage6_light_signed_custody_preflight.py), [préflight source #1398](../../../lab/stage6_light_checkout_source_preflight.py), [audit originaux #1401](../../../lab/stage6_light_original_selection_bridge.py), [audit actions/ressources #1404](../../../lab/stage6_light_trace_funding_preflight.py), [ADR-0017](../../../../../docs/decisions/ADR-0017-i3-moratoire-deux-phases-repetition-scellee.md), [issue Stage6 #1395](https://github.com/josselin-orta-lab/individual-zero/issues/1395) et [issue M11 #1339](https://github.com/josselin-orta-lab/individual-zero/issues/1339).

## 1. Décision de priorité et falsificateur

**DRIFT DETECTED :** des vérifications synthétiques successives renforcent la cohérence des octets mais n'observent ni tiers dépositaire réellement indépendant, ni première publication antérieure aux expériences, ni sélection et vie exécutées. **Arrêt recommandé des nouveaux prévols synthétiques de même portée** tant qu'un apport externe n'est pas disponible. Ne pas transformer des tests logiciels verts en preuve de terrain.

**Question opérationnelle falsifiable :** un opérateur indépendant des deux magasins de l'émetteur peut-il retenir de façon irréversible, *avant toute exposition autorisée*, une empreinte du préengagement et ensuite la haute-eau de chacun des neuf scellés, de sorte que la restauration complète des systèmes du laboratoire **et** du service de signature ne permette pas de présenter silencieusement une histoire plus ancienne comme la dernière histoire valide ?

Un seul cas de rollback non détecté, d'altération du premier instant de réception, de publication à embranchement non détectée, de source différente, de privilège partagé non déclaré, de panne qui déclenche un rejeu de vie, ou de levée d'autorité implicite entraîne `FAIL / STOP`. Un opérateur qui n'existe pas ou ne fournit pas son inventaire produit `NOT_RUN`, **jamais PASS**.

## 2. Trois domaines de confiance et responsabilités encore non attribuées

| Domaine | Responsabilités | Il ne doit pas contrôler | Preuve minimale indépendante |
| --- | --- | --- | --- |
| **A. Producteur I3** | Code exact, identité de l'étude, allocations futures après autorisation, dossiers d'originaux, reçus de phases, chaîne du producteur | Clé privée du témoin, horloge témoin, registre monotone C, politiques de rétention C | SHA Git/code/transport, journaux d'exécution scellés, auteur technique et identité du rôle producteur |
| **B. Témoin externe** | Authentifier la demande, constater la première réception, signer l'engagement, publier reçus et conflits; pas de décision du Mind | Exécuter le moteur, forcer une action, activer une cohorte, supprimer la haute-eau C | Identité juridique/administrative distincte, clé publique Ed25519 épinglée indépendamment, identité endpoint/CA, journaux d'admission |
| **C. Conservation monotone protégée** | Enregistrer de façon append-only la première observation et chaque nouvelle haute-eau avec ordre, date, hash et provenance du témoin; préserver une copie consultable | Pouvoir être restauré ou effacé par les administrateurs A **ou** B sans détection indépendante | Politique d'immutabilité et de rétention effectivement appliquée, inventaire IAM et sauvegardes, négatifs rollback/revocation, preuve d'horloge |

Une signature et un serveur distant **ne prouvent pas** que B et C sont administrativement indépendants. Même un HSM peut signer une ancienne histoire si toute la haute-eau externe a été réinitialisée. Deux clés différentes possédées par la même personne **ne satisfont pas** la séparation. Les noms de domaines A/B/C décrivent des responsabilités à vérifier, pas des acteurs déjà nommés.

**Convergence sans confusion :** l'architecture off-host du [gate I3/M11](../../engineering/OFFHOST_M11_INDEPENDENCE_RELEASE_GATE_2026-11-13.md) décrit le même risque de contrôle commun, mais une preuve de préengagement Stage6 n'est **pas** un M11 natif de récupération. Les deux usages doivent avoir leurs espaces de noms, autorités, séquences, clés et décisions propres. Aucun GO M11 ni Stage6 ne peut être déduit de l'autre.

## 3. Dossier prospectif à fixer avant toute première exposition

Ne **pas** remplir les cases ci-dessous à partir d'une expérience déjà exposée. Les valeurs futures doivent être déterminées sur la **source exacte et autorisée**, puis reçues et protégées par C avant un quelconque World.

| Pièce obligatoire | Provenance et vérification | Situation au 15 novembre 2026 |
| --- | --- | --- |
| Décision propriétaire sur la variante G/S/R d'ADR-0017 | Nouvelle décision explicite signée/consignée, portée source et indices définis, sans dériver de cette PR | **ABSENTE** |
| Admission de répétition d'ingénierie et levée scientifique distinctes | Deux décisions spécifiques; jamais une simple PR, signature de données ou demande « poursuivre » | **ABSENTES** |
| Référence méthode/autorisation | Méthode v1 figée + version de **nouveau contrat d'admission séparé** si ultérieurement approuvée | **v1 DENY-ALL uniquement** |
| Code exact et transport | Objet Git, arbres de fichiers, hashes des exécutables, dépendances et transport, attestés contre les octets et la chaîne de build | **Dossier exécutable Stage6 non admis** |
| Identifiant de campagne et allocations | Run ID prospectif, 16 populations, 288 emplacements logiques, 384 fondateurs; graines réelles **non attribuées aujourd'hui**, disjonction historique/réserve et indépendance contrôlées | **NON ALLOUÉS** |
| Engagement de graines et aléa | Racine de commitment avec domaine de protocole, sels aléatoires à entropie suffisante contre la devinette de petites graines, séparation World/fondateur/vie/parents/mutation; politique de révélation ultérieure | **NON CRÉÉ** |
| Clés et politiques opérateurs | Deux rôles Ed25519, empreinte de la **clé publique** producteur dans le préengagement, CA/endpoint, personnels et IAM séparés, gestion rotation/révocation | **NON CONFIGURÉS** |
| Premier enregistrement immuable | Reçu d'arrivée externe du **préengagement avant l'exposition**, heure de première observation, SHA brute, index monotone, publication vérifiable et politique WORM prouvée | **NOT_RUN** |
| Chaîne G/S/R et originaux | Neuf reçus avec liens aux artefacts exacts et aux originaux, preuves d'exécution indépendantes et scellés de génération, aucune régénération | **NOT_RUN** |

**Attention au contrat #1405 :** `stage6_light_signed_custody_preflight.py` exige expressément que la méthode v1 ait *toutes* les permissions à `false` et tous les indices à `null`. Même avec neuf signatures conformes, il rend `owner_authorization: false` et `STAGE6_LIGHT_NOT_RUN_NO_AUTHORIZATION`. Son succès est une **vérification négative de cohérence** : il ne peut pas être réutilisé tel quel pour admettre une future exécution. Si le propriétaire approuve ultérieurement un transport, son autorisation devra être un **acte distinct, source-épinglé et versionné**, contrôlé par un nouveau gate explicitement revu. Ne jamais rendre la méthode v1 permissive sur place ni contourner cette distinction.

## 4. Ordre minimal du dépôt externe, sous réserve d'autorisations nouvelles

1. **Avant ouverture :** le responsable d'A déclare la source exacte et les plans; un responsable distinct de B examine le domaine, la clé de publication et le rôle autorisé; C reçoit la preuve de politique de conservation monotone et ses administrateurs indépendants.
2. **Préengagement :** uniquement après les décisions adéquates, B reçoit les octets canoniques et signe le préengagement; C conserve **avant** toute exposition les octets, SHA, index, identité et heure de première réception via une écriture dont l'ACK est conditionné à la durabilité. Le producteur ne peut ni attribuer rétrospectivement l'heure ni fournir lui-même le « reçu externe ».
3. **Phases :** `G0 → SEAL_G0 → SELECT_G1 → G1 → SEAL_G1 → SELECT_G2 → G2 → SEAL_G2 → R_FINAL`. À chaque étape, vérifier que le scellé précédent est durable dans C **avant** de permettre la suivante; le scellé doit identifier les octets réellement disponibles de sa génération et ses empreintes. Les réducteurs de sélection lisent seulement le champ autorisé par le protocole; le moteur individuel ne reçoit jamais la performance des autres individus.
4. **Retours d'ACK et pannes :** une réponse perdue, un état local/restauré incertain ou un désaccord A/B/C implique **STOP** et inspection en lecture seule. Pas de nouvel essai de vie G, pas de reprise post-mortem, pas de sélection rétroactive, pas de retour sur un état corporel incertain. Les seules réparations éventuelles restent celles autorisées par les textes applicables, sans réécriture des originaux.
5. **Vérification extérieure :** un auditeur indépendant obtient les octets de C directement, sans sélection préalable par A, vérifie sources/manifestes, les signatures, l'ordre, les preuves d'antériorité, l'absence de fork, la disjonction des allocations et **les tests négatifs complets**. Il consigne `PASS`, `FAIL` ou `NOT_RUN` par scénario et par SHA exact.
6. **Aucune promotion implicite :** même une custodie externe PASS n'autorise pas une cohorte, un replay, une activation i3, un statut scientifique positif ni une levée de l'ADR-0017. Les décisions du propriétaire et le protocole de recherche restent des portes séparées.

## 5. Matrice de falsification opérationnelle à exécuter sur infrastructure réellement séparée

| ID | Injection / menace prospective | Résultat requis | État actuel |
| --- | --- | --- | --- |
| C-01 | Premier préengagement soumis **après** l'exposition | Rejet temporel vérifiable, aucune réécriture de la première date | **NOT_RUN** |
| C-02 | Restauration du journal local A, signer valide | Haute-eau C plus récente, **STOP** avant action | **NOT_RUN** |
| C-03 | Restauration simultanée A + base B / service signataire | C refuse le checkpoint ancien malgré une nouvelle signature valide | **NOT_RUN** |
| C-04 | Tentative de restaurer/supprimer C avec droits opérateurs A ou B | Modification impossible ou détectée hors de leur domaine | **NOT_RUN** |
| C-05 | Publication de deux reçus signés divergents pour le même index | Fork publié, conflit conservé, **STOP**, pas de réécriture d'index | **NOT_RUN** |
| C-06 | Clé révoquée, principal étranger, mauvaise CA, source/méthode/transport modifié | Rejet d'identité avant toute persistance utile ou exposition | **NOT_RUN** |
| C-07 | Perte d'ACK après écriture durable, crash, réseau coupé pendant phase G/S | Read-only classification; aucun rerun de vie ou de sélection incertaine | **NOT_RUN** |
| C-08 | Historique de graines, origine ou populations non disjoints | FAIL de l'allocation; aucun résultat de lignée admis | **NOT_RUN** |
| C-09 | Corpus d'originaux insuffisant, reçu signé sans octets natifs concordants | FAIL sur les originaux, pas seulement SHA de prétention | **NOT_RUN** |
| C-10 | Retour serveur récent mais empreinte « latest » fournie seulement par A | Refus d'indépendance; C doit répondre directement et protéger sa haute-eau | **NOT_RUN** |

**Règle d'arrêt :** une seule cellule `FAIL` bloque la revendication « custodie indépendante ». Une cellule `NOT_RUN` ne peut pas être remplacée par `PASS` local ou par une signature fictive. Un témoin incapable de démontrer la séparation de ses administrateurs reste `NOT_ATTESTED`.

## 6. Handoff à compléter par un véritable opérateur, sans inventer d'identités

- Responsable organisationnel A / instance et environnement : **NON DÉSIGNÉ**
- Responsable indépendant B / hébergeur / clé publique signataire / CA : **NON DÉSIGNÉ**
- Responsable protégé C / produit d'immutabilité / administrateur IAM / durée de rétention : **NON DÉSIGNÉ**
- Preuve de séparation A–B–C, profils IAM, politique réelle de verrouillage et tests de restauration : **NON FOURNIE**
- Adresse horodatage, source d'horloge, publication append-only et accès extérieur d'audit : **NON FOURNIS**
- Source / transport / méthode autorisés par le propriétaire / SHA d'allocations réelles : **NON AUTORISÉS**
- Répétition complète source-exact Python 3.11 et 3.12 : **NOT_RUN**
- Revue indépendance et attestation finale : **NOT_RUN**
- Portée d'une éventuelle levée scientifique / décision propriétaire : **ABSENTE**

**Sortie de cette itération : `OPERATION_NOT_CONFIGURED / NOT_RUN`.** Ce document ne constitue pas une demande de mise en route automatique et n'ajoute aucune clé, configuration d'accès, endpoint ou permission au dépôt. Le prochain acte **utile** dépend d'un opérateur véritable et de ses preuves, non d'un dixième simulacre de chaîne signée.
