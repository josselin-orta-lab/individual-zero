# i3 Stage8-E1 : associations exploratoires des 31 gènes, depuis les 32 256 vies originales

**Observation et clôture de lecture seule : 19 novembre 2026, `STAGE8E_POSTHOC_LOCI_DESCRIBED_NO_CAUSAL_VERDICT`.** Aucun résultat scientifique Stage7/8-A/8-B/8-C n'est requalifié. Aucune naissance, World, graine ou mutation n'a été exécutée pour cette nouvelle analyse. Ce rapport est **postérieur** à l'étude d'origine et ne constitue **aucune preuve causale d'un gène**.

## Provenance et garde

- Source scientifique mère : Stage8-C unique [Actions #44320492293](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44320492293), source `a32b7bf50981e0bbaf688e3caf9973525888c05d`, allocation preexposition `bee65ba13a75eca1b283f1558aba2fc5418748aa84c35d8525fe6646b8dd22b6`, résultat positif S−M **+8,675998** pas (borne unilatérale 97,5 % +1,468357), 22+/10−, `CLOSED_NO_RETRY`.
- L'audit préverdict original #44406977082, auditeur SHA `23d0e3eabff0042123c84f4b292a2e4c72cfcc8f`, avait validé les **32 256 corps gzip G0/G1/G2 et 4 608 mutations**.
- Source d'analyse Stage8-E1 séparée, auditable : Git `65dd488c5e76594163efeaa82fd524050e47e5c5`, après succès logiciel Python 3.11/3.12 sur PR #1453 ; l'outil `stage8e_gene_associations_readonly.py` appelle préalablement le vérificateur Stage8-D complet. Aucune fonction de génération, World ou moteur vivant n'est appelée.
- Nouvelle exécution lecture seule [Actions #44505924594](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44505924594), tentative 1, déclencheur `8977f38bd4419e7e365d890235f6732e087e2984`, `completed/success` à 10:33 UTC le 19 novembre. Résultat artifact `stage8e-existing-originals-all-gene-associations-44320492293`, id **14518619277**. Le ZIP complet a été téléchargé et vérifié séparément : SHA-256 **`a99d7ffdc5b6be5545a74110531e4d321c746886e51f04f67c28cc2922f3c51a`**, 22 543 octets. Son JSON unique conserve **les 31 mesures génétiques et les 32 profils populationnels**. Pas de relecture gzip depuis le petit ZIP : cette attestation appartient au runner audit #44505924594.
- Le workflow exécuté a ensuite été archivé **octet pour octet**, sans relance, sous PR #1457 ; son Git blob est `e0b63ec308aa6e6f86be3844521eeb900d0cc68d`.

## Mesure exploratoire, pas nouvelle hypothèse confirmée

Le génome v4 comporte **31 paramètres** : 15 paramètres corporels par canal (`theta/p/w`), dix scalaires (horizons `gamma1..3`, apprentissage, exploration, prudence, réflexion et mémoire), cinq traits de tempérament et `omega`. Ils ont été mesurés **tous**, sans exclusion, pour les **24 génomes descendants de chaque bras S/M/U de G1 et G2**. Chaque gène est normalisé par les bornes génomiques fixées dans `genome.BOUNDS`.

Pour chacun des **32 groupes-populations**, une **seule** moyenne de gène est produite par bras et génération. Pour chaque gène, calculer `Delta_gene[p] = moyenne_G2(S)−moyenne_G2(M)` et le Pearson descriptif avec `Delta_steps[p] = mean_G2_steps(S)−mean_G2_steps(M)`. La corrélation concerne **32 paires de statistiques populationnelles**, pas 24 génomes, 144 vies, 276 paires ni 32 256 corps. Le rang de corrélation absolue, les 32 suppressions une population à la fois et les sous-panneaux P00–P15 / P16–P31 sont **post hoc et non confirmatoires**.

| Gène v4 | Corrélation Pearson n=32 | Shift G1 S−M norm. | Shift G2 S−M norm. | Pearson P00–15 / P16–31 |
| --- | ---: | ---: | ---: | ---: |
| `temperament.exploration` | −0,32479 | −0,02031 | +0,00010 | −0,327 / −0,344 |
| `gamma3` | −0,32361 | −0,03045 | −0,04437 | −0,355 / −0,302 |
| `theta.vigilance` | +0,31616 | −0,01132 | −0,01682 | +0,205 / +0,373 |
| `theta.energy` | −0,30853 | +0,02005 | −0,00285 | −0,247 / −0,347 |
| `temperament.affiliation` | −0,26314 | −0,00101 | +0,01066 | −0,152 / −0,344 |
| `lambda_r` | −0,25837 | +0,02309 | +0,02924 | −0,193 / −0,357 |
| `w.energy` | +0,24569 | +0,05840 | +0,11467 | +0,419 / +0,081 |
| `belief_rate` | +0,24472 | −0,02679 | −0,02084 | −0,338 / +0,563 |
| `p.vigilance` | +0,23828 | +0,00257 | +0,01853 | +0,025 / +0,372 |
| `gamma1` | −0,21351 | +0,00952 | +0,00751 | +0,068 / −0,434 |

Ces dix lignes ne sont **pas** les dix seuls résultats : l'artifact conserve **les 21 autres gènes sans sélection**. Les dix populations S−M négatives **P00, P01, P03, P11, P16, P18, P19, P24, P28 et P31** restent incluses, comme dans l'analyse primaire Stage8-C.

**Ce que l'on peut déduire, et pas davantage :** la covariation est la plus marquée en valeur absolue pour l'exploration du tempérament, `gamma3`, et les seuils `theta.vigilance` / `theta.energy`. Les signes sont cohérents entre les deux moitiés pour ces quatre loci, mais les moitiés sont **un partitionnement de la même campagne**, pas des réplications indépendantes. Le tempérament d'exploration a un **décalage G2 moyen presque nul**, même avec une corrélation dans les populations ; **ne pas le qualifier de trait sélectionné favorable**. `gamma3` présente une différence G2 S−M de **−0,0444 de sa plage normalisée**, mais l'association n'identifie pas une contribution causale de `gamma3`.

**Aucun gène causal identifié.** Le maximum des 31 `|r|` est seulement **0,32479**. Corrélations entre gènes, classement choisi après lecture des vies, histoire d'ascendance partagée, épistasie et un effet de sélection sur les parents empêchent les p-values confirmatoires et toute attribution directe au seul gène. Un faible ou nul décalage de diversité totale à Stage8-D (Pearson −0,05955) reste compatible avec des effets géniques spécifiques, sans en apporter la preuve.

## Voie de falsification causale distincte

Le protocole de conception [Stage8-E2, bloc des horizons `gamma1..3`](STAGE8E2_GAMMA_BLOCK_PROSPECTIVE_CAUSAL_DESIGN_2026-11-19.md) propose une intervention **nouvelle** sur un bloc génomique lié aux horizons de valorisation. Le trio doit être échangé **conjointement**, car `gamma1 ≤ gamma2 ≤ gamma3` rend une permutation isolée de `gamma3` potentiellement invalide. Un éventuel effet futur identifierait au mieux **le bloc comme intervention causale** dans cette étude et non `gamma3` en particulier.

Aucun nouveau World ou génome n'est né, et aucune étude confirmatoire n'est encore admise : pas de source d'expérimentation figée, de graines/Worlds réservés, de répétitions techniques, de reçu ni de nouveau verdict. I1 actif, I3 référence non promue, Stage2.1 `NOT_ISSUED/HOLD_NO_VERDICT`. Provenance `INTERNAL_PROSPECTIVE_NOT_EXTERNALLY_ATTESTED`.
