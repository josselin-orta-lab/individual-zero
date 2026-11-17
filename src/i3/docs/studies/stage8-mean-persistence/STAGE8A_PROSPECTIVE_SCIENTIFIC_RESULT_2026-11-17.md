# i3 · Stage8-A · résultat prospectif scellé (17 novembre 2026)

**Verdict scientifique sur le critère primaire : `STAGE8A_MEAN_PERSISTENCE_ADVANTAGE_F0` (succès).**

Ce texte est un **compte rendu de résultats observés après exposition**. Le protocole original [`STAGE8A_MEAN_PERSISTENCE_PROTOCOL_2026-11-16.md`](STAGE8A_MEAN_PERSISTENCE_PROTOCOL_2026-11-16.md), publié *avant* les vies, n'a pas été réécrit. Le résultat prospectif ne doit pas être assimilé à la promotion d'i3, ni à une démonstration hors F0.

## Question, contrefactuel et unités

La sélection de parents selon leur persistance corporelle réellement financée conduit-elle en moyenne à des descendants G2 vivant plus longtemps que ceux issus de parents choisis uniformément au hasard, même lorsque certaines lignées déclinent ?

Le bras `random_parent` n'accède pas aux scores de survie pour ses tirages. Dans chaque génération, les deux bras vivent les mêmes six occasions de mondes F0 (stable, depletion, pulse × deux répétitions), sur la référence motrice P1.3 funded-v2 et les mutations génomiques v4 natives, sans héritage de souvenirs. **Les 32 populations**, pas les individus, génomes ou 400 pas de vie, sont les unités inférentielles. La génération G0 est unique et partagée, G1 et G2 possèdent les deux bras. Les mondes changent entre générations, ce qui interdit d'attribuer causalement une évolution brute G0→G2 à la sélection.

## Exécution réelle, distincte de Stage7

- [GitHub Actions #43950098410](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43950098410), première et seule tentative `run_attempt=1`, source Git exacte `ac353a9c4206ee3ecfd90bb101e26d092103958b`, déclenchée le **2026-11-16 20:28:13 UTC**, terminée `completed/success` le **2026-11-17 01:31:12 UTC**.
- Les jobs `preflight`, `engineering (3.11)`, `engineering (3.12)`, et `science` sont tous `completed/success`.
- Python 3.12 : plan publié **20:28:31 UTC**, reçu technique **22:05:08 UTC**, originaux complets **22:05:17 UTC**.
- Python 3.11 : plan publié **20:28:34 UTC**, reçu technique **22:28:04 UTC**, originaux complets **22:28:16 UTC**.
- Le job scientifique a confirmé les deux reçus **22:28:28 UTC**, puis publié un plan scientifique **nouveau** (`allocation_sha256=dcd93550453541273c940f78fc459dd3f4deaa807911cb89992c4d1eb7d3b660`) **22:28:29 UTC, avant la première vie scientifique**.
- Sa réduction et vérification internes ont abouti au résultat publié **01:30:54 UTC**, puis à l'archive complète scientifique **01:31:09 UTC** le 17 novembre.
- **Chaque transport complet** : 23 040 vies natives (4 608 G0, 9 216 G1, 9 216 G2), 18 phases scellées (9 par panneau), 3 072 tirages parentaux et 3 072 mutations. **Total des trois transports** : 69 120 vies. La science implique un seul ensemble de 32 populations, non 96.

## Résultat principal selon la règle gelée

La méthode prospectivement fixée calcule `D[p]` pour chacune des 32 populations, à partir de la différence entre la moyenne de pas vécus de 144 vies G2 sélectionnées et celle de 144 vies G2 témoins. Puis elle calcule :

```
mean_D = moyenne(D[0], ..., D[31])
sd_D = écart type empirique des 32 D
L = mean_D - 2.0395134463964077 * sd_D/sqrt(32)
```

**Succès** uniquement si `sd_D>0`, `mean_D>0` et la borne `L>0`. Les zéros et les populations défavorables restent dans les estimations.

| Variable | Valeur publiée |
| --- | ---: |
| Population unités | 32 |
| `mean_D` G2 sélectionnés − parents aléatoires | **+14,487413194444445 pas** |
| `L` (borne inférieure Student unilatérale 97,5 %) | **+7,993312233799369 pas** |
| Populations avec avantage strict | **23** |
| Populations défavorables | **9** |
| Verdict primaire | **`STAGE8A_MEAN_PERSISTENCE_ADVANTAGE_F0`** |

Dérivées mathématiques des chiffres arrondis du log, **non analyses confirmatoires supplémentaires** : erreur-type ≈3,18414 pas, écart-type entre populations ≈18,01223 pas, rapport t ≈4,54986, borne haute symétrique d'un intervalle t à 95 % ≈+20,98151 pas. Le test est interprété sous les hypothèses de populations suffisamment indépendantes et de validité raisonnable de Student, non attestées par la séparation des graines seule.

Ces faits valident une **amélioration moyenne de la persistance G2 au sein du plan expérimental F0**, pas une amélioration pour tous les descendants : **9 populations sur 32 restent défavorables**. Ils ne démontrent pas la cause génétique précise, les mécanismes écologiques du désavantage, l'amélioration brute G0→G2, une supériorité générale de la cognition ou la généralisation hors F0. Les étiquettes des bras n'ont pas fait l'objet d'une randomisation indépendante supplémentaire ; cette limite du contraste reste à examiner.

## Scellés et conservation

Toutes les entrées ci-dessous sont des **artefacts GitHub publiés**, avec le SHA-256 du **ZIP externe** attribué par le service (pas une signature externe des vies). Vérifier les manifestes internes et les données originales séparément.

| Étape | Artefact GitHub | ZIP SHA-256 |
| --- | --- | --- |
| Plan ingénierie 3.12 | `14266058295` | `97c324b2671282f9e274526654edc48978abe2db4afa41b73972a272aa83d2ac` |
| Plan ingénierie 3.11 | `14267251560` | `c7ba6892188782139ac611f06552c6fc82aae83441c62f7f7a23b178d9e43168` |
| Reçu ingénierie 3.12 | `14276341167` | `9656dc5493e238ac8eba04c4aea327cd37466ddde61ed065ca1bb2ce497eec40` |
| Originaux ingénierie 3.12 | `14276591069` | `2bfb7b72c6b33b0253da1d1a69a7e43c6e95379811c978a117ed6ebd2920eaf8` |
| Reçu ingénierie 3.11 | `14278266716` | `24d7060aa6222aeccc2568f6bee0f569bf82f4eee896c2b03e7a12227c05578d` |
| Originaux ingénierie 3.11 | `14278376600` | `3249e1031f95409bba9aced6750487c37f994ae890557ccdb2360175852620e1` |
| Plan scientifique pré-exposition | `14278546177` | `3a3eb789cb3a726e019238c72fa3b7a66ef45781d2fdf7b6be45bbb3a3ed61c2` |
| Résultat scientifique | `14289613177` | `5c5bced3b05c0331230811e79bb6ac6155b2ff3f04fc99ad1bcee8c21d017e90` |
| Originaux scientifiques | `14289668087` | `d4abb68e809940ef1eab82049e0e1b86c2a62e8c10622740eea45678109503ea` |

**Rétention actuelle affichée : expiration le 2027-02-14 20:28:14 UTC.** Ces archives devront être copiées dans une conservation durable avant expiration sans altérer leurs ZIP ou empreintes. Référence : [suivi scientifique #1427](https://github.com/josselin-orta-lab/individual-zero/issues/1427#issuecomment-6941782335).

## Deux niveaux distincts de preuve

**Vérifié en interne dans l'exécution source-exacte :** déroulement complet des 4 jobs, deux reçus techniques source-matched, publication de la nouvelle allocation scientifique avant vie, tests et contrôles natifs des originaux G/S/R, descendants, mutations et calcul préenregistré, puis upload des ZIP.

**Non réalisé par cette synthèse :** extraction et **relecture originale par original indépendante des 23 040 fichiers gzip**, replay de la physique et de la décision, attestation hors GitHub et preuve d'indépendance statistique des 32 populations. L'environnement local disponible au moment de ce rapport n'a pas permis d'extraire les ZIP téléchargés. Ne jamais annoncer une attestation indépendante achevée. L'enquête et la réplication hors F0 sont des tâches séparées, pas un motif pour réexposer cette allocation.

## Décision inchangée pour les autres études et moteur

- Stage6-light `beta_u_eff` : `NO_SIGN_CONCORDANCE`, 9+/7−, fermé sans relance.
- Stage7 persistance héréditaire directionnelle : `PERSISTENCE_G2_NO_REPRODUCIBLE_ADVANTAGE_F0`, 12+/4− vs seuil 13+/16, fermé sans relance.
- **Stage8-A gain moyen : `STAGE8A_MEAN_PERSISTENCE_ADVANTAGE_F0`, `CLOSED_NO_RETRY`** : un estimand différent préenregistré sur de nouvelles populations.
- Stage8-B interaction écologique et Stage8-C concentration parentale/causalité génétique : **non démontrées**, garder les analyses secondaires exploratoires et prospectivement figer toute future validation. Ne pas sélectionner opportunément les seuls 23 groupes favorables.
- I1 reste le runtime actif ; I3 référence de développement non enregistrée ; Stage2.1 global `NOT_ISSUED/HOLD_NO_VERDICT`. Provenance `INTERNAL_PROSPECTIVE_NOT_EXTERNALLY_ATTESTED`, sans promotion scientifique globale.
