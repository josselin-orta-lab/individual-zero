# Stage8-C · registre de garde des originaux et transmission courte

**Établi le 18 novembre 2026, avant publication de tout résultat de la cohorte scientifique.** Ce registre ne préenregistre **aucune nouvelle hypothèse**, ne modifie aucune allocation, ne crée aucun World et n'autorise **aucune relance**. Il complète le [protocole prospectif](STAGE8C_THREE_ARM_PROSPECTIVE_PROTOCOL_2026-11-18.md), son [annexe d'admission scientifique](STAGE8C_SCIENCE_ADMISSION_APPENDIX_2026-11-18.md), le [suivi #1438](https://github.com/josselin-orta-lab/individual-zero/issues/1438) et l'[audit des originaux #1443](https://github.com/josselin-orta-lab/individual-zero/issues/1443).

## Exécution à surveiller

- Campagne **prospective unique** [GitHub Actions #44320492293](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44320492293), `run_attempt=1`, source scientifique Git **`a32b7bf50981e0bbaf688e3caf9973525888c05d`**. Aucune autre source n'est autorisée à produire ou reclasser ces vies.
- Deux répétitions techniques **réussies**, Python 3.11 et 3.12 : **32 256 vies natives d'origine par répétition**, avec **4 608 mutations et 18 phases par répétition** d'après leurs reçus scellés et leur gate. Il s'agit d'évidence de transport, **jamais de données inférentielles S−M**.
- Contrôle conjoint **réussi** ; le plan scientifique indépendant a été publié **avant la première naissance scientifique**. À la vérification du 18 novembre, la cohorte scientifique G0/G1/G2 était **encore en cours**, sans reçu scientifique final ni ZIP de ses originaux.
- Critère unique inchangé : `n=32` populations F0, `D[p]=mean_G2_steps(S,p)-mean_G2_steps(M,p)`, Student unilatéral à `alpha=0,025`, `t(31)=2,0395134463964077`, réussite seulement si `s>0` et `mean(D)-tcrit*s/sqrt(32)>0`. Les contrastes S−U et M−U restent secondaires, et **toutes** les populations défavorables ou nulles doivent être publiées.

## Artefacts réellement présents avant le résultat de science

Tous dans l'exécution **#44320492293**. Les identifiants et tailles ci-dessous ont été lus dans la liste des artefacts GitHub Actions, **pas inventés à partir de noms de fichiers**.

| Nature | ID d'artefact | Taille GitHub déclarée |
| --- | ---: | ---: |
| Plan technique préexposition Python 3.11 | `14435160421` | 169 883 octets |
| Plan technique préexposition Python 3.12 | `14435195718` | 169 803 octets |
| Reçu technique scellé Python 3.11 | `14448166911` | 791 octets |
| Reçu technique scellé Python 3.12 | `14455719351` | 792 octets |
| Originaux gzip techniques Python 3.11 | `14446784305` | 1 275 044 422 octets |
| Originaux gzip techniques Python 3.12 | `14455079672` | 1 268 757 801 octets |
| Reçu de la gate conjointe | `14455244612` | 983 octets |
| Plan scientifique + les deux reçus avant exposition | `14455899574` | 172 512 octets |

**Empreintes figées de contrôle** : allocation scientifique SHA-256 canonique `bee65ba13a75eca1b283f1558aba2fc5418748aa84c35d8525fe6646b8dd22b6` ; plan natif imbriqué `c044a2facf703985f26896817b4c9214e845ee0156ae16dc1141c06594f8070b` ; réservations des 192 World G2 `9927f47772378559d714c8ef66b65b8dcfeb3766e39e1d1db69562245bf5683e` ; protocole `frozen_method` `c63ef4730795f54d6fba282010a70e7fa32760717967af280ac4169d9bced8c4`.

L'audit des **cinq plans Stage8-C** disponibles (deux techniques historiques, deux techniques nouvelle source et un plan scientifique) a relevé **58 560 graines natives** et **320 clés parentales HMAC distinctes**, sans collision entre leurs dix paires. **Ceci ne constitue pas une relecture indépendante des vies gzip.**

## Conservation : frontière de 90 jours

Les workflows fixent `retention-days: 90`. Les artefacts produits le **18 novembre 2026** approcheront donc leur échéance **vers le 16 février 2027** (date effective à vérifier dans GitHub Actions). Les deux ZIP techniques totalisent déjà **environ 2,54 Go**, au-delà de la limite de téléchargement par le connecteur de ce chat (**512 Mio** par artefact).

La priorité de garde est de **préserver sans altération** les huit artefacts ci-dessus, puis, dès leur publication : `SCIENCE_PLAN.json`, `SCIENCE_RECEIPT.json`, `SCIENCE_FINAL.json`, `SCIENCE_CORE.json`, les deux `PHASES.jsonl`, les **32 256 vies scientifiques gzip originales**, et le rapport d'audit indépendant. Pour tout transfert vers un stockage plus durable : conserver les octets/ZIP originaux, l'identifiant de run, le nom d'artefact, la taille, le SHA-256 du fichier reçu, l'horodatage et un manifeste de correspondance. L'archivage externe **n'est pas une condition de validité scientifique de l'étude** sous ADR-0022, mais sa conservation empêche la perte de vérifiabilité après rétention GitHub.

Un reçu attestant que des fichiers ont été rehashés **dans un job GitHub** ne remplace pas la lecture des gzip par un second auditeur. Ne jamais écrire « 32 256 vies scientifiquement auditées indépendamment » sans le rapport original-level complet.

## Reprise sûre après clôture du workflow

1. Vérifier `status=completed`, `run_attempt=1`, `head_sha=a32b7bf5...`, le succès des deux répétitions, du `technical_gate` et du job `science`. Un échec, une annulation ou un artefact scientifique manquant donne **`TECHNICAL_NO_VERDICT_NO_RETRY`**, jamais un résultat biologique négatif.
2. Consulter le reçu, les **32 contrastes S−M** et l'effet moyen uniquement depuis la **cohorte scientifique distincte**, jamais depuis les répétitions techniques. Ne pas retrancher les populations défavorables.
3. Vérifier l'exécution autonome du workflow `i3-stage8c-readonly-original-audit-20261118.yml`, déclenché seulement après le run prospectif exact. Son **code d'audit** est épinglé au commit pré-résultat **`23d0e3eabff0042123c84f4b292a2e4c72cfcc8f`** (la définition du workflow a été figée dans [PR #1446](https://github.com/josselin-orta-lab/individual-zero/pull/1446)). Il doit recomposer la généalogie des 4 608 mutations et les 768 fondateurs G0, recalculer **les 32 contrastes depuis les gzip** et comparer chaque valeur au résultat publié.
4. Si le contrôle indépendant échoue : publier son erreur, conserver tout le corpus et ne pas « corriger » l'observation par un nouveau tirage, une autre racine, une relance de l'étude ou une modification du seuil. Éviter de fermer l'[issue #1443](https://github.com/josselin-orta-lab/individual-zero/issues/1443) prématurément.
5. Conserver l'architecture des verdicts : Stage7 négatif selon sa règle directionnelle, Stage8-A positif en moyenne F0, Stage8-B négatif pour son interaction écologique. I1 demeure le moteur actif et I3 la référence expérimentale sans promotion automatique ; Stage2.1 scientifique reste `NOT_ISSUED/HOLD_NO_VERDICT`.

**Statut documentaire de ce registre : avant verdict**. Sa publication, seule, n'est pas une preuve de survie, d'héritabilité ni de causalité génétique.
