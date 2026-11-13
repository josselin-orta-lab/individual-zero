# I3 · Étape 6 légère : transport G/S/R numérique, préflight sans World (13 novembre 2026)

**Statut : `SYNTHETIC_PLUMBING_CHECK_ONLY`, `NO_WORLD_NO_LIFE`, `NO_SCIENTIFIC_ADMISSION`.** Cette étape met à l'épreuve la plomberie du [protocole méthodologique v1](STAGE6_LIGHT_PROTOCOL_METHOD_V1_2026-11-13.md), **sans** autoriser de nouvelle vie, sans exécuter le Mind, sans instancier de `World` et sans attribuer de graine ou d'indice. Elle ne remplace pas une répétition scellée à pleine échelle, ni un transport scientifique.

## Réalisation technique

Le module [`stage6_light_synthetic_transport.py`](../../../lab/stage6_light_synthetic_transport.py) n'importe **aucun module I3**, seulement la bibliothèque standard. Il n'a ni commande d'exécution vivante, ni appel au moteur, ni fonction qui délivre un ticket d'admission. Toute tentative de `run_life`, `open_world` ou `authorize_science` lève `PermissionError`. Il lit le manifeste v1 original en lecture seule et refuse toute autorisation passée à `true`, tout SHA/indice injecté à la place de `null`, ainsi que tout changement de statut du protocole.

Le calendrier symbolique énumère les **288 coordonnées logiques** de mondes et **384 positions** de fondateurs, avec **aucune graine affectée**. Les domaines de tirage parent/mutation comprennent chacun **1 536 positions futures** ; l'espace de graines de vie comprend 288 positions. Des nombres fabriqués dans les tests servent à détecter les doublons et les recouvrements manifestes avec les intervalles historiques connus ; ils ne sont **ni enregistrés ni revendiqués comme une allocation prospective réelle**. L'indépendance statistique et l'exhaustivité de la disjonction restent **`NOT_VERIFIED`**.

Le prototype accepte des **reçus jouets** strictement estampillés `TOY_ONLY_NO_WORLD`. Chaque reçu contient uniquement un identifiant logique, un compte de pas inventé et un booléen de censure, sans corps, trajectoire, coût, récompense, mémoire ni résultat du Mind. Le test construit la matrice logique complète de **2 304 reçus G0 + 4 608 reçus G1 + 4 608 reçus G2 = 11 520 reçus fictifs**, sans produire une seule vie réelle. À G0, les deux bras partagent **la même source** de reçus, sans duplication.

La machine suit : `G0 → S1 → G1 → S2 → G2 → R_FINAL`. Après chaque génération, elle vérifie l'exhaustivité, la censure, les coordonnées et les doublons ; elle trie et calcule un SHA-256 local du jeu synthétique. Le sélecteur lit **uniquement** la censure et les pas fictifs du bras `selected` pour choisir des parents selon les poids linéaires 24…1 et la priorité `(censures, pas, slot)`. Le bras `random_parent` procède à un tirage jouet uniforme **sans consulter son aptitude**. L'unique sortie de sélection contient les emplacements de parents et une empreinte, jamais leurs scores. Toute corruption des reçus ou du choix, tentative de reprise ou appel hors ordre clôt définitivement cet objet de test.

Une table artificielle de 16 contrastes G2 et trois sentinelles teste, **sans inférence**, le seuil bilatéral 13/16, les zéros conservés au dénominateur, le cas nul, le cas opposé et l'invalidation lorsque deux sentinelles concordent. Les sorties s'appellent toujours `TOY_*`, déclarent `science_verdict=NOT_ISSUED` et n'utilisent ni génome réel ni résultat expérimental.

## Couverture des tests et falsificateurs

[`test_stage6_light_synthetic_transport.py`](../../../../../tests/i3/test_stage6_light_synthetic_transport.py) vérifie : import sans I3 / absence de CLI scientifique ; garde fermé des autorisations ; énumération des 288 coordonnées ; collisions de graines **fictives** ; cardinalité G0 unique ; chemin G/S/G/S/G/R ; déterminisme sous permutation d'entrée ; refus de reçus manquants, dupliqués, infiltrés ou modifiés ; séquence non rejouable ; corruption des scellés/parents ; seuil positif, nul et zéros ; invalidation par deux marqueurs neutres ; NaN ; refus du moteur et des admissions. **Chaque scénario ne consomme aucune graine de science.**

Commande logicielle sans World, depuis le dépôt :

```bash
PYTHONPATH=src python -m unittest discover -s tests/i3 -p 'test_stage6_light_synthetic_transport.py' -v
```

**Limites expressément conservées :** les empreintes jouets ne sont pas des scellés indépendants, les comptes fictifs ne sont pas des reçus corporels natifs, le tri uniforme n'est pas une démonstration de survie, les racines d'aléa jouets ne sont pas des graines prospectivement attribuées, et les 16 étiquettes de population ne démontrent pas leur indépendance écologique. Aucun test de ce module n'établit un niveau alpha réel ni la puissance du critère 13/16. Il n'existe pas encore de transport vivant source-exact Stage6 et le protocole lui-même reste `METHOD_FIXED_PREAUTH_NOT_EXECUTABLE`.

## Prochaine frontière et règles d'arrêt

Avant tout développement d'un adaptateur vivant, valider **explicitement** avec le propriétaire la variante G/S/R de l'ADR-0017 et vérifier l'autorité nécessaire pour **chaque** ouverture de World (y compris engineering). Un futur transport distinct devra intégrer custodie des reçus énergétiques/vigilance et des scellés originaux, causes d'arrêt, descendance mutée, vrais espaces de seeds disjoints, indépendance des populations et le même pipeline sur Python 3.11/3.12, puis obtenir une levée source/index propre **avant** la première exposition scientifique. Aucun de ces critères n'est satisfait ou autorisé par ce préflight.

**État inchangé :** I1 actif, I3 référence non enregistrée, P1.3 funded-v2, Stage 2.1 `NOT_ISSUED/HOLD_NO_VERDICT`, Stage 6 légère `NOT_RUN_NO_AUTHORIZATION` ; 0 nouvelle vie, 0 nouveau World, 0 nouvelle cohorte, 0 nouvel indice.
