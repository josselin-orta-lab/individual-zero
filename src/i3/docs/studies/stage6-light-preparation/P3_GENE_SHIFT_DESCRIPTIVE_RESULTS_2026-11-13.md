# I3 — lecture descriptive des génomes de P3 : résultats (13 novembre 2026)

**Verdict technique : `P3_GENE_SHIFT_DESCRIPTIVE_READ_COMPLETE`. Verdict scientifique : `NOT_ISSUED`. Inférence : aucune.** Ce rapport applique une fois la règle gelée par le [préflight](P3_GENE_SHIFT_DESCRIPTIVE_PREFLIGHT_2026-11-13.md) (commit `fdc9c0f7da478a0196bf28ef010bdc0c1e875eed`). Il ne crée aucun World ni aucune vie, ne modifie pas la référence P1.3 et ne vaut ni GO ni autorisation.

## 1. Intégrité

| Contrôle | Résultat |
| --- | --- |
| SHA-256 de l'archive décompressée | `e45df7a494b01b02846128f5c93b30987a383edd65bd5884d6690740da11103e`, conforme |
| Génomes reconstruits et vérifiés par empreinte | 144 sur 144 |
| Génomes G2 identiques à l'enregistrement gelé | 48 sur 48 |
| Génération 0 identique entre les bras | oui |
| Worlds ouverts, vies créées, vies rejouées | 0, 0, 0 |
| Empreinte du rapport canonique | `9206245d59bfdfb08ec71600686810639181541ad34f007fe1bceba4e736987a` |

Le rapport complet est [P3_GENE_SHIFT_DESCRIPTIVE_REPORT_2026-11-13.json](P3_GENE_SHIFT_DESCRIPTIVE_REPORT_2026-11-13.json). Il est produit par [p3_gene_shift_descriptive.py](../../../lab/p3_gene_shift_descriptive.py), commit `4474d997674e52476103149bc3dd313811aa4fc7`.

**Écart de procédure, déclaré.** L'ordre prévu était : commit du code, puis lecture. La lecture a eu lieu au premier passage des tests, avant ce commit, parce que le test affiche le rapport. La règle était déjà gelée et le code n'a pas été modifié après la lecture : les huit tests ont passé au premier passage et le fichier commité est celui qui a été exécuté. L'ordre des commits ne permet pas de le prouver ; c'est une déclaration.

## 2. Quantité principale : `beta_u_eff` à G2

`beta_u_eff` est le poids de curiosité exprimé par la référence, sur une étendue possible de 0 à 3.

| Population | G0 (les deux bras) | G2 `selected` | G2 `random_parent` | Contraste `C_2` | Contraste `C_1` |
| --- | --- | --- | --- | --- | --- |
| 0 | 1,236 | 0,924 | 1,268 | -0,343 | +0,237 |
| 1 | 1,028 | 0,973 | 1,492 | -0,519 | -0,135 |
| 2 | 1,336 | 0,946 | 1,312 | -0,367 | +0,165 |
| 3 | 0,763 | 0,602 | 0,874 | -0,272 | -0,250 |

- **`C_2` : accord de signe 4/4, négatif.** Moyenne -0,375, écart-type entre populations 0,104.
- `C_1` : 2 positifs et 2 négatifs. Moyenne +0,004, écart-type 0,234.
- Dérive de G0 à G2 dans le bras `selected` : -0,312, -0,055, -0,390 et -0,161. Dans le bras `random_parent` : +0,031, +0,464, -0,023 et +0,111.

**L'attente déclarée avant lecture n'est pas vérifiée.** Le préflight attendait un contraste positif dans la majorité des populations. Il est négatif dans les quatre. Conformément au préflight, ce résultat n'est ni corrigé ni expliqué par une seconde analyse.

## 3. Quantité secondaire et marqueurs neutres, à G2

| Quantité | `C_2` par population | Signes | Moyenne | Écart-type |
| --- | --- | --- | --- | --- |
| `beta_u` normalisé (secondaire) | -0,074 ; +0,223 ; -0,067 ; -0,403 | 1 positif, 3 négatifs | -0,080 | 0,256 |
| `temperament.affiliation` (neutre) | +0,354 ; +0,261 ; +0,229 ; -0,153 | 3 positifs, 1 négatif | +0,173 | 0,224 |
| `temperament.reward_sensitivity` (neutre) | -0,133 ; +0,431 ; +0,244 ; -0,284 | 2 positifs, 2 négatifs | +0,064 | 0,330 |

Aucun des deux marqueurs neutres ne présente d'accord de signe 4/4, comme attendu. Leurs contrastes par population atteignent pourtant 0,2 à 0,4 fois l'étendue du gène, alors que ces gènes n'ont aucun effet.

## 4. Multiplicité

Cette lecture n'était pas prévue mot pour mot par le préflight. Elle est ajoutée pour limiter la portée du résultat, pas pour l'étendre.

À G2, 4 quantités sur 31 présentent un accord de signe 4/4, la quantité principale comprise. 17 présentent 3 contre 1, et 10 présentent 2 contre 2. Si les signes étaient tirés au hasard, on attendrait en moyenne 3,9, 15,5 et 11,6 **(hypothèse d'indépendance entre quantités, qui n'est pas exacte)**. **Au regard du seul critère admis, l'accord de signe, la quantité principale ne se distingue donc pas du bruit à cette échelle.**

Une régularité doit être signalée sans être interprétée. Les quatre contrastes de la quantité principale sont proches les uns des autres : écart-type 0,104 pour une moyenne de -0,375. Le préflight n'autorise aucun test sur cette régularité, et quatre populations ne permettent pas d'en juger. Elle justifie seulement de garder `beta_u_eff` comme quantité principale du futur protocole.

## 5. Généalogie et bornes

| Bras | Ancêtres G0 distincts des 6 génomes G2, par population | Part du premier ancêtre | Parents G1 distincts |
| --- | --- | --- | --- |
| `selected` | 4 ; 1 ; 4 ; 3 | 0,33 ; 1,00 ; 0,50 ; 0,50 | 4 ; 2 ; 4 ; 4 |
| `random_parent` | 4 ; 3 ; 4 ; 2 | 0,33 ; 0,67 ; 0,33 ; 0,83 | 4 ; 3 ; 5 ; 4 |

Après deux tours, les six génomes d'une population descendent de un à quatre fondateurs, dans les deux bras.

À G2, la part des génomes exactement à une borne atteint 37,5 % pour un gène (`theta.vigilance`, bras `random_parent`). Pour `beta_u`, elle est de 8,3 % dans le bras `selected` et de 4,2 % dans le bras `random_parent`.

## 6. Ce que ce résultat change

La décision visée était le dimensionnement du protocole de l'étape 6 légère. Quatre conséquences en découlent. Ce sont des choix de conception proposés, pas des résultats.

1. **Le critère doit rester bilatéral.** La direction attendue était fausse. Le protocole ne doit pas présumer que la persistance augmente la curiosité. L'argument du « témoin positif » est à reformuler : que l'absence de curiosité soit létale n'implique pas qu'une curiosité plus forte aide.
2. **Six génomes par population ne suffisent pas.** Avec un à quatre fondateurs restants, l'échantillonnage des fondateurs domine. Un contraste de 0,2 à 0,3 fois l'étendue du gène ne porte aucune information à cette taille, puisque des gènes sans effet en produisent autant.
3. **Augmenter le nombre de populations ne suffit pas.** Il faut aussi des populations plus grandes et davantage de générations. Leur choix doit s'appuyer sur un modèle nul de dérive, calculable sans aucune vie, et non sur une valeur arbitraire.
4. **Une seule quantité principale, déclarée d'avance.** Avec 31 quantités, des accords de signe complets apparaissent par hasard. Les parts aux bornes doivent être rapportées.

## 7. Ce que ce résultat ne dit pas

- Il ne dit pas que la sélection réduit la curiosité. Quatre populations ne permettent aucune inférence, et la section 4 montre qu'un accord de signe complet apparaît aussi par hasard.
- Il ne dit pas que la sélection par la persistance façonne l'inné, ni qu'elle ne le façonne pas. La thèse centrale de l'ADR-0014 reste non observée.
- Il ne dit rien du gène ω, absent du génome v3 de P3.
- Il ne vaut pas pour d'autres mondes que les familles F0 de P3.

## 8. Handoff

| Rubrique | Contenu |
| --- | --- |
| Génération | I3, proposition non enregistrée |
| Base | `main` = `24dadc509e3a96339def0ddb5f68c257feeabf08` |
| Commits | préflight `fdc9c0f7da478a0196bf28ef010bdc0c1e875eed` ; code et tests `4474d997674e52476103149bc3dd313811aa4fc7` ; ce rapport dans le commit suivant |
| Fichiers | ce dossier ; `src/i3/lab/p3_gene_shift_descriptive.py` ; `tests/i3/test_p3_gene_shift_descriptive.py` ; une entrée dans `README.md` et dans `STATUS.md` |
| Invariants | aucun fichier de `modules/` ou de `runtime/` ; ni registre, ni `engine.json`, ni `ACTIVE_SURFACE.json`, ni ADR, ni protocole figé, ni original |
| Tests | `tests/i3/test_p3_gene_shift_descriptive.py` : 8 tests PASS en Python 3.12.3, en local. Python 3.11 : NOT_RUN, interpréteur absent. CI GitHub : NOT_RUN, aucun accès en écriture depuis cet environnement. Suite I3 complète : voir le message de handoff. |
| Statut scientifique | Inchangé. Étape 2 `NOT_ISSUED`, référence P1.3 funded-v2, I3 non enregistré. |
| Prochaine étape falsifiable | Modèle nul de dérive sans vie, puis protocole de l'étape 6 légère |
