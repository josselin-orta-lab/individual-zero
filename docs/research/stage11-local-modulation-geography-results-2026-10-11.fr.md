# Stage 11 : menaces locales, récupération et cartes variées

**Date :** 11 octobre 2026 (Europe/Paris). **Statut :** diagnostic logiciel de développement sur scénarios publics. **Aucun résultat held-out ni validation scientifique.**

## Provenance et conformité

- Code effectivement testé : `904b4ec389998b554429a65f642e81677252d878`.
- [GitHub Actions #38112051388](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38112051388) : **754 tests réussis** en Python 3.12 et bootstrap smoke. La suite complète des Goldens et l'autre version Python ne sont pas vérifiées par cette campagne.
- [Protocole public défini avant les résultats v1](stage11-local-threat-recovery-public-protocol.en.md) ; [première campagne négative, mécanismes d'échec, et corrections v2 déclarées avant relance](stage11-local-modulation-reflex-custody-v2.en.md).
- Modules et diagnostics : `src/lab/stage11_modulation_probe.py`, `src/lab/stage11_geographic_robustness_probe.py`, `src/lab/stage11_geographic_probe.py`.
- Commandes de reproduction : `python -m lab.stage11_modulation_probe`, `python -m lab.stage11_geographic_robustness_probe`, `python -m lab.stage11_geographic_probe`.
- Classification machine : `development_only_not_heldout`; `scientific_verdict = null`, `heldout = false`.
- La spécification EN `docs/architecture/reference/en/mvp-specification-v1.2.1.md` demeure seule normative. Aucun paramètre scientifique, modèle Equipment, seuil de sécurité, κ, ou résultat Stage 9 n'a été réécrit.

## 1. Modulation à partir des observations physiques

| Scénario public | Alerte retenue dans S_t | Transitions constatées | Statut final |
| --- | --- | --- | --- |
| Créature adjacente, fuite bloquée, puis retrait externe au pas 4 | Pas 1, 2, 3 | Pas 1 : `normal → threat` ; pas 5 : `threat → normal` | `normal` |
| Même physique, détecteur local Stage 11 désactivé | Aucune | Aucune | `normal` |
| Énergie 20, puis `set_body(energy=80)` externe au pas 5 | Aucune alerte de menace | Pas 2 : `normal → recovery` ; pas 6 : `recovery → normal` | `normal` |

La menace est une **perception locale de créature adjacente**, non une déduction sur le danger global ou sur une zone cachée. Le test de créature utilise un monde public entièrement bloqué autour de l'individu : aucun réflexe de fuite n'est réalisable, permettant l'exécution des cycles cognitifs ordinaires. L'individu n'a ni fait apparaître ni retiré la créature. Le retrait est un événement externe déclaré, reçu par le monde, et seulement ensuite observé par Perception.

Dans ce scénario, le score κ initial du type de contribution n'était que **0,5** et la réservation de sécurité du Gatekeeper requiert **0,8**. Les alertes ont été **retenues** dans S_t, mais **aucune n'a préempté le slot réservé**. Le profil de menace tient compte de ce type précis d'alerte effectivement retenue et d'origine physique, ce que permet §6.4. Ce n'est pas une réévaluation scientifique de la fiabilité de cette source et aucune alerte synthétique n'a été créditée.

La remontée d'énergie à 80 est **induite par l'extérieur** pour tester la sortie du profil ; ce test ne démontre aucun sommeil, repos choisi, soin ou récupération endogène. Les profils sont gelés par cycle et la sortie demeure conditionnée à plusieurs pas monde.

### Empreintes de modulation

| Scénario | SHA-256 des entrées | SHA-256 du résultat | Tête du journal |
| --- | --- | --- | --- |
| Créature locale | `6b2e7e0c89908f4dd82d053c3df66f46e65c3822e1493a23d8f86cdafec8d0b1` | `c2a46dcb93f7dfcca9dee7e05435b5c7e2921e3ab36171230e676d2fc96a6476` | `695677744f032d94025deea17e6dc67f94108d8d1dc819cde776cb59f31b13e4` |
| Alerte désactivée | `04715598bca8be9f9471a811d940abe392709df70d098aad12a143de970b0d23` | `306ef6239d9924ab92d8558b3f5081efb303d7f949970f91cb7be7c927ee09de` | `ba68469111b8af3b2aa0ff5cda10735ca037e6be53be1d115238bd8984e52fb8` |
| Énergie restaurée | `955a7c831d6af15375f7cce2379c5d95a29dc7fcb122f67e3485b196adcad9d1` | `f1073f204ff051a1777b91bc7fe84200fe0f043b1f490d48391d6f112db6bd89` | `e40c1a6f85e0469c8ba2bec6c1a9a0a4f2eb10d2b48c0d05ea19870554a0f388` |

## 2. Couverture géographique : variantes publiques

La comparaison oppose deux runtimes I0-vNext sur les mêmes paramètres physiques et la même disposition ; un seul active les cibles géographiques. Fenêtre : 6 pas de monde, besoins initialement satisfaits.

| Disposition | Sites perçus, sans géographie | Sites perçus, avec géographie | Actions géographiques appliquées | Rejets de planification |
| --- | ---: | ---: | ---: | ---: |
| Obstacle au nord | 1 | **3** | 2 | 0 |
| Couloir vers l'est | 1 | **6** | 6 | 0 |
| Créature au nord | 2 | **5** | 3 | 0 |
| Zone létale connue au nord | 1 | **3** | 2 | **21** |

Les nouvelles cibles restent locales, perceptibles et bornées. Aucune trajectoire mesurée n'a pénétré une case occupée par la créature ou une zone létale **déclarée connue** au système de sécurité. Cette déclaration initiale de zone létale est une connaissance explicitement fournie à Action Control, **pas** l'accès de l'agent au plan caché du monde.

**Résultat négatif conservé :** face à la zone létale connue, une même cible peut être proposée puis refusée au fil des cycles, générant **21 rejets de planification** sur cette courte fenêtre. La barrière de sécurité fonctionne, mais le filtrage des cibles impossibles et la consommation de calcul sont à améliorer ; il ne faut pas présenter cette répétition comme un gain informationnel.

**Correction de provenance physique :** le premier essai avait révélé que les pas de réflexe n'atteignaient jamais Phase-1 Exploration. Un hook neutre pour les runtimes historiques permet maintenant au seul Stage 11 géographique de consigner la localisation réellement capturée avant l'envoi d'un réflexe. Le compteur ne crédite jamais la destination d'un dernier mouvement avant une nouvelle Perception.

### Empreintes des quatre diagnostics

| Disposition | SHA-256 des entrées | SHA-256 du résultat |
| --- | --- | --- |
| Obstacle au nord | `08418cfbdd50d4194815064c01e30999653d5a86e81b0839bbcbde7980aac3d4` | `593863c50a0cac3fd74aed4d551a493b6926254d98643bf9bc0e4697406a110a` |
| Couloir est | `3e42ce607c5404c2d0d127a6f94d0c1e809038726aa4f5364aa850dcf0d9889a` | `b623cc89cdd3d1ca35770ed4ec086e60338049664b5efffdf036c3c976238f90` |
| Créature nord | `9a52696ccc0674597ebae2b0065737764bdc5a43f5547a4edac8646c0defc1b3` | `e6eb4458ec3cf8333c5714c78b23f3bac40bce7be2bfc301b3f0fabeea549ef2` |
| Létal connu nord | `8a6b14f308766300e6cf0543e8b2334f8efabf40627d0f15505351c3abd6891b` | `6112c1977e7aed904acb40ce71e76e0e448162f03396353e0f62becc5fb05026` |

Le scénario de référence libre, version `stage11-public-frontier-coverage-dev-v2`, conserve 8 sites distincts avec la géographie, contre 1 dans chacun des contrôles Stage 9 et même-vNext sans géographie. Empreinte du diagnostic corrigé : `7b12f200006987d244b40b0c10ef08f72b7b2a723e735b9ece5dee29fe969d5c`.

## 3. Limites scientifiques et suites

1. Les cartes sont publiques, de courte durée, et connues du banc de développement. Aucun résultat n'atteste la sécurité contre des zones dangereuses **inconnues** ni une navigation optimale.
2. Les poids d'intérêt et les alertes de risque sont des paramètres logiciels de développement, pas une calibration P-23/P-24/P-48 indépendante.
3. L'entrée en menace requiert une alerte effectivement présente dans S_t ; lorsqu'un réflexe termine le pas avant tout cycle cognitif, il ne faut pas prétendre qu'une transition du profil a eu lieu.
4. La couverture doit être étendue à des cartes et fenêtres préalablement déclarées, avec contrôle du coût UC, habituation face aux impasses et scenarios de menaces non localement observables.
5. Les tests Goldens longs, la matrice Python multi-versions, l'intégration Stage 10 et Stage 12 et l'acceptation scientifique demeurent séparés.

**Stage 11 : EN COURS. Stage 9 : SOFTWARE IMPLEMENTED / SCIENTIFIC VALIDATION PENDING / NO-GO.** Ce rapport ne rend pas la PR fusionnable.
