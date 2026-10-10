# Stage 9 : constat comportemental de développement (10 octobre 2026)

**Statut : OBSERVATION DE DÉVELOPPEMENT / DIAGNOSTIC LOGICIEL REPRODUCTIBLE.** Ceci n'est ni une expérience scientifique EXP préenregistrée, ni une campagne `held-out`, ni une validation indépendante, ni la clôture d'INV-25, ni un GO scientifique, ni un Golden Stage 9. La seule référence normative reste `docs/architecture/reference/en/mvp-specification-v1.2.1.md` (§§8.5, 13.2–13.4, 14, 20.3). Aucun seuil scientifique n'est fixé par ce constat.

[English version](stage9-development-behavior-2026-10-10.en.md).

**Pour reproduire ce test :** [procédure minimale pas à pas pour les observateurs](stage9-behavioral-test-quickstart.fr.md).


## Objet et provenance

**Question :** I0 parvient-il, dans les mondes de développement du Stage 9, à observer l'effet de boire, publier une hypothèse causale, proposer une expérience et réellement exécuter une intervention vérifiée ?

1. **Exécution locale rapportée le 10 octobre 2026 :** sous Arch Linux, `x86_64`, noyau `6.8.12-30-pve` et Proxmox LXC, Python `3.12.15`, environnement virtuel et installation éditable. L'utilisateur a indiqué travailler sur `main` alignée avec `origin/main`. Les [deux extraits de terminal transmis](evidence/stage9-development-behavior-2026-10-10-local-terminal.txt) sont conservés tels que rapportés dans la conversation. Le SHA Git complet du **checkout local**, le fichier `results.txt` original, le journal brut, l'empreinte SHA-256 locale et un horodatage attesté **n'ont pas été communiqués**. Le `main` distant relevé lors de la rédaction était [`85a5280e08dc97ed91334036ebb1d797762214cb`](https://github.com/josselin-orta-lab/individual-zero/commit/85a5280e08dc97ed91334036ebb1d797762214cb), ce qui ne certifie pas le SHA local.
2. **Recoupement indépendant des messages locaux :** [GitHub Actions, exécution #38067542568](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38067542568), [job #114258148176](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38067542568/job/114258148176), sur le commit Stage 9 `96abfa089fd52f12b7e35c334289088583645125` **avant** son intégration squash. Le [rapport JSON extrait de cette CI](evidence/stage9-development-behavior-2026-10-10-ci-report.json) contient huit cellules et leurs métriques complètes. Il provient des journaux CI, **pas** de la machine locale. L'empreinte `evidence_sha256` interne au rapport ne constitue pas une authentification des observations locales.
3. **Concordance :** les huit cas et l'ensemble des champs transmis par l'utilisateur correspondent aux mêmes champs de la CI. Nous disposons ainsi d'un recoupement du diagnostic sur le même banc de développement, pas d'une validation scientifique sur des mondes cachés.

### Reproduire localement

~~~bash
mkdir -p artifacts/stage9-behavior-dev
git rev-parse HEAD
python -m lab.stage9_hydration_contrast_report > artifacts/stage9-behavior-dev/results.txt
sha256sum artifacts/stage9-behavior-dev/results.txt
~~~

Protocole `stage9-hydration-contrast-diagnostic-v1`, graines de développement 41 et 42, 18 pas par cas, quatre mondes par graine. Il n'utilise **aucune** donnée `held-out` indépendante.

## Résultats constatés

| Graine | Monde | Statut causal | Propositions | Enregistrements acceptés | Non évaluées | Contextes accessibles | Tests « boire » exécutés |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 41 | `null_water_reference` | `aucun` | N/C | N/C | N/C | N/C | N/C |
| 41 | `small_water_gain` | `hypothese_causale` | 37 | 37 | 37 | 9 | 0 |
| 41 | `recurrent_water_need` | `hypothese_causale` | 44 | 44 | 44 | 13 | 0 |
| 41 | `model_aligned_water_gain` | `aucun` | 0 | 0 | 0 | 0 | 0 |
| 42 | `null_water_reference` | `aucun` | N/C | N/C | N/C | N/C | N/C |
| 42 | `small_water_gain` | `hypothese_causale` | 39 | 39 | 39 | 9 | 0 |
| 42 | `recurrent_water_need` | `hypothese_causale` | 43 | 43 | 43 | 13 | 0 |
| 42 | `model_aligned_water_gain` | `aucun` | 0 | 0 | 0 | 0 | 0 |

Les quatre cellules `small_water_gain` et `recurrent_water_need` publient `hypothese_causale`. On y compte au total :

- **163 émissions de propositions**, **163 enregistrements acceptés** et **163 évaluations indisponibles** ;
- **44 occasions physiques d'accès à l'eau** pour tester la relation (ce ne sont pas des décisions ni des preuves d'admissibilité finale) ;
- **une seule option distincte par cellule**, réémise de nombreuses fois, et non 163 expériences indépendantes ;
- **zéro test causal « boire » exécuté, zéro intervention physique publiée et zéro « boire » après l'hypothèse**.

La prédiction est marquée `equipment_input_unseen` pour chacune des 163 émissions, tandis que les diagnostics de refus Planning enregistrés sont vides. Le témoin `null_water_reference` conserve le statut `aucun` et aucun effet positif de l'eau ; les champs `null` y signifient **non renseigné/non applicable**, et non zéro. Pour `model_aligned_water_gain`, le diagnostic `insufficient_positive_closed_episodes` indique un manque d'épisodes positifs clos, sans constituer un verdict sur l'incapacité d'apprentissage. Le monde `recurrent_water_need` modifie aussi la décroissance de l'eau : il n'est pas un contraste à variable unique avec le témoin.

Le rapport de CI conserve `acceptance_status: open` et `golden_stage9_frozen: false`.

## Interprétation et limites

La chaîne observation → mémoire → hypothèse → proposition et enregistrement d'un test fonctionne dans ces cas de développement. L'absence de prédiction Equipment exacte (`equipment_input_unseen`) **n'interdit pas à elle seule** la proposition d'un test : [le code de planification causale](../../src/i0/modules/causal_test_planning.py) crée aussi une proposition lorsque cette prédiction manque.

La cause structurelle du blocage suivant apparaît dans `Stage9OptionEvaluator` : les options `test_causal` sont volontairement marquées `not_evaluated` et ne reçoivent pas de motivation intrinsèque inventée. La spécification réserve l'évaluation de cet intérêt au module **Exploration**, paramètre P-48, prévu au **Stage 11** (§§8.5, 13.4 et 14). Compléter uniquement l'Equipment ne permettra donc pas à ces propositions de franchir spontanément Competition.

**Ce que cette observation étaye :** publication d'hypothèses et enregistrement de propositions reproductibles sur des scénarios connus.

**Ce qu'elle ne démontre pas :** intervention autonome effective, causalité établie, généralisation à des mondes inconnus, taux scientifique de fausses règles, conformité indépendante d'INV-25 ou Golden.

Les extraits locaux ne sont pas des journaux bruts certifiés. Pour renforcer ultérieurement la preuve, conserver le SHA exact du commit local, l'original de `results.txt`, son SHA-256, les journaux, les états causaux, la configuration et l'heure effective ; dater tout ajout au lieu de lui attribuer rétroactivement une antériorité. L'analyse ultérieure des évaluations/Competition puis l'implémentation normative d'Exploration devront rester distinctes de la campagne scientifique.

**La décision scientifique reste NO-GO**, conformément au [registre de pré-lancement](stage9-heldout-prelaunch-decision-record.md) et aux manuels d'évaluation [FR](stage9-independent-heldout-evaluation-manual.fr.md) / [EN](stage9-independent-heldout-evaluation-manual.en.md).
