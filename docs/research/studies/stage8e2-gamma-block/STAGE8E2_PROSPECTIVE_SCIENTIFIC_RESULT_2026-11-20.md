# Individual Zero i3 · Stage8-E2 · résultat causal prospectif du bloc gamma

**Clôture au 20 novembre 2026 : `STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0 / CLOSED_NO_RETRY`.** Expérience scientifique prospective interne : **résultat négatif selon le critère unique préenregistré**. Les archives originales ont été relues par un auditeur indépendant du générateur et la réduction statistique a été reproduite dans un autre job. Ces preuves sont **internes**, non une attestation de dépôt extérieur. Une absence d'effet causal de toute taille n'est PAS démontrée.

## Question, intervention et critère figé

L'étude teste si la **permutation réciproque du bloc ordonné `gamma1,gamma2,gamma3` entre génomes G2 S et M** change l'avantage de persistance S−M. Les 28 autres gènes et la politique motrice P1.3 funded-v2 sont inchangés. S descend de parents sélectionnés selon leurs six vies corporelles précédentes ; M reproduit exactement les multiplicités parentales avec identités brouillées. Les sham sont des clones génotypiques des S/M avant échange, et les « swap » sont des individus distincts, confrontés aux mêmes WorldSpecs G2 mais à une entropie de vie indépendante.

**Estimand primaire figé avant G0**, par population : `T[p]=(S_sham−M_sham)−(S_swap−M_swap)`, où chaque moyenne est établie sur **144 vies natives originales**. L'unité indépendante est la **population, n=64**, non les individus ni les pas. Test de Student bilatéral, `alpha=0.025`, `df=63`, seuil `|t|>2.2962367715148795`, intervalle bilatéral à 97,5 %. Une variance nulle ou un original absent invaliderait le verdict. La manipulation teste **l'ensemble gamma123**, jamais `gamma3` isolé.

## Trois exécutions prospectives réellement réalisées

| Campagne | HEAD protocole / moteur | G0 | G1 | G2 | Originaux | Porte |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Technique CPython 3.11 | moteur `03faff4b9c194a5288b92e394f6a75cbe62cd095` | 9 216 | 18 432 | 36 864 | **64 512** | PASS + cold audit |
| Technique CPython 3.12 | même moteur exact | 9 216 | 18 432 | 36 864 | **64 512** | PASS + cold audit |
| Science, troisième racine OS | protocole `404bdf6c844c048985659d6c4d03827ffb19d878` ; moteur `03faff4b9c194a5288b92e394f6a75cbe62cd095` | 9 216 | 18 432 | 36 864 | **64 512** | PASS + cold audit + réduction indépendante |

**193 536 vies originales au total** dont 129 024 techniques **non admises dans l'analyse scientifique**, et 64 512 nouvelles vies scientifiques. Les **trois racines et les WorldSpecs G2 sont distincts** ; 384 WorldSpecs G2 par exécution, physiquement appariés entre quatre bras. Chaque génération a attendu l'audit complet des originaux de la précédente, dans neuf phases chaînées, sans remplacement de vie après échec.

- [Exécution technique unique #44536464441](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44536464441) : **six jobs sur six PASS**, deux plans préexposition, six archives originales G0/G1/G2, deux réaudits à froid de **64 512 gzip chacun**, porte finale **PASS sans verdict scientifique**.
- [Exécution scientifique prospective unique #44637950471](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44637950471) : **cinq jobs sur cinq PASS**, préflight, préexposition **avant toute vie G0**, naissance native, réaudit à froid de **64 512 gzip**, puis second calcul statistique indépendant. Aucune relance ni seconde cohorte scientifique.
- Plan préexposition scientifique réellement publié : `SCIENCE_PLAN.json` SHA-256 **`11402a5581cc9cdd32d33ca5314f5727b5fc14cf2d935562a2c23962c84a0c0d`** ; plan natif SHA-256 **`bfc77d52ba4a075e21a8c4289171cefd259f06d270f502d100c24e69d4e3de43`**. Le protocole et la racine scientifique n'ont pas été choisis après lecture du résultat. Moteur inchangé : `source_snapshot.sha256=e816ff5f5ee679253fc57f6e9ee79d21dff73dd72d6adf3c7f55ba7aa0f3e7f6`.

## Résultat primaire effectivement observé

| Grandeur | Valeur |
| --- | ---: |
| Moyenne populationnelle de `T` | **−0,09071180555555447 pas** |
| Écart-type entre les 64 populations | 15,67312585913368 |
| Erreur-type | 1,95914073239171 |
| `t` de Student, `df=63` | **−0,046301832255212165** |
| `p` bilatéral, recalcul secondaire de `t` | environ **0,96321614** |
| Intervalle bilatéral de confiance à 97,5 % | **[−4,589362795845991 ; +4,407939184734882]** |
| `T>0` / `T<0` / `T=0` | **31 / 33 / 0 populations** |
| Critère de succès `|t|>2,29623677` | **NON SATISFAIT** |

**Verdict figé : `STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0`.** La permutation du bloc gamma123 ne démontre pas de modulation du contraste S−M dans cette nouvelle famille F0. Cette conclusion ne prouve pas un effet exactement nul, une équivalence, l'innocuité d'un gène, l'absence d'épistasie ou une généralisation hors F0. L'intervalle autorise des modulations moyennes dans les deux sens. Les **33 populations à contraste négatif sont intégralement conservées**.

**Décomposition descriptive NON PRIMAIRE, calculée après résultat :** écart moyen S−M sham **+7,274522569444446 pas**, S−M après swap **+7,365234375 pas** ; différence S_swap−S_sham **+0,14453125 pas**, M_swap−M_sham **+0,053819444444445 pas**. Les deux avantages S−M ont un signe positif descriptif, mais leur **différence préenregistrée est nulle au sens du test**. Ne pas convertir ces quatre nombres post hoc en nouveaux tests confirmatoires. L'ancien avantage moyen Stage8-C (+8,676 pas) répond à une autre question et reste publié, non révisé.

## Authentification et réaudit hors générateur

- Audits techniques à froid : `ALL_64512_NATIVE_ORIGINAL_GZIP_REAUDITED_NO_SCIENCE` **deux fois**. Empreintes des chaînes de phases : 3.11 `1cd354277fb58f53aac6b3a381cf0a24e98f4f6bc27aedfac0bb8afb094fd67b` et 3.12 `ccccb27fecdccf679b5e792bca08896aaaed33df0fd1524fb0e751ace05b6c92`.
- Audit scientifique à froid : `ALL_64512_NATIVE_ORIGINAL_GZIP_REAUDITED_NO_SCIENCE` (format du **moteur original technique réutilisé par l'enveloppe scientifique**, le résultat scientifique n'est admis que par son job distinct). Empreintes des manifestes G0 : `bc778001bf312e78ca1ff4881e6e77bc6d8dde82e655726495de6c38deb877cf` ; G1 : `bd86fce99c6a41ea2d6ded2373efaf392d0d4a8c799f04f318eeae4493c615b6` ; G2 : `61eb74a1f429c2f9189ee13da5c52593776d2b6f9d2b2d8ac41bfdea31a6ba00`. Chaîne de neuf phases : `9b79d665c6bd1ea5f26b4e3e1f672c2cf01ace562ef9ccb86d359c0855ef458d` ; **6 144 mutations** reconstruites.
- Vérification complémentaire de lecture des artefacts GitHub : contrôle des octets des plans publiés, manifestes, empreintes SHA-256 comprimé/décodé de **193 536 entrées originales distinctes**, chaînes de phases, allocations disjointes et calcul refait à partir des **64 lignes de moyennes des quatre bras**. Ce dernier contrôle hors CI examine les **manifestes et reçus téléchargés** ; la relecture des **octets gzip complets** a été effectuée par les **trois jobs d'audit à froid**, et non par cette vérification complémentaire locale.
- La réduction externe au générateur `tools/stage8e2_independent_primary_verification.py` a confirmé **`SCIENTIFIC_64_POPULATION_PRIMARY_INDEPENDENTLY_REPRODUCED`** ; résultat scientifique JSON SHA-256 `18ad42a1e68a0a7c1c2390bd397ee90e7872bdf398f0f5bac37d06bbfff8af45`, rapport indépendant SHA-256 `f85be1a8c5a007e0e9ac5f40157e4aa38c40aa16ab013e9c44a34ac1a3fc2b28`.

## Conservation, limites et clôture

Les archives originales **ne sont pas stockées dans Git**. Les artefacts GitHub Actions sont conservés avec **rétention déclarée de 90 jours**, pas indéfiniment. Les **neuf archives G0/G1/G2**, les trois métadonnées, les plans et leurs empreintes doivent être copiés vers un stockage durable, contrôlé par SHA-256, avant leur expiration. Cette opération de conservation à long terme est encore **à réaliser** : le succès du workflow ne constitue pas une réplication permanente. Les résultats nuls, défavorables et les décès n'ont pas été filtrés. Pas de témoin externe indépendant, pas de M11 externe, pas d'affirmation d'intelligence générale.

**Arrêt : `CLOSED_NO_RETRY` pour les trois racines.** Aucune nouvelle naissance Stage8-E2 pour « améliorer » ce résultat. Toute recherche ultérieure de gènes causaux est une **nouvelle question** nécessitant un protocole et des indices indépendants, pas une redéfinition de ce test. I1 reste moteur actif, i3 reste référence de développement non enregistrée ; Stage2 général `NOT_ISSUED/HOLD_NO_VERDICT` demeure inchangé.

Sources : [plan causal daté du 19 novembre](../../../../src/i3/docs/studies/stage8-parent-concentration/STAGE8E2_GAMMA_BLOCK_PROSPECTIVE_CAUSAL_DESIGN_2026-11-19.md) (chemin source depuis la racine du dépôt : `src/i3/docs/studies/stage8-parent-concentration/…`), [issue scientifique #1459](https://github.com/josselin-orta-lab/individual-zero/issues/1459), [deux répétitions #44536464441](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44536464441), [science #44637950471](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44637950471).
