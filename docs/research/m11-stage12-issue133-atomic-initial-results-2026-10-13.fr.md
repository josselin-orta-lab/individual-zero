# M11/Stage12 #133 : première preuve intégrée SQLite, sommeil P6-B6 et reprise courante

Date : 13 octobre 2026. **Document expérimental, pas d'acceptation opérateur.** Préenregistrement antérieur à tous les changements : `docs/research/m11-stage12-issue133-atomic-prereg-2026-10-13.fr.md`, commit `585f1500193e6ff572fa60054ce35073df8a67ca`. Branche dédiée `exp/m11-stage12-atomic-paid-index-20261013`, PR #140 **empilée sur PR #139** ; `main` reste à `040f49832f6861edfbb606203b5446ffa633052d`.

## Contrat logiciel mis en place

Le mode `m11_sqlite_custody=True` de `Stage12Runtime`/Stage11SleepRuntime est explicitement opt-in. Il **exclut** toute activation du WAL JSONL latéral. Le constructeur Stage12 ordinaire conserve au contraire son WAL fsyncé d'origine. L'appel direct à `run_step`, y compris un appel explicite via `Stage10Runtime.run_step`, est interdit à un objet réservé à SQLite ; le forçage du chemin hérité conduit à un `technical_halt` non réutilisable comme naissance M11.

`M11TransactionalMortal` accepte exclusivement un Stage12 exactement typé, né en mode SQLite, avec Oracle, Bench, callbacks et WAL absents. Son candidat privé exécute la vraie commande WorldBody, puis **le même commit SQLite** archive l'état courant physique, Scheduler, propriétaires causaux (dont h/index/Memory/Metacognition/Stage12), les occurrences du journal intégral et le statut vital. Pas de commande rejouée lors du `cold_recover`.

Les états de détecteurs/alertes/critères de progrès ont une installation à froid strictement limitée à un propriétaire fraîchement construit et à la génération SQL authentifiée. `restore_causal_state` public de Stage12 demeure une interdiction de restauration historique d'un état actif. Le contrat M11 inclut désormais les versions et prix Stage12, afin qu'une factory incompatible soit refusée.

`w_C=0`, P-42 100 UC par pas et 600 UC par période, politique P6-B6, tarifs Stage12 P-43, sommeil et physique de référence ne sont pas modifiés. Aucun accès Oracle/Bench ni stockage externe de l'audit.

## Résultats reproductibles

[Exécution ciblée #38387247958](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38387247958) : **SUCCESS** en Python 3.11/3.12, quatre jobs au vert :

| Contrôle | Observation |
| --- | --- |
| Naissance SQLite M11 Stage12, aucune autorité physique parallèle | Refus du second WAL et de `run_step` direct ; une seule vie privée |
| Round-trip froid après génération 1 | Exact current SQLite, pas suivant en génération 2, sans replay |
| Index P6-B6 30 pas réels puis reprise | h publié réellement, reçu `index_maintenance_charged` et `index_retired` pour chaque h ; reprise au pas 31 et génération 31 |
| Parité physique des 3 premiers pas | Même statut physique, temps Scheduler et hash du journal que Stage12 WAL non M11 |
| Mort physique réelle sous M11 Stage12 | SQL statut `dead` durable, génération 1 ; `run_step` et `cold_recover` refusés |
| Crashs réels M11 `os._exit(76)`, 6 frontières × 2 interpréteurs | Intent avant commit : `may_recover=false`, génération 0 ; après commit : génération 1, reprise du courant puis pas 2 |
| Crashs réels sur une vraie activation h indexée, 2 frontières × 2 interpréteurs | Crash après activation h dans candidat privé AVANT commit SQL : intent en attente et reprise refusée, pas de h partiel SQL. Crash APRÈS commit SQL du h/index : h et retrait indexé dans la même génération, reprise de ce courant et pas suivant |

Ces tests prouvent les frontières exécutées, pas une preuve mathématique globale de transactions sous tous systèmes de fichiers/hypothèses de crash. La durée d'une vie SQLite Stage12 n'a pas encore été validée à 600 pas. Reproduction scientifique des comportements mémoire, mondes held-out, ressources et qualité cognitive reste une campagne distincte.

La CI additionnelle [#38387390240](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38387390240) inclut désormais les non-régressions de l'ancien Stage12 WAL et du sélecteur indexé, et doit être vérifiée sur son propre SHA `9af95d94257da63eee3c4941b720b4b5ec9e31fb` avant tout GO.

## Décision et limites

**Intégration M11/Stage12 techniquement démontrée pour les courtes vies, leur reprise froide, les morts terminales et les 16 crashs contrôlés**, mais **NON VALIDÉE à l'échelle totale du MVP**. Les conditions préenregistrées demandent encore une analyse de charge/performance à horizon long sous SQLite, les diagnostics et métacognitions avancées, l'absence de régression de toute la suite, le maintien strict d'une seule autorité et la réception opérateur. PR #140 doit rester en brouillon, #139 inchangée, #133 ouverte. Ne pas fusionner dans `main` sans ces validations.
