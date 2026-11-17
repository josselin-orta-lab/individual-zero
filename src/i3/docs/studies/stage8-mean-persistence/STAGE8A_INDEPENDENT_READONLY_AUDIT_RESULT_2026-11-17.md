# i3 Stage8-A · vérification indépendante des 23 040 vies originales (17 novembre 2026)

**Verdict de l'audit de données : `READ_ONLY_REPRODUCTION_OK`.** La réduction indépendante des originaux retrouve exactement `STAGE8A_MEAN_PERSISTENCE_ADVANTAGE_F0`, le verdict prospectif déjà scellé. L'audit est **POST HOC** et distinct de l'expérience ; il ne modifie ni le protocole ni sa source, ni les graines, ni ses résultats défavorables.

## Sources réelles

| Preuve | GitHub Actions |
| --- | --- |
| Expérience prospective source-exacte | [Run #43950098410](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43950098410), HEAD `ac353a9c4206ee3ecfd90bb101e26d092103958b`, 2026-11-17 01:31:12 UTC |
| Préenregistrement scientifique | Plan SHA `dcd93550453541273c940f78fc459dd3f4deaa807911cb89992c4d1eb7d3b660`, artefact **14278546177**, publié avant les naissances |
| Vies scientifiques originales | Artefact **14289668087** (23 040 gzip), ZIP `d4abb68e809940ef1eab82049e0e1b86c2a62e8c10622740eea45678109503ea` |
| Résultat scientifique original | Artefact **14289613177**, ZIP `5c5bced3b05c0331230811e79bb6ac6155b2ff3f04fc99ad1bcee8c21d017e90` |
| Code distinct de l'audit en lecture seule | [PR #1430](https://github.com/josselin-orta-lab/individual-zero/pull/1430), HEAD `f3e739b0c568391a71ea27e9e25bea2d3df314e0` |
| Exécution et sortie de l'audit | [Run #44042075429](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44042075429), `completed/success`, 2026-11-17 07:56:03 UTC |
| Rapport compact scellé du nouvel audit | Artefact **14309617788**, ZIP 937 octets, `sha256:5ff6a686f259f50433785cd8e13bf58d825915b12c0df165fc396ac15a0afc7a` |

Le vérificateur de [Stage8-A post hoc](STAGE8A_READONLY_INDEPENDENT_ORIGINAL_AUDIT_PLAN_2026-11-17.md) **n'importe pas le réducteur Stage8-A**. Il utilise le lecteur d'archives original existant de Stage7, avec une réduction moyenne Student indépendante, et ne sait ni ouvrir de World, ni calculer les décisions motrices, ni muter un génome ou créer une nouvelle vie. Ses tests synthétiques ont réussi sous Python 3.11 et 3.12 avant la création du job réel. Le job s'est ensuite réellement exécuté sur les artefacts scientifiques originaux, et non sur des fixtures.

## Reproduction exacte (ligne terminale de log du 17 novembre, 07:55:58 UTC)

| Mesure vérifiée | Valeur |
| --- | ---: |
| Gzip originaux et enregistrements rehashés | **23 040** |
| Populations indépendantes *du plan*, analysées | **32** |
| Avantage moyen des descendants G2 sélectionnés, en pas | **+14,487413194444445** |
| Borne Student inférieure unilatérale à 97,5 %, en pas | **+7,993312233799369** |
| Populations positives / négatives / nulles | **23 / 9 / 0** |
| Verdict biologique reproduit | `STAGE8A_MEAN_PERSISTENCE_ADVANTAGE_F0` |
| Contrôle de concordance indépendant | `READ_ONLY_REPRODUCTION_OK` |
| Nouvelles vies créées par l'audit | **0** |

Les SHA-256 des manifestes, des contenus gzip et décompressés, les identités World/génome, les morts (dont morts éventuelles à 400 pas) et censures, les dépenses énergie/vigilance, les 18 phases G/S/R et les valeurs G0/G1/G2 sont contrôlés. Toute discordance aurait rendu le job négatif, pas promu un nouveau résultat scientifique. Le nombre `32` désigne des populations du plan, non une indépendance statistique démontrée.

## Ce que la réussite permet d'affirmer

Les **vies originales archivées**, réduites par un code distinct de celui qui avait réalisé l'analyse de Stage8-A, reproduisent la **même amélioration moyenne G2** et le même critère préenregistré. Le résultat est donc robuste à cette vérification séparée des sommes et des enveloppes archivistiques. Le résultat est borné aux familles F0 du protocole.

## Ce que la réussite ne démontre pas

- **Aucune attestation externe indépendante de la naissance des individus**, ni signature horodatée hors GitHub. Provenance toujours `INTERNAL_PROSPECTIVE_NOT_EXTERNALLY_ATTESTED`.
- **Pas de relecture de la physique et de l'action motrice** par une simulation de contrôle : seules les traces enregistrées et leurs paramètres ont été vérifiés.
- **Indépendance statistique des 32 populations non prouvée** par les seules graines : l'intervalle Student et sa couverture nécessitent des hypothèses supplémentaires.
- **Attribution aléatoire indépendante de l'étiquette de branche non réalisée**, échantillonnage F0 seulement, **9 populations défavorables** conservées sans masquage.
- **Aucune identification causale d'un gène** ou d'une interaction écologique particulière, aucune généralisation hors F0, aucune promotion du moteur i3.

Les résultats Stage6 (gène, 9+/7−) et Stage7 (persistance directionnelle, 12+/4− au seuil 13/16) **restent négatifs selon leurs critères distincts**. Stage8-A positif teste *la moyenne* avec un protocole **nouveau, préenregistré** ; ce n'est ni une correction opportuniste ni un rerun des anciennes populations.

**Gouvernance :** Stage8-A `CLOSED_NO_RETRY`, aucun monde nouveau depuis le 16 novembre ; I1 actif, I3 référence non enregistrée, Stage2.1 `NOT_ISSUED/HOLD_NO_VERDICT`. La rétention actuelle des artefacts de la campagne atteint le **14 février 2027 à 20:28:14 UTC** ; conserver les archives originales sans modification avant expiration.

L'intégralité du rapport scientifique initial reste consignée dans [Stage8-A prospective result](STAGE8A_PROSPECTIVE_SCIENTIFIC_RESULT_2026-11-17.md), et l'enregistrement du nouvel audit figure dans [l'issue scientifique #1427](https://github.com/josselin-orta-lab/individual-zero/issues/1427#issuecomment-6942199008).
