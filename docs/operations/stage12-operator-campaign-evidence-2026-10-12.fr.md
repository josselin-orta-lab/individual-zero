# Stage 12 v1.3.1 : campagne technique conservee et bilan de couverture (12 octobre 2026)

**Statut de la campagne : PASS logiciel cible. Statut du Stage 12 : EN COURS, non valide par l'operateur. Statut scientifique : non evalue.**

Ce rapport concerne les preuves de developpement sur une vie mortelle neuve, et non une attestation de causalite physique independante. Source normative : `docs/architecture/reference/en/mvp-specification-v1.3.1.md`, notamment paragraphes 2-7 et 9, ainsi que les exigences Stage 12 conservees de la v1.2.1. Les resultats historiques Stage 9 (NO-GO) sont inchanges.

## Provenance

- Reference `main` au lancement : `94a52f546078bb9315ad96b6243eb6ed5055b0ef`.
- PR technique : [#126](https://github.com/josselin-orta-lab/individual-zero/pull/126).
- **Revision du code reellement execute** : `92dcfe96dd566f3e7e1a6931e3978f25f36e5e5a`.
- [Campagne ciblee Python 3.11/3.12 et essais physiques conserves](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38286130847) : SUCCESS pour ses quatre jobs.
- [CI generale rapide](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38286130846) : a verifier independamment sur son commit exact avant la fusion.
- [Archive Python 3.11](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38286130847/artifacts/11762784092) et [archive Python 3.12](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38286130847/artifacts/11763352177), chacune contenant le WAL, l'export causal complet, le manifeste et le controle operateur externe.
- Python exact : 3.11.17 et 3.12.15, respectivement.
- Le code de l'essai verifie l'identite du checkout suivi, les blobs Git, les fichiers normatifs et les modules effectivement importes avant naissance et apres l'execution; la provenance inclut explicitement l'absence de lock complet des dependances.

## Resultats logiciels reellement observes

| Critere | Python 3.11 | Python 3.12 |
| --- | ---: | ---: |
| Suite ciblee `test_stage12_*.py` | 89 PASS | 89 PASS |
| Scenarios complements (goal progress, paquet externe, mortal Observer, alertes, sommeil six passes) | PASS | PASS |
| Transitions physiques appliquees | 600 | 600 |
| Commandes admises et executees | 600 | 600 |
| Evenements `step_opened` / `step_closed` | 600 / 600 | 600 / 600 |
| Diagnostics metacognitifs publies (UC charges) | 600 | 600 |
| Mesures de l'occupation S_t publiees | 601 | 601 |
| Occurrences causales de la vie | 48 650 | 48 650 |
| Arret final `experiment_stopped` | 1, non letal | 1, non letal |
| Vie interrompue par la mort | 0 | 0 |
| Verification independante a partir de l'export et des ancres du manifeste | PASS | PASS |

Les deux exports canoniques sont **strictement identiques octet pour octet**, SHA-256 :
`00fe0c163a391453ec080674f6f5c9eb97cec289824f9f7d77453f4c4388005f`.
Meme tete de chaine :
`26bb2b9ea73b8772f637c7aac2372beec57ede90655001848008f5d828fb8b1a`.

La lecture independante des deux fichiers ZIP a confirme pour chaque version : compte de lignes exactement egal au manifeste, WAL = export canonique suivi d'un saut final, 600 pas distincts avec ouverture, commande, effet physique et fermeture, absence de troncature et stop operateur. Ces ancrages sont issus de la meme garde de preuves et deviennent fixes dans le present rapport ; ils ne prouvent ni l'observation d'une verite physique externe ni une approbation humaine cryptographique.

## Couverture reelle, limites et verdict des modules

- **Variabilite des commandes : insuffisante.** Les 600 commandes physiques sont `se_deplacer`. La campagne ne couvre pas spontanement d'autres actions ni d'autres mondes/graines.
- **Stagnation** : 595 alertes positives, 0 negatives, 5 indisponibles. L'autre classe n'est pas demontrée dans cette vie.
- **Boucle de raisonnement** : 0 positive, 593 negatives, 7 indisponibles. Pas de boucle observee dans cette vie.
- **Faible entropie contextuelle** : 0 positive, 597 negatives, 3 indisponibles. Pas de classe positive observee.
- **Biais d'attribution** : 600 diagnostics sans paire vecue resultat / attribution independamment admise ; 0 succes, 0 echec verifies et **aucune calibration**. L'[issue #110](https://github.com/josselin-orta-lab/individual-zero/issues/110) reste ouverte.
- **Progression d'objectif** : 0 critere un-pas preregistre, 0 progres et 0 non-progres verifies. Les scenarios unitaires et adversariaux ciblent le contrat, pas cette trajectoire de 600 pas.
- **Alignement buts/actions** : 600 actions `without_traceable_justification` et 0 justifications traceables (but ou motivation intrinseque) dans cette vie. Cette etiquette signifie *absence de trace*, ni jugement d'irrationalite ni anomalie de securite prouvee.
- **Sommeil/consolidation** : le scenario de 600 pas desactive volontairement la contribution du sommeil par configuration ; les tests de six passes et d'interruption sont distincts. Aucune calibration de sommeil n'est etablie ici.
- **M-11** : Stage 12 garde un WAL fsync independant du coordinateur SQLite Stage 10/11 ; aucun redemarrage atomique Stage 12 n'est certifie. Rattrapage d'une generation ancienne interdit.
- **Mortalite** : la vie longue finit par un arret operateur non letal et non par un deces. La mortalite irreversible est couverte par des tests cibles mais pas par une mort reelle dans cet essai.
- **Statut d'acceptation** : `operator_accepted=false`, `scientific_validated=false` et `m11_atomic_recovery_certified=false` dans les manifestes.

## Decision de la campagne et suite

**PASS cible** : execution deterministe de 600 vrais pas, invariants de commandes et de fermetures, audit offline du journal, metriques diagnostiques effectuees aux bons pas, arret operateur, preuves conservees, reproductibilite identique sur deux versions de Python.

**Pas de PASS Stage 12 global** : la couverture positive/negative des trois detecteurs, les paires vecues pour l'attribution, la progression d'objectif et les motifs traceables ne sont pas etablis sur cette campagne. Une campagne complementaire fondee sur des observations physiques authentiques devra couvrir ces cas sans inventer de mesures, et le decideur operateur devra examiner ses preuves.

Ce rapport ne change aucun resultat scientifique anterieur, la specification normative, le code cognitif, les effets de `WorldBody`, ni la decision humaine. La fermeture de la PR #126 peut etre prononcee apres CI et revue de l'evidence, **sans valider le Stage 12 lui-meme**.
