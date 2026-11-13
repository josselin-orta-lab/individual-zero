# I3 — lecture descriptive des génomes de P3 : préflight (13 novembre 2026)

**Statut : PRÉFLIGHT GELÉ AVANT LECTURE.** La règle de réduction ci-dessous est commitée avant toute lecture des valeurs de gènes de l'archive P3 et avant tout code. Ce travail est descriptif. Il ne peut produire aucun verdict scientifique, aucun GO et aucune autorisation de monde.

**Base :** `main` = `24dadc509e3a96339def0ddb5f68c257feeabf08`. **Génération :** I3, proposition non enregistrée. **Référence :** P1.3 funded-v2, inchangée. **Worlds et vies créés par ce travail :** 0.

**Autorités.** L'[ADR-0018](../../../../../docs/decisions/ADR-0018-i3-cloture-etape-1.md) recommande d'avancer une étape 6 légère pour vérifier si la sélection déplace l'inné. L'[ADR-0020](../../../../../docs/decisions/ADR-0020-i3-owner-selected-development-reference.md) §4 délègue la réduction diagnostique d'archives. Ce préflight correspond au chantier RP-B0 de la proposition de feuille de route (PR #1359, non autoritaire) et répond à la demande du propriétaire, le 13 novembre 2026, de poursuivre le développement en la suivant. Il ne consigne ni n'élargit aucune décision du propriétaire.

## 1. Question et décision visée

**Question.** Dans le pilote de lignée P3, la distribution des gènes du bras sélectionné par la persistance s'écarte-t-elle de celle du bras à parents aléatoires ?

**Décision que le résultat peut changer.** Le dimensionnement du protocole de l'étape 6 légère : nombre de populations, nombre de générations, taille des populations, traitement des bornes. Le résultat ne peut changer aucun verdict.

## 2. Source, sans aucune vie nouvelle

- Archive d'origine : [selection-full.json.gz](../p3-mutation-pilot/selection-full.json.gz). SHA-256 du contenu décompressé attendu : `e45df7a494b01b02846128f5c93b30987a383edd65bd5884d6690740da11103e` ([ORIGINAL_SHA256SUMS.txt](../p3-mutation-pilot/ORIGINAL_SHA256SUMS.txt)). Source d'exécution de P3 : `52476fec3f39a7fd70bf611877b01d9c13d26009` ([résultats P3](../p3-mutation-pilot/RESULTS.md)).
- Contenu : 4 populations, 3 générations (G0, G1, G2), 2 bras (`selected`, `random_parent`), 6 génomes par cellule, 864 vies déjà vécues.
- Les 144 génomes sont reconstruits sans exécuter d'individu : G0 par sa graine (`historical_v3_generation_zero`), G1 et G2 par la mutation historique de leur parent (`historical_v3_mutate`, échelle 0,1). Chaque génome reconstruit doit redonner l'empreinte archivée (`genome_sha256`). Les 48 génomes G2 sont aussi comparés à [G2_GENOMES.json](../p3-mutation-pilot/G2_GENOMES.json).
- Aucun `World`, aucun `Mind`, aucun `run_life`. La réserve et la validation de P3 ne sont pas touchées.

## 3. Exposition préalable, déclarée

- Les résultats de survie de P3 et de P4a sont publics et connus.
- Le 12 novembre, une recherche textuelle de navigation a affiché huit valeurs de `temperament.affiliation` du fichier `G2_GENOMES.json`. Ce gène n'a aucun effet dans la référence.
- Aucune valeur de `beta_u`, ni d'aucun autre gène, n'a été lue. La structure de l'archive (noms de clés, tailles) a été inspectée sans afficher de valeur.

## 4. Règle de réduction figée

**Quantités.** Les 30 gènes du génome v3, chacun normalisé par ses bornes : `z = (v - lo) / (hi - lo)`. S'y ajoute une quantité dérivée, non normalisée : `beta_u_eff = beta_u * (1 + 0.5 * temperament.exploration)`, qui est le poids de curiosité réellement exprimé par la référence ([mind.py](../../../modules/mind.py), ligne 116).

**Moyennes.** Pour chaque population `p`, bras `a` et génération `g`, `m(p, a, g)` est la moyenne de la quantité sur les 6 génomes.

**Contraste apparié.** Pour `g` dans {1, 2} : `C_g(p) = m(p, selected, g) - m(p, random_parent, g)`. La génération 0 est identique entre les bras, ce que le script vérifie.

**Résumé par quantité.** Les quatre valeurs `C_2(p)`, le nombre de signes positifs, négatifs et nuls, la moyenne, l'écart-type d'échantillon, le minimum et le maximum. Le même résumé est donné pour `C_1`.

**Dérive dans chaque bras.** `S(p, a) = m(p, a, 2) - m(p, a, 0)`, pour les deux bras.

**Bornes.** Pour chaque gène, la part des génomes dont la valeur est exactement égale à une borne, par bras et par génération, toutes populations réunies.

**Généalogie.** Pour chaque population et chaque bras, le nombre d'ancêtres G0 distincts des 6 génomes G2 (chaîne `parent_slot`), et la part du plus fréquent.

**Hiérarchie déclarée.** Quantité principale : `beta_u_eff` à G2. Quantité secondaire : `beta_u` normalisé à G2. Marqueurs neutres du génome v3 : `temperament.affiliation` et `temperament.reward_sensitivity`, que `Mind.__init__` ne lit pas. Les autres gènes sont rapportés sans commentaire.

## 5. Attente déclarée avant lecture

- `C_2` de `beta_u_eff` est attendu positif dans la majorité des populations. Sans le terme de curiosité, la survie tombe de 110/288 à 4/288 ([P5c](../p5c-paid-score-addends/RESULTS.md)). Un poids faible devrait donc être défavorisé par la persistance.
- Aucun accord de signe systématique n'est attendu pour les deux marqueurs neutres.
- Si ces attentes ne sont pas vérifiées, le résultat est rapporté tel quel. Il n'est ni corrigé ni expliqué par une seconde analyse.

## 6. Ce que cette lecture ne permet pas de conclure

- Avec 4 populations, un test des signes bilatéral exact ne descend pas sous p = 0,125. Aucune inférence n'est possible.
- Chaque population ne compte que 6 génomes et deux tours de sélection. Dans une lignée sans recombinaison, un gène neutre peut suivre un génome gagnant.
- Trente et une quantités sont rapportées sans correction de multiplicité. Aucune ne peut être présentée comme une découverte.
- Le seul libellé admis est « accord de signe k/4 ».

## 7. Falsificateur, contrôles et règle d'arrêt

- **Falsificateur du chantier.** Le travail échoue en `INTEGRITY_FAIL`, sans publier de valeur, dans trois cas : le SHA-256 de l'archive diffère, une des 144 empreintes de génome ne se vérifie pas, ou la génération 0 diffère entre les bras.
- **Contrôles.** Bras `random_parent`, génération 0 appariée, marqueurs neutres.
- **Règle d'arrêt.** Une seule lecture. Le script produit un JSON canonique et son empreinte SHA-256, que le rapport de résultats recopie. Aucune règle n'est ajoutée après lecture. Toute analyse supplémentaire demanderait un nouveau préflight.

## 8. Plus petit test exécutable et coût

- Tests logiciels sans World : `World.__init__` et `run_life` sont interdits par patch, une fixture synthétique est vérifiée contre un calcul à la main, une archive altérée est rejetée.
- Coût : 0 World, 0 vie, calcul négligeable, un module de laboratoire et un fichier de tests.

## 9. Non-revendications

Ce travail n'est ni une revue indépendante, ni une étude préenregistrée d'efficacité, ni une preuve que la sélection façonne l'inné. Il ne rouvre aucune cohorte, ne réutilise aucun indice de monde et ne modifie ni la référence P1.3, ni le registre, ni `ACTIVE_SURFACE.json`.
