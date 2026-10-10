# Stage 11 : diagnostic de développement sur l'hydratation

**Date :** 10 octobre 2026 (UTC, exécution CI). **Statut :** diagnostic logiciel sur monde public, **pas une évaluation scientifique**, ni une campagne held-out, ni une validation du Stage 9.

[Rapport technique anglais et provenance complète](stage11-public-hydration-development-2026-10-10.en.md).

## Exécution reproductible

- Code testé : `85685f353b30c8e43355c066d98b774e22b92445`, branche `i0/vnext-stages-10-12`.
- [GitHub Actions #38090244262](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38090244262) : **700 tests réussis** en Python 3.12. Aucune campagne scientifique ni validation complète des Goldens n'a été exécutée.
- Reproduction : `python -m lab.stage11_hydration_probe`.
- Graine de développement publique : **41** ; monde : `small_water_gain` ; durée : **18 pas**.
- Empreinte du scénario commun : `42a4a3bb02e61c5d5356b4360f342158c11060be2da224b89e559882e7e5b966`.
- Empreinte du journal Stage 9 : `2028e6ce0afed96189f07e8fca2b169fb7c6966cd80ca307e7fe7cbef0d618e7`.
- Empreinte du journal I0-vNext : `6f37bb562e03a5ad5363b497b85e4f7adb31254b27d550337503719baa1445ab`.
- Empreinte des mesures : `bc66275858c0e143bacb9afd7d35ab59631374d594801166d829632f62f79c68`.

## Observations

| Mesure | Stage 9 | I0-vNext Stage 11 |
| --- | ---: | ---: |
| Propositions de test | 37 | 4 |
| Évaluations sans motivation disponible | 37 | 0 |
| Évaluations intrinsèques exploitables | 0 | 4 |
| **Commandes de test appliquées** | **0** | **3** |
| **Interventions causalement vérifiées** | **0** | **0** |

Sur les **4** propositions I0-vNext, les quatre prédictions Equipment sont indisponibles (`equipment_input_unseen`). Deux actions disposent d'une provenance physique et d'un épisode Memory fermé, mais **aucun rapport AgencyComparator correspondant aux tests** n'a été publié. Le statut causal final reste `hypothese_causale`.

## Interprétation et limite

La motivation intrinsèque P-48 permet ici de choisir et d'exécuter des tests, sans que ces actions constituent automatiquement des preuves d'intervention. Le diagnostic logiciel passe de zéro à trois commandes exécutées **dans ce scénario connu uniquement**.

La chaîne de vérification reste bloquée : le plan conserve des conséquences prédites vides lorsque l'Equipment ne couvre pas l'entrée ; Action Control n'ouvre alors pas la comparaison prédiction/observation correspondante. Les épisodes physiques seuls ne satisfont pas le contrat causal.

Le prochain travail doit chercher une prédiction **prospective, traçable et issue d'expérience réellement vécue** si la spécification l'autorise, ou préserver l'indisponibilité de la comparaison. Il ne faut ni déduire une prédiction des paramètres secrets du monde, ni inventer une valeur, ni assouplir l'exigence de vérification.

Les profils Global Modulation ne changent pas durant cette courte exécution : leur activation et leur sortie restent à tester sur des situations adaptées. L'exploration géographique autonome, la généralisation et les Stages 10/12 ne sont pas achevés.

**Conclusion : Stage 11 EN COURS. Stage 9 VALIDATION SCIENTIFIQUE EN ATTENTE / NO-GO.**
