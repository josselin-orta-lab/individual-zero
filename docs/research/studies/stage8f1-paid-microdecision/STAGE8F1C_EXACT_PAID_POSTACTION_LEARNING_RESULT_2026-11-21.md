# Stage8-F1C · apprentissage post-action payé et vérifié dans la physique native

**21 novembre 2026 : `SOFTWARE_ONLY_NATIVE_POSTACTION_PAID_LEARNING_RETENTION_PASS`.**
Ce verdict est **strictement logiciel, sur deux copies d'un état appris SYNTHÉTIQUE**. Ce n'est ni une première vie scientifique, ni une expérience d'héritabilité, ni un résultat sur les souvenirs historiques G2.

## Racines exactes et exécution

- Développement et tests : [PR #1485](https://github.com/josselin-orta-lab/individual-zero/pull/1485), commit source `0f4b77dd9ba309eff0bd6b8f1fea239cfa80af7e`, fusionné dans `main` par `3628f2c36a81c53cb7193c058a04d176c2f4fcb2`.
- Production, répétition et vérification [GitHub Actions #44837981694](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44837981694) : **2/2 jobs PASS**, **10/10 falsificateurs dédiés PASS**. Deux processus Python 3.11 ont produit des preuves identiques **octet pour octet** ; auditeur séparé Python 3.12, bibliothèque standard seule, sans import du moteur, a recalculé les coûts, la physique, les moyennes d'effets et les états mentaux.
- Suite i3 générale [#44837981567](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44837981567) : **Python 3.11 PASS (1812 tests)** et **Python 3.12 PASS**. Contrôle de gouvernance i3 et contraintes I1/I2 préservés.
- Première tentative technique [#44837914024](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44837914024) : échec de **deux assertions des tests de falsification** ; corrigées dans le source `0f4b77d` sans modifier le moteur historique. Échec conservé, jamais requalifié en réussite.

## Transaction vérifiée

Même `WorldSpec` synthétique 3×3, même corps, même perception et **même état privé complet de `Mind` avant décision**, prédiction personnelle initiale injectée via la vraie API `EffectsModel.observe` (mais non vécue par un G2 historique).

- Dans **les deux bras**, la décision F1 volontaire `dormir` a été financée (0,0328 énergie et 0,05 vigilance), puis exécutée par le même **véritable** `World.step`. La physique donne un corps après action de `[3.0192, 74.63, 59.6, 90.2, 98.95]`.
- Dans **les deux bras**, l'allocation `Mind.prepare_learning` a autorisé `CognitiveWork(cycles=2, simulated_steps=32, memory_items=3, replays=1)`. La physique **native** `World.pay_cognition` a réellement débité, avant tout apprentissage, **0,1096 énergie et 0,174 vigilance** ; le corps devient `[2.9096, 74.63, 59.6, 90.2, 98.776]`, sans nouveau tick.
- L'apprentissage exécuté `Mind.learn_from_outcome` a réellement modifié le modèle des effets, les valeurs TD et le buffer de rejeu. L'observation personnelle `("dormir",)` possède initialement une observation synthétique avec moyenne énergétique **+3,0000** ; après prise en compte du débit réel de l'action **et** de l'apprentissage, la moyenne native recalculée passe à **+2,9288** sur deux observations.
- Le témoin **`discard_after_compute` effectue vraiment la même mise à jour sur un Mind détaché, paie les mêmes factures**, puis jette l'état calculé. Sa mémoire persistante conserve l'estimation +3,0. Ce contrôle **n'est pas** le F1-discard de la décision : F1B couvre séparément le coût égal de décision sans action.
- Un troisième `World.step` dans le cas `terminal_food_not_rescued` conserve **`zero_food`** et refuse tout apprentissage et débit de cognition après décès. Un calcul supplémentaire insolvable est également refusé sans mutation du corps.

**Totaux vérifiés à froid : 3/3 pas natifs, 2/2 apprentissages réellement payés, 1 mise à jour retenue, 1 mise à jour calculée-et-écartée, 1 décès irréversible, 0 vie, 0 cohorte scientifique.**

## Preuves originales et chaîne de conservation

- Deux fichiers `F1C_PAID_NATIVE_ORIGINAL.json` et `F1C_PAID_NATIVE_REPRODUCED.json` de **125 436 octets chacun**, SHA256 identique : `e46ad5f54af49796da65f48d603595544116aa6e73632546b0935d2178c5e91d`. Artefact original GitHub Actions #**14679910820**.
- Réduction froide `F1C_INDEPENDENT_COLD_AUDIT.json`, **889 octets**, SHA256 `754a4c06eeae546f1fe8900375323752056c1b660e1af89d6b4688419a8e1588`. Artefact auditeur #**14679421943**.
- Le [manifeste machine-readable](STAGE8F1C_NATIVE_PAID_LEARNING_PROVENANCE_MANIFEST_2026-11-21.json) conserve les identités, empreintes, coûts et frontières. Les ZIP Actions sont soumis à **90 jours de rétention** ; les octets originaux ont aussi été délivrés sous archive portable dans le dossier de conversation. Un manifeste Git ne remplace **pas** la conservation durable de ces octets.

## Critères **non** démontrés et stop scientifique

La mémoire pré-décision a été **synthétisée**, non reconstruite depuis les vies G2, car leurs instantanés privés complets ne sont pas archivés. Les reçus sont des pas `World.step`, **pas** une vie native `run_life` scellée avec `evidence_head`. Il n'y a **aucun test de décision future améliorée**, d'avantage de persistance, de sélection, d'héritabilité ni de causalité gamma123. F1 reste non admis dans le moteur natif de vie ; aucun nouvel original scientifique, aucune cohorte.

Le verdict causal historique **Stage8-E2 reste `STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0 / CLOSED_NO_RETRY`** et i3 n'est pas promu. Une prochaine preuve distincte devra tester l'effet de cette mémoire financée sur une décision **ultérieure**, avec facturation appariée des décisions et contrôle de rétention, toujours avant toute nouvelle cohorte.
