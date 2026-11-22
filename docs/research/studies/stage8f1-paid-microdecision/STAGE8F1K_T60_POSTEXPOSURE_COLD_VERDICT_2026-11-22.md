# Stage8-F1K T60 : resultat postexposition, controle froid et diagnostic natif

**Enregistre le 22 novembre 2026 apres la premiere et unique exposition scientifique K01..K16. Document POSTEXPOSITION ; ne modifie ni la grille et le protocole preenregistres, ni les resultats anterieurs.**

## Verdict verrouille par le protocole

**`INCONCLUSIVE_NO_REAL_SURCHARGE`**. Le seul surcout de competition qualifiant a T5 est celui de **K06** dans `near_shallow_then_dry` : **1/16 origine et 1/4 ecologie**. Seuil preenregistre indispensable : au moins quatre origines dans au moins deux ecologies, avec cycle supplementaire effectivement execute et facture payee en energie ET vigilance. Porte non franchie : les criteres de valeur adaptative ne peuvent pas etre valides ou requalifies apres observation, meme quand les trajectoires comportent des pertes nettes.

Reference scientifique : [protocole preexposition F1K](STAGE8F1K_HELDOUT_POLICY_VALUE_PREEXPOSURE_2026-11-21.md), publie avant exposition, blob Git `f551f751eab04e58c93f432662c3181721228b13` ; [grille reservee F1K](STAGE8F1K_HELDOUT_POLICY_VALUE_GRID_2026-11-21.json), blob `bae149207c1fc41fb7fcc6fff11462e03dd17407`.

## Custodie et audit

- [GitHub Actions run #45005079265](https://github.com/josselin-orta-lab/individual-zero/actions/runs/45005079265) : `workflow_dispatch`, `run_attempt=1`, commit source `1a01360ddeb709944bc14f03d9f6a7fc5f075163`, trois jobs PASS (reservation et production native, audit froid Python 3.12 sans moteur, publication de la Release).
- [Release scientifique F1K](https://github.com/josselin-orta-lab/individual-zero/releases/tag/i3-stage8f1k-t60-heldout-once) : `immutable=true`, ressources originales et froides ; le tag est attache au commit de reservation `fcd1b048b63c03d4486ee2bb32444a148bed0ea8`.
- Reservation Git atomique avant tout `World.step` sur `refs/heads/i3-stage8-f1k-heldout-consumed-once`, marqueur et verrou exclusif de premiere execution conserves ; aucune seconde execution native K autorisee.
- **64/64 gzip** (16 sources P1.3, 16 references P1.3, 16 shams, 16 politiques F1J) controles en lecture seule contre les doubles SHA-256 compresses et decomprimes du manifeste original. Controle de l'empreinte du tar 64 gzip et identite en octets JSON entre original et relecture canonique.
- Empreinte SHA256 du JSON natif original : `852afc7d7b9f1fa1925ceede2fb6502a4f49cfeed3dd11845bd15126dea4c778` ; empreinte de provenance froide : `670635c9859c590866af7c651bd53b2bf10a86207c5412b3c0ca5ee88ec15ea7`.
- L'audit froid a verifie **2501 transitions natives** et **1871 tours de competition**, avec 56 boissons et 29 repas natifs. Source personnelle valide, trois bras valides, 16 controles sham neutres et 16 origines conservees.

## Resultats descriptifs ITT sur les 16 origines

**0 gain de survie F1J, 14 egalites et 2 pertes** : K03 (-38 ticks), K09 (-36 ticks), soit -74 ticks au total et -4,625 ticks par origine en moyenne descriptive. **5/16 actions T5 differentes**, aucun gain de dominance corporelle a cinq canaux par F1J, trois dominances de P1.3, six compromis corporels mixtes et une egalite totale ; six paires classifiees `NOT_EQUAL_SURVIVAL` car morts avant T60 ou survies differentes. Aucun score composite ni p-value ne remplace la porte echouee.

| Origine | Ecologie | Ticks P1.3 | Ticks F1J | Delta | Action T5 P1.3 -> F1J | Surcout qualifiant |
|---|---|---:|---:|---:|---|---|
| K01 | east_distant_sparse | 56 | 56 | 0 | boire -> se_deplacer:S | non |
| K02 | east_distant_sparse | 56 | 56 | 0 | boire -> se_deplacer:W | non |
| K03 | east_distant_sparse | 56 | 18 | -38 | boire -> se_deplacer:W | non |
| K04 | east_distant_sparse | 56 | 56 | 0 | boire -> se_deplacer:S | non |
| K05 | near_shallow_then_dry | 41 | 41 | 0 | collecter -> collecter | non |
| K06 | near_shallow_then_dry | 42 | 42 | 0 | se_deplacer:E -> se_deplacer:E | oui |
| K07 | near_shallow_then_dry | 40 | 40 | 0 | collecter -> collecter | non |
| K08 | near_shallow_then_dry | 42 | 42 | 0 | collecter -> collecter | non |
| K09 | bitter_food_far_well | 56 | 20 | -36 | se_deplacer:S -> se_deplacer:W | non |
| K10 | bitter_food_far_well | 56 | 56 | 0 | se_deplacer:W -> se_deplacer:W | non |
| K11 | bitter_food_far_well | 56 | 56 | 0 | se_deplacer:S -> se_deplacer:S | non |
| K12 | bitter_food_far_well | 56 | 56 | 0 | se_deplacer:S -> se_deplacer:S | non |
| K13 | replenishing_well_remote_food | 56 | 56 | 0 | se_deplacer:S -> se_deplacer:S | non |
| K14 | replenishing_well_remote_food | 56 | 56 | 0 | se_deplacer:S -> se_deplacer:S | non |
| K15 | replenishing_well_remote_food | 56 | 56 | 0 | se_deplacer:N -> se_deplacer:N | non |
| K16 | replenishing_well_remote_food | 56 | 56 | 0 | se_deplacer:S -> se_deplacer:S | non |

## Diagnostics originaux : deux morts par privation d'eau

- **K03, `east_distant_sparse`** : avant T5, les deux politiques possedent le meme etat corporel et se trouvent sur une case d'eau. P1.3 choisit **boire** a T5, boit une fois et vit jusqu'a T60 (56 ticks). F1J choisit **se_deplacer:W** a T5, ne boit jamais et meurt a T22 de `zero_water` (18 ticks). Surcout T5 absent : **4 cycles** et facture native identique dans les deux bras (**0,2594 energie ; 0,366 vigilance**). La source d'eau reste disponible au deces F1J, mais la strategie n'y accede pas.
- **K09, `bitter_food_far_well`** : P1.3 choisit **se_deplacer:S** a T5, atteint le puits et boit deux fois a T9 et T10, vivant jusqu'a T60 (56 ticks). F1J choisit **se_deplacer:W**, ne boit jamais et meurt a T24 de `zero_water` (20 ticks). Surcout T5 absent : **4 cycles**, facture identique (**0,2416 energie ; 0,348 vigilance**). Le puits conserve encore du stock dans la branche F1J.
- Dans ces deux histoires, la **politique de competition change la decision et la trajectoire**, sans cycle supplementaire T5. Ce sont des signaux corporels locaux defavorables, PAS une preuve que le **calcul supplementaire** a provoque la mort, ni une validation statistique d'inferiorite generale.
- **K06** est la seule source avec vrai surcout T5 (**5 cycles P1.3 contre 6 F1J**, energie 0,2384 contre 0,2584 et vigilance 0,376 contre 0,426). La commande initiale reste identique et les deux branches meurent a T46 de `zero_water`, avec 42 ticks chacune.

## Limites et consequences scientifiques

1. Resultat de methode important : le test DEV_R T60 montrait 16/16 surcouts T5 ; les mondes K preenregistres n'en montrent qu'1/16. Cette forte diminution de la **couverture du surcout** empeche le test principal de gain net de la deliberation, sans modifier les graines ni les criteres apres coup.
2. Les pertes observees et les decisions modifiees rendent plausible un cout adaptatif de certaines bifurcations dues a la politique F1J, MAIS le verdict F1K reste **`INCONCLUSIVE_NO_REAL_SURCHARGE`**. Toute nouvelle etude sur la valeur de la selection des actions a calcul egal ou sur la couverture du surcout doit avoir une nouvelle population independante, nouvelle preregistration et sans relance ni tuning sur K.
3. **Ecart d'implementation publie avant exposition** : le protocole initial envisageait une seconde reproduction technique native en octets. Le transport scientifique final utilise une unique production native K, suivie d'une relecture canonique et d'un audit froid, les deux productions natives restant limitees au DEV_R. Ne pas assimiler cette relecture a une deuxieme execution native. Conserver le texte original et sa divergence.
4. Aucun `World.step` K supplementaire, aucune nouvelle execution des graines reservees et aucune correction retroactive de F1I/F1J. Le verdict historique F1I reste `INCONCLUSIVE_COST_GATE`, F1J reste localement `FIXED_ROUND_16_OF_16_REAL_COST_PARITY_DEMONSTRATED_LOCAL`, Stage2 reste `NOT_ISSUED/HOLD_NO_VERDICT`, I1 demeure actif.

Ce document est une **analyse postexposition en lecture seule**, reproductible par relecture des 64 gzip et des rapports d'audit froid publies sur une Release GitHub immuable ; il ne constitue pas une nouvelle exposition ou une promotion scientifique.
