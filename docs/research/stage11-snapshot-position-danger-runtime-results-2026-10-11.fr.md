# Stage 11 : restauration causale, arrivée physique externe et transitions de dangers

**Date :** 11 octobre 2026  
**Qualification :** contrôles de développement logiciel, exécutés sur des mondes publics ou des données de test expressément synthétiques. **Aucune validation scientifique held-out n'est revendiquée.**

Source normative inchangée : `docs/architecture/reference/en/mvp-specification-v1.2.1.md`.  
Statuts : **Stage 11 EN COURS**, **Stage 9 NO-GO scientifique**. PR [#25](https://github.com/josselin-orta-lab/individual-zero/pull/25) conservée en brouillon et non fusionnée au moment du présent rapport.

## Historique exact des contrôles

| Code testé (SHA Git) | GitHub Actions | Python 3.12 unitaire | Bootstrap | Sens |
| --- | --- | ---: | --- | --- |
| `92886c2a83dd45b8283cbbbabdaa10c532bbf80e` | campagne historique de capacité | 843 réussis | antérieur | **Ne valide pas** les modifications ultérieures de snapshots |
| `8acba9ce2bd12c97031186dba8e268f901f1bfda` | [#38122271021](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38122271021) | **846/846 PASS** | PASS | nouvelle cohérence capture/ledger/last_capture ; ne règle pas encore l'arrivée externe complète |
| `ea108f6188a94d7bf276ed8710fe580999335d04` | [#38122929828](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38122929828) | **849 PASS, 1 FAIL sur 850** | non exécuté | contre-exemple : Memory exporte `recall_above_threshold` mais ne le restaure pas |
| `ad3dbc85d38b6879caf99027b465bf73ca48a962` | [#38123479223](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38123479223) | **854/854 PASS** | PASS | restauration Memory et scénarios de capacité/danger |
| `7ae286a132bbf9a137b663cb16677dcb56316b63` | [#38123635612](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38123635612) | **855/855 PASS** | PASS | refus transactionnel d'un snapshot incompatible entre propriétaires |
| `57ac40f3239bfcfc138e8fa022ba627e348889d5` | [#38123752782](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38123752782) | **856/856 PASS** | PASS | contrôle d'identité du calendrier causal d'un scénario injecté |
| **`2d0dec9395f374f35c5bc0dab8750451dfa83b5a`** | [**#38123902401**](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38123902401) | **857/857 PASS** | **PASS** | coordination inter-runtimes et refus de coordonnées externes avec conversion implicite |

Les résultats sont attachés exclusivement aux commits indiqués. Aucun contrôle Python 3.11 complet ou Golden n'a été lancé durant cette série. Les modifications documentaires postérieures au dernier code testé ne sont pas une nouvelle validation du code.

## Garanties logicielles établies sur le dernier code testé

1. **Capture physique externe au-delà du registre de visites.** Le scénario `set_position` agit uniquement sur WorldBody et est journalisé comme input externe. Il exige des coordonnées entières exactes, intérieures et non obstruées : pas de conversion silencieuse d'un nombre fractionnaire, d'un booléen ou d'une chaîne en coordonnée valide. Lorsque la vraie Perception observe une nouvelle position avec un registre Exploration saturé, Stage 11 journalise `stage11_geographic_physical_capture_unregistered` ; il n'invente ni site enregistré, ni récompense intrinsèque, ni mouvement autonome. Le rejet direct de `GeographicExploration.observe_capture` reste atomique.
2. **État de Memory.** Le champ causal `recall_above_threshold`, déjà exporté, est désormais restauré. Les tests couvrent les deux côtés d'un franchissement de seuil afin de ne ni dupliquer un rappel ni supprimer un rappel légitime lors d'une reprise.
3. **Restauration transactionnelle.** `SnapshotManager.restore` mémorise les états causaux présents avant restauration ; si un propriétaire ultérieur refuse, le gestionnaire tente de restaurer **tous** les propriétaires depuis leur état initial, y compris celui qui a muté avant de lever une exception. Aucun événement `snapshot_restored` n'est inscrit en cas de refus. Si ce rollback compensatoire échoue lui-même, une erreur critique explicite est levée au lieu de prétendre à une restauration sûre.
4. **Scénarios versionnés.** `InjectedScenario.restore_causal_state` refuse un calendrier d'événements différent, même si scénario, version et curseur semblent correspondre. Un curseur booléen est refusé. Un test intégral avec deux runtimes portant des programmes externes différents confirme que le refus ne laisse pas de propriétaires restaurés partiellement.
5. **Dangers connus changeants.** Sur un test expressément **synthétique** DC-05, le modèle canonique passe de `aucun` à `etabli_pour_securite` après deux événements nocifs distincts, puis revient à `aucun` après deux événements non nocifs distincts. Action Control applique immédiatement sa lecture canonique, Planning n'utilise pas de cache privé de dangers, et deux snapshots complets rétablissent exactement les états propriétaires correspondants. Les vrais pas WorldBody exécutés restent distincts des faux événements de test.

## Protocoles déposés avant leurs implémentations respectives

- [Arrivée externe au-delà de la capacité du registre](stage11-external-position-capacity-runtime-contract.en.md)
- [Transitions des dangers connus et deux snapshots](stage11-known-danger-transitions-snapshot-protocol.en.md)
- [Refus transactionnel inter-propriétaires](stage11-snapshot-transactional-rejection-protocol.en.md)
- [Intégrité du calendrier d'événements externes](stage11-scenario-snapshot-schedule-integrity-protocol.en.md)

Tous les témoins synthétiques restent des **unit fixtures**, non des observations physiques, interventions scientifiques ou attestations indépendantes. Les tests n'autorisent aucune requalification rétroactive de Stage 9.

## Limites et prochains verrous

- Les dangers réellement **inconnus** et les changements de gravité en environnements variés ne sont pas scientifiquement généralisés ; une lecture directe de l'état réel de WorldBody par la cognition reste interdite.
- Une arrivée externe arbitraire dans une zone létale, ou un scénario invalide échouant pendant l'ouverture du pas, demande une vérification complète des transitions, du journal, du scheduler et du rollback. Le test actuel de position invalide prouve la non-mutation de WorldBody au niveau du service, **pas** la récupération générale de l'ensemble du runtime après tout input erroné.
- La capacité `max_distinct_sites` est un **plafond d'enregistrement de l'exploration**, pas une limite motrice intrinsèque : accepter un repositionnement physique externe ne démontre pas un déplacement autonome possible.
- Les impasses sur des horizons plus longs, budgets cognitifs fortement dégradés, dangers nouveaux, replay étendu, campagne Golden et environnement de référence Python 3.11 restent à instruire.
- Aucun test fourni ici n'établit une sécurité universelle, une causalité physiquement acquise, une acceptation scientifique, un Stage 11 terminé ou la levée du **Stage 9 NO-GO**.

**Conclusion conservatrice :** la suite unitaire Python 3.12 et le bootstrap ont réussi sur le SHA `2d0dec9395f374f35c5bc0dab8750451dfa83b5a` ; **Stage 11 reste EN COURS**.
