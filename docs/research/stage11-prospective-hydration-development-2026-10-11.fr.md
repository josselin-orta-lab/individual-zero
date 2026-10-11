# Stage 11 : prédictions prospectives issues de l'expérience vécue

**Date locale :** 11 octobre 2026. **Statut :** diagnostic logiciel, sur données publiques uniquement. Aucune validation scientifique n'est revendiquée.

## Contexte

Le Stage 11 permet désormais à Exploration d'attribuer une motivation intrinsèque à un test causal. Un test peut être sélectionné puis exécuté par Action Control, mais le modèle causal refuse à juste titre de convertir une simple commande appliquée en intervention scientifiquement établie.

Lorsque l'Equipment figé ne connaît pas l'entrée (`equipment_input_unseen`), le plan n'invente pas de conséquence numérique. Le comparateur P-47 ne dispose alors d'aucune prédiction à vérifier.

## Incrément ajouté

Le nouveau module `src/i0/modules/lived_prediction.py` peut calculer une **prévision descriptive de la valeur de l'eau à l'étape suivante**, uniquement à partir de transitions antérieures physiquement vécues et reliées à des épisodes Memory fermés.

Il exige notamment un pas antérieur, des références distinctes de commande et de transition, un épisode Memory fermé, une observation corporelle accessible et le même site. Les doublons de sources physiques et les observations futures sont rejetés.

Si les preuves sont insuffisantes ou discordantes, la prévision reste **indisponible**, et non égale à zéro. Une prévision éventuellement disponible est gelée avant l'envoi de la commande et confiée à l'AgencyComparator existant. Ni les paramètres Equipment, ni les statuts causaux, ni la politique de sécurité ne sont modifiés.

L'activation est explicite : `Stage11Config.prospective_water` vaut `None` par défaut. Les valeurs configurées dans le banc public sont seulement des paramètres de développement, pas une calibration scientifique.

[Spécification de l'incrément en anglais](stage11-lived-prospective-prediction-dev.en.md).

## Résultat mesuré

Sur le commit de code `996778582b159ab633325ba14626c07567994214`, la [CI #38090942472](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38090942472) a réussi **715 tests** sous Python 3.12, plus le test de démarrage.

Le diagnostic public `stage11-public-hydration-funnel-dev-v3` utilise la graine **41**, le monde `small_water_gain` et **18 pas**, sans monde ni graine held-out.

| Mesure | Sans nouveau prédicteur | Prédicteur activé |
| --- | ---: | ---: |
| Commandes de test causal appliquées | 2 | 2 |
| Visites d'exploration | 2 | 2 |
| Actions avec épisode physique fermé | 2 | 2 |
| Prévisions descriptives prospectives émises | 0 | 0 |
| Rapports comparateur spécifiques à ces tests | 0 | 0 |
| Interventions causalement vérifiées | 0 | 0 |

Le statut causal final reste `hypothese_causale` dans les deux variantes. Les empreintes de journal sont identiques pour les deux variantes sur cette exécution : `a0d096374904efac521657d7a96b11f7be10d74928215efb1d0ef9aaa3bf1274`. Cela est cohérent avec l'absence de toute utilisation effective du prédicteur.

Empreintes des diagnostics :
- prédicteur désactivé : `e498ac28f1b0bbecdd38da993d5035b75088b8456b60fbd520da3196c7384ad4` ;
- prédicteur activé : `44f23d9c809ab947c33508ffc0c70b231d4953bd2e852c7499a3a1a4c14cf28d`.

**Interprétation limitée :** le contrat de prévision prospective passe les tests logiciels, mais l'individu n'a pas disposé, dans cette courte trajectoire, d'un épisode antérieur utilisable avant une nouvelle décision correspondante. Aucune amélioration comportementale liée au prédicteur n'est démontrée par ce diagnostic.

## Prochaines vérifications

- Exercer le raccordement avant envoi dans un test de contrat isolé : un échantillon antérieur fermé et valide doit produire une prédiction gelée ; un témoin incomplet ne doit en produire aucune.
- Obtenir davantage d'occasions naturellement acquises dans des mondes publics, sans injection d'hypothèse ni réglage a posteriori des seuils.
- Comparer ensuite les taux de prévisions émises, erreurs, rapports comparateur, provenance Memory et interventions admises. Ces niveaux de preuve restent séparés.
- Préserver le Stage 9 **SCIENTIFIC VALIDATION PENDING / NO-GO** ; aucune campagne held-out ni Golden n'est autorisée par ce diagnostic.

**Conclusion : Stage 11 en cours. Les nouvelles prévisions ne sont pas encore validées par une observation prospective naturelle.**
