# Stage 11 : arrêt sûr d'un input externe invalide et propriété des scénarios

**Date :** 11 octobre 2026  
**Portée :** logiciel de développement seulement. Aucune preuve de sécurité générale, observation scientifique held-out, ni conclusion causale nouvelle.

La référence normative demeure `docs/architecture/reference/en/mvp-specification-v1.2.1.md` (notamment §§4.6, 17.1, 17.4, 17.6, INV-33). Elle n'a pas été modifiée. **Stage 11 : EN COURS. Stage 9 : NO-GO scientifique. PR #25 : Draft, non fusionnée.**

## Résultats rattachés au SHA exact

| Commit testé | Exécution CI | Résultat prouvé |
| --- | --- | --- |
| **`2680283940c10c555238d55814146cb7a3c6129e`** | [#38124468816](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38124468816) | **861/861 tests Python 3.12 réussis** et bootstrap smoke PASS |
| **`821ebff64a4bbc0ffeb0ca47b08648616fc0389c`** | [#38124663847](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38124663847) | **NON VALIDÉ :** workflow marqué failure, job quick-unit-tests conclu failure sans aucune étape (`steps=null`), aucun log accessible (`BlobNotFound`). Aucun test unitaire ni bootstrap ne peut être attesté. Cause infra/quota/politique non déterminée ; ne pas conclure à une régression logicielle ou à une réussite. |

Le dernier SHA déclaré PASS ne valide pas le second. La branche actuelle contient des modifications supplémentaires non couvertes par une CI réussie. Des commits de documentation postérieurs à `821ebff6` ne constituent pas non plus de validation.

## Implémenté et testé avec succès sur `2680283`

- `InjectedScenario.apply_for_step` traite les inputs programmés au même `t_monde` comme un lot dont l'état WorldBody et le curseur sont sauvegardés au préalable. Sur erreur : compensation complète de WorldBody, retour du curseur, journalisation de `external_input_rejected` puis, si nécessaire, `external_input_batch_rolled_back`. La trace append-only préserve aussi la réception et l'application antérieure des événements compensés.
- `ScriptedStage2Runtime.open_step` ferme un pas rejeté en `external_stop` avec **0 commandes et 0 transitions**. Aucune nouvelle capture Perception ni action n'est créée. Le programme de scénario est arrêté (marker `rejected_event` dans son état causal uniquement en cas d'échec). La reprise automatique à `t+1` est interdite.
- Quatre tests d'intégration publics `tests/test_stage11_external_input_atomicity.py` ont été exécutés dans cette CI : rejet d'un lot après une modification de danger, rejet d'une position invalide isolée, continuation normale avec deux inputs valides et rejeu indépendant exact.
- `docs/research/stage11-external-input-atomic-step-open-protocol.en.md` décrit le contrat enregistré avant code.

## Code ajouté après `2680283`, validation EN ATTENTE

- `ScenarioEvent.as_dict` et `InjectedScenario.__init__` prennent des copies profondes des payloads imbriqués, au lieu de conserver des références modifiables par l'appelant.
- `external_input_received` journalise une copie profonde du payload. `apply_for_step` ne retourne plus les instances d'événements internes de l'owner, mais des copies détachées.
- Trois tests unitaires additionnels `tests/test_stage11_scenario_payload_custody.py` couvrent la modification du dictionnaire source, d'un snapshot exporté et d'un événement retourné ; ils exigent que le programme, la physique et le journal restent inchangés.
- Deux tests additionnels dans `tests/test_stage11_external_input_atomicity.py` couvrent un échec volontaire après mutation partielle de WorldBody et un échec de la compensation elle-même, pour lequel une erreur critique et un `world_recovered=false` explicites sont exigés.
- `docs/research/stage11-external-scenario-payload-custody-protocol.en.md` enregistre le contrat avant ces modifications.

**Ne pas supprimer ou relâcher ces tests pour obtenir artificiellement un PASS.** La CI n'a pas démarré ses étapes, donc il reste nécessaire de les exécuter effectivement.

## Procédure minimale de reprise (sans consommation CI par défaut)

1. Vérifier l'état réel de PR #25, son HEAD, les runs #38124468816 et #38124663847 et la disponibilité de minutes / runners GitHub Actions. L'échec #38124663847 n'a pas de traces de tests exploitables : ne pas le classer comme test rouge ni comme succès.
2. Avec Python 3.12 dans un clone local du HEAD exact `821ebff64a4bbc0ffeb0ca47b08648616fc0389c`, lancer d'abord :
   - `python -m unittest discover -s tests -p 'test_stage11_scenario_payload_custody.py' -v`
   - `python -m unittest discover -s tests -p 'test_stage11_external_input_atomicity.py' -v`
   - `python -m unittest discover -s tests -p 'test_stage11_scenario_snapshot_schedule.py' -v`
   - `python -m unittest discover -s tests -p 'test_stage2_runtime.py' -v`
3. Si les vérifications ciblées passent, et **seulement si le quota/runner le permet**, contrôler la suite unitaire pertinente sur le SHA actuel ; le programme de référence Python 3.11 et les Goldens restent des campagnes séparées, justifiées par leur coût.
4. Poursuivre le Stage 11 sur la base des garanties réellement prouvées : gestion de dangers inconnus sous budget contraint, séquences multi-pas, et retour sur snapshot après de nouveaux changements de risque. Ne faire aucune fusion et ne pas déclarer le Stage 11 terminé.

## Limites scientifiques

Les `ScenarioEvent` sont des interventions externes techniques, pas des actions autonomes de l'individu. Un risque caché dans le monde n'est pas une connaissance de l'individu. Les gardes de rejeu et les tests synthétiques ne constituent ni une démonstration d'inférence causale acquise, ni un verdict de sécurité globale. Le **NO-GO scientifique du Stage 9 reste inchangé**.
