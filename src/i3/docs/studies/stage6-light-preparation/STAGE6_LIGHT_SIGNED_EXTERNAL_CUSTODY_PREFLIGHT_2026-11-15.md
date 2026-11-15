# I3 Stage-6-light : contrôle hors ligne des engagements externes signés (15 novembre 2026)

**Statut : `SIGNED_PHASE_PREFIX_MATCH_ONLY_NOT_INDEPENDENTLY_ATTESTED` ; développement logiciel uniquement.** Ce document spécifie le vérificateur en lecture seule [`stage6_light_signed_custody_preflight.py`](../../../lab/stage6_light_signed_custody_preflight.py). Il fait avancer l’exigence d’une preuve de préengagement et de chronologie G/S/R, identifiée dans [#1395](https://github.com/josselin-orta-lab/individual-zero/issues/1395), **sans prétendre que de tels engagements ont eu lieu**. La méthode Stage6 v1 conserve son statut `METHOD_FIXED_PREAUTH_NOT_EXECUTABLE`, et aucune vie, World, cohorte ou graine scientifique n’a été produit ou autorisé.

## Question falsifiable

Étant donné deux **clés publiques épinglées séparément**, un reçu de préengagement signé par la clé du témoin, une suite de reçus de phases signés par une autre clé et deux empreintes de maintien hors du domaine d'exécution, le vérificateur peut-il rejeter un reçu falsifié, un choix de source ou de graines changé après préengagement, une phase hors ordre, une liaison d’artefact fausse, une bifurcation, un rejeu ou une mauvaise autorité cryptographique ?

La vérification compare seulement des **octets fournis**. Elle ne signe rien, ne publie rien, n’ouvre aucune connexion réseau, ne vérifie aucun World et ne calcule aucun résultat scientifique. Les empreintes d’ancrage `retained_precommit_sha256` et `retained_latest_sha256` doivent provenir de registres **réellement distincts** et conservés à l’extérieur de la frontière de restauration du producteur. Un appelant qui les fabrique a posteriori peut satisfaire le logiciel. L’indépendance organisationnelle, le premier instant de publication, la fraîcheur, l’absence de compromission des clés et la non-équivocation ne sont donc **jamais attestés par ce module**.

## Contrat de validation

Deux types de reçus JSON UTF-8 **canoniques** (tri des clés, sans espaces superflus, sans doublons), chacun avec `schema`, `payload` et `signature` Ed25519 base64 canonique. Les signatures portent un séparateur de domaine propre au rôle, puis la représentation canonique de `{"schema": …, "payload": …}` ; aucune clé privée n’est lue ni créée par l’outil de production.

1. **Préengagement témoin `PRECOMMIT`.** Contient `run_id`, `protocol_id`, empreintes brutes de la méthode v1 non exécutable, du code source, du transport prévu, du manifeste d’allocation et de l’engagement de graines, plus les identifiants distincts des deux signataires. Signature de la clé **témoin** ; égalité stricte avec la SHA-256 brute déjà retenue à l’extérieur du producteur.
2. **Journal de phases du producteur.** Une entrée par phase, en préfixe strict de `G0`, `SEAL_G0`, `SELECT_G1`, `G1`, `SEAL_G1`, `SELECT_G2`, `G2`, `SEAL_G2`, `R_FINAL`. Chaque entrée signe un `ordinal` entier strict, la même référence au préengagement, la SHA du reçu précédent, la SHA de l’artefact précédent en entrée et une nouvelle SHA d’artefact. Le premier lien dépend du seul engagement de graines. L’empreinte du dernier reçu doit égaler la haute-eau externe indépendante **prétendue**.
3. **Interdiction inchangée.** Avant d’ouvrir un fichier de preuve, le vérificateur impose le SHA de la méthode v1 locale, ses autorisations toutes `false`, ses champs non alloués tous `null` et les clauses de moratoire ADR-0017. Même une chaîne complète et signée retourne `owner_authorization: false`, `historical_first_exposure_time_attested: false`, `science_verdict: NOT_ISSUED` et `STAGE6_LIGHT_NOT_RUN_NO_AUTHORIZATION`.

Toutes les entrées ont une taille bornée, les clés publiques sont passées explicitement par l’appelant, les identifiants des deux rôles doivent différer, les huit SHA attendues sont obligatoires, le `run_id` est unique **dans la prétention du dossier** mais sa nouveauté ne peut pas être vérifiée contre un dépôt externe. Une signature sur un artefact ne prouve pas que l’artefact provient du moteur ou qu’il contient des observations valides.

## Critères de rejet / menaces

- Octets réécrits, champ supplémentaire, clé JSON répétée, encodage non canonique, signature falsifiée ou mauvaise clé/role.
- Method v1 modifiée ou permission rendue exécutable, clé témoin et producteur confondues, ancrage prétendu absent ou mauvais.
- Identifiant de campagne, SHA source / transport / allocation / graines différents du préengagement ; entrée `SELECT_G1` avant `SEAL_G0`, saut de phase, ordinal `true`, artefact répété, dépendance ou prédécesseur altérés, haute-eau non identique au dernier reçu.
- Impossibilité de satisfaire le contrôle cryptographique en l’absence de deux clés publiques Ed25519 distinctes et de l’empreinte retenue hors dépôt, **sans mode dégradé ni auto-autorisation**.

**Risques non couverts :** les deux clés peuvent appartenir au même acteur malgré leur différence ; un témoin peut signer après exposition ; la rétention externe peut être déclarée sans exister ; un signataire peut publier deux chaînes valides ; un checksum d’allocation ne garantit pas l’indépendance des 16 populations, ni la disjonction des cohortes ; une signature ne prouve ni la création réelle d’une vie, ni l’exécution du code, ni la véracité d’un manifeste d’originaux. Ces limites exigent une autorité réellement indépendante, un registre temporel append-only consultable et les vérifications de sources/originaux déjà distinctes dans i3.

## Transfert opérateur hypothétique, **non autorisé par ce document**

Le propriétaire devra **d’abord** statuer explicitement sur l’adaptation G/S/R de l’ADR-0017, le transport scientifique source-exact, l’allocation indépendante et la nature des autorisations de répétition et de science. Un véritable tiers dépositaire devra alors publier **avant toute exposition** la SHA du préengagement et une preuve temporelle indépendante, protéger sa clé, conserver de manière monotone chaque haute-eau successive, publier les bifurcations et permettre une vérification extérieure. Le producteur doit fournir les octets exacts de chaque phase, les artefacts source-exacts associés et les originaux natifs scellés. Aucune de ces actions n’a été réalisée dans ce chantier.

## Tests et limites de résultat

[`test_stage6_light_signed_custody_preflight.py`](../../../../../tests/i3/test_stage6_light_signed_custody_preflight.py) construit **uniquement** des dossiers fictifs et des clés Ed25519 de test éphémères. Quatorze tests (dont un contrôle supplémentaire de la méthode réelle en CI) couvrent signatures, ordre, préfixes, dépendances, haute-eau, schémas et garde des permissions. Un jeu de neuf reçus artificiels qui passe n’est **pas** une attestation scientifique ; il prouve seulement la cohérence cryptographique de ses propres déclarations. La suite GitHub Python 3.11 et 3.12 sur le commit exact reste obligatoire avant fusion.

**Statuts invariants :** i1 moteur actif, i3 référence non enregistrée, P1.3 funded-v2 inchangé, Stage2.1 `NOT_ISSUED/HOLD_NO_VERDICT`, Stage6 `STAGE6_LIGHT_NOT_RUN_NO_AUTHORIZATION`. Aucune admission, aucune allocation, aucune nouvelle exposition, aucun résultat adaptatif.
