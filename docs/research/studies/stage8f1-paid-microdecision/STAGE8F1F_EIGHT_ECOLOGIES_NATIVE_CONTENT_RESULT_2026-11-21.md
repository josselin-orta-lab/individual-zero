# Stage8-F1F · contenu personnel payé, divergence motrice dans 1/8 écologies

**21 novembre 2026, résultat du critère préenregistré : `MEAN_CONTENT_MOTOR_EFFECT_IN_K_OF_EIGHT_PREREGISTERED_ECOLOGIES`, avec K=1 et 8/8 conditions valides.** Pour la première fois dans cette série de tests *logiciels et synthétiques*, la moyenne d'une conséquence personnellement vécue et réellement payée influence une **commande motrice ultérieure**, à coût cognitif strictement apparié au sein de chaque contexte. **Aucun gain adaptatif, aucune persistance, aucune généralisation statistique et aucune conclusion concernant les vrais G2 ne sont démontrés.**

## Provenance et critères fixés avant toute vie native F1F

Le [protocole F1F](STAGE8F1F_ECOLOGICAL_CONTENT_PREEXPOSURE_2026-11-21.md) a été déposé au commit `e9b86a2a9730ceb3c89b5380b471b20b0c152f85`, avant la création du premier reçu expérimental F1F. Le [protocole distinct F1G TD/buffer](STAGE8F1G_SEPARATE_TD_BUFFER_PREEXPOSURE_2026-11-21.md) a également été déposé à l'avance, au commit `82d3dc015b5d89ce52b1abc632e7a6a1a52d01b7`. Base du code `77c3e3395dfa379851d6192a7ec09968727c9ed9`, [PR #1491](https://github.com/josselin-orta-lab/individual-zero/pull/1491).

Source racine F1C [CI #44837981694](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44837981694), artefact natif #14679910820, `F1C_PAID_NATIVE_ORIGINAL.json`, **125436 octets**, SHA256 `e46ad5f54af49796da65f48d603595544116aa6e73632546b0935d2178c5e91d`. Elle contient une action `dormir` librement choisie, débitée, suivie d'un apprentissage réellement exécuté et acquitté : **0,1096 énergie + 0,174 vigilance**. L'état mental postapprentissage complet est scellé et reproduit bit à bit avant tout essai écologique. Le prior avant ce premier tick reste **une observation synthétique**, non un instantané historique de G2.

## Construction native et contrôle de décision autonome

Huit vrais `WorldSpec` de développement 3×3, quatre chemins eau, deux cas alimentaires et un cas mixte, plus un témoin sans ressources. Les ressources sont **stockées à quantité zéro au tick 0** et révélées **au tick 1** par des `WorldSpec.changes` natifs, après la même expérience initiale F1C. Cela garantit à l'individu le **même `World.capture` initial et exactement la même mémoire personnelle finale payée** dans les huit écologies, tout en variant réellement la perception des cases et des ressources avant le choix suivant. Aucune règle n'impose `dormir`, `boire`, d'exploration ou de déplacement.

Pour chaque monde, trois bras prennent séparément une décision native : `full` (moyennes personnelles authentiquement apprises), `sham` (intervention de lecture neutre), `mask_both` (masquer temporairement les deux moyennes `dormir` et `*` par les **véritables** moyennes personnelles archivées avant l'apprentissage). **La taille et les comptes de mémoire, les valeurs TD, le buffer, les états RNG et le corps sont appariés.** Après choix et avant le moteur physique, les moyennes réellement apprises sont rétablies. Les 24 commandes motrices ont été exécutées avec leurs vrais `CognitiveWork` par `World.step`.

**Règle primaire** : compter K, parmi les huit comparaisons `full`/`mask_both`, le nombre de `(action,param)` différents **uniquement si** toutes les huit factures et tous les contrôles `sham` sont strictement appariés. Sinon `INCONCLUSIVE_ECOLOGY_COST_GATE`. Cette porte a réussi : **8/8 écologies à travail et débit énergie/vigilance égaux au sein de chaque monde**, sans impayé; **8/8 sham neutres**.

## Commandes natives réellement observées

| Contexte préenregistré | Vraie mémoire `full` | Moyennes masquées `mask_both` | Effet moteur |
|---|---|---|---|
| `bare` | déplacement Est | déplacement Est | Non |
| `water_here` | boire | boire | Non |
| `water_north` | déplacement Nord | déplacement Nord | Non |
| `water_east` | déplacement Est | déplacement Est | Non |
| `water_west` | déplacement Ouest | déplacement Ouest | Non |
| `food_here` | déplacement Est | déplacement Est | Non |
| `food_east` | déplacement Est | déplacement Est | Non |
| `mixed_here_water_east_food` | **déplacement Est** | **déplacement Nord** | **Oui** |

Dans le contexte mixte, **eau disponible sur la case (1,1), aliment visible sur la case Est (2,1)**, la véritable mémoire induit `explorer:1,0` et `se_deplacer E`. Lorsque les deux moyennes réellement apprises sont temporairement remplacées, la décision native sélectionne `explorer:0,-1` et `se_deplacer N`, sans jamais changer les options offertes, le corps, la graine ni la facture de cognition. Le `sham` conserve `explorer:1,0` et Est.

**Facture identique dans ce cas décisif :** `CognitiveWork(cycles=4,simulated_steps=101,memory_items=34,replays=0)` ; `World.step` débite **0,2888 énergie et 0,402 vigilance**, sans impayé, dans chacun des trois bras. Corps au départ `[2.9096,74.63,59.6,90.2,98.776]`, après les deux déplacements `[0.6208,74.43,59.2,90.2,98.374]` dans les deux conditions ; seule la **position** change : Est `[2,1]` contre Nord `[1,0]`.

**Mécanisme à interpréter sobrement :** les sorties observables de compétition montrent des scores très proches autour de `explorer:1,0` et `explorer:0,-1`. Pour `full`, les premiers scores affichés sont ≈ **−0,378790**, contre ≈ **−0,389037** en `mask_both`; `boire` devient également plus compétitif dans le masque. Ce changement modifie le vainqueur de la compétition de choix. Il est sensible à cette configuration écologique et aux quasi-égalités de scores; cela **ne démontre pas** une préférence robuste pour Est, ni que le déplacement Est est plus avantageux pour l'individu.

## Validation et conservation de preuves

[CI F1F #44892635999](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44892635999) **2/2 jobs PASS** : Python 3.11 a reproduit les **32 `World.step`** natifs par processus (8 premières expériences F1C de source-identique, puis 8×3 décisions) avec un JSON original et une répétition **octet-identique**. **16/16 tests de falsification dédiés PASS**. Un **auditeur indépendant Python 3.12, stdlib uniquement et sans importer `Mind`/`World`**, a reconstitué les huit géographies, les apparitions des ressources, les cinq channels corporels, toutes les factures et **24/24 transitions physiques du second tick**, ainsi que les instantanés privés, les masques et les contrôles neutres.

Artefact source #**14702338615**, `F1F_ECOLOGICAL_ORIGINAL.json` **1 612 315 octets** (répétition identique), SHA256 `f620d1b46ddf269dc368dcd90ba6c93f44f0b6442f8d9e6322440de32e3fbab5`; ZIP original SHA `beacb0da448c0846dca02af0897f3352ace8a4708814ad298a9d2630120d9bb9`. Artefact froid #**14702267579**, `F1F_COLD_ECOLOGY_AUDIT.json` **2 749 octets**, SHA256 `8013f2add1f3eb0190127bb77eac588c95f153f32ba21113302bafa0292e2ac2`, ZIP SHA `f61b595b801e81fe28c1b43533ceaf6009568ec7ebb54d716bae8bd7c8a0a568`. Archive portable indépendante des 90 jours GitHub Actions : `F1F_8_ecologies_paid_memory_evidence_20261121.tar.gz`, SHA `ac62b49686ffaad0bc34b6d7131599255468bad6c581b6e0f03f70f07edd7d0b` et [manifest de garde](STAGE8F1F_NATIVE_ECOLOGICAL_PROVENANCE_MANIFEST_2026-11-21.json). Les fichiers bruts sont fournis en conversation, pas dans Git.

## Décision et limite de généralité

**Le critère causal F1F de modification de commande par la valeur des moyennes personnelles est satisfait dans 1/8 mondes synthétiques préenregistrés, sous strict appariement des coûts.** C'est une **preuve mécanique locale et reproductible**, non une démonstration d'apprentissage adaptatif, de persistance ni de sélection/héritabilité. Les huit mondes sont des conditions déterministes autour d'**une même racine F1C**, et non huit vies indépendantes ou un échantillon statistique d'écosystèmes. On ne convertit pas `1/8` en probabilité universelle ou en gain de survie.

F1D et F1E demeurent négatifs dans leur écologie d'origine; ce résultat **ne les réinterprète pas**. Aucun `run_life`, aucune nouvelle cohorte scientifique, aucun vrai journal G2 reconstruit, aucune admission en moteur de vie. Stage8-E2 causal gamma123 reste **`STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0 / CLOSED_NO_RETRY`**. Poursuite préenregistrée F1G : contrôler **séparément** l'accès aux valeurs TD et au contenu du tampon d'épisodes dans ces **mêmes huit contextes**, sans sélectionner le seul cas positif F1F.
