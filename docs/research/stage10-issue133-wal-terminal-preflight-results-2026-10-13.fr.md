# Issue #133 : audit WAL fail-closed et preuve de frontière terminale (13 octobre 2026)

## Périmètre et provenance

**Source de code** : `1a67526acd05d5d1b941c1ecbcefa9f9bdc05112`, PR #139, créée depuis le `main` protégé `040f49832f6861edfbb606203b5446ffa633052d`. La spécification normative `docs/architecture/reference/en/mvp-specification-v1.3.1.md` §2, §4, §5 et M-11 exige qu'un état physiquement et cognitivement cohérent soit le seul point de reprise. Aucune restauration d'ancienne vie n'est admise. La spécification n'est pas modifiée.

L'[action ciblée #38381311631](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38381311631) est **SUCCESS** : tests du vérificateur en lecture seule sous Python 3.11 et 3.12 + trois réels `os._exit(76)` par interpréteur autour de h/index. La CI générale et Stage12 sont des contrôles distincts : ne pas les déclarer réussis sans leur état sur ce SHA.

## Défaut de classification identifié

Le premier vérificateur `scripts/audit_stage10_index_wal.py` exigeait l'intégrité canonique SHA-256, l'unicité des IDs, le couplage paiement → h → retrait et l'absence d'étape ouverte, mais **acceptait un simple préfixe WAL après `step_closed`**, dépourvu du vrai `experiment_stopped` final. Ce résultat (code 0) ne prétendait pas autoriser une reprise, mais qualifiait abusivement une archive comme « complète ».

**Correction commit `34dd997`** : refuser tout WAL sans événement terminal explicite de l'opérateur ou clôture physique de décès, imposer `experiment_stopped` unique et final, et vérifier la chronologie/identité des ouvertures et fermetures de pas. Le propriétaire read-only classe toujours `may_resume_stage12=false` même sur une archive saine. Les versions de h et références publiées ne peuvent être répétées silencieusement ; la facture de maintenance doit correspondre à des références uniques.

**Tests ajoutés commit `7da2b60`** : archive stoppée cohérente, préfixe fermant un pas mais sans arrêt final, arrêt non final ou répété, ouverture imbriquée, fermeture de mauvaise tentative, réutilisation d'une référence consolidée, paiement sans retrait et lot avec référence dupliquée. Workflow isolé renforcé commit `1a67526`, sans relancer l'expérience de débit H600.

## Matrice des résultats

| Cas | SHA-256/format WAL | Résultat attendu de l'auditeur |
| --- | --- | --- |
| Vie H600 avec arrêt opérateur explicitement signé | Intact | Code 0 : archive cohérente, reprise non certifiée |
| Vie à pas fermé sans `experiment_stopped` | Intact | Code 3 : préfixe non terminé |
| `os._exit` avant h | Intact | Code 3 : paiement sans publication, pas ouvert |
| `os._exit` après h avant retrait | Intact | Code 3 : h durable mais retrait absent, pas ouvert |
| `os._exit` après retrait | Intact | Code 3 : travail indexé complet, pas physique ouvert |
| Copie WAL tronquée, altérée ou hash incorrect | Corrompu | Code 2 : échec intégrité |
| Publication dupliquée, lot indexé incohérent | Chaîne potentiellement intacte | Code 3 : défaut de cohérence |

**Conclusion** : les vérifications logicielles du débit, du suivi UC et de la barrière d'audit en lecture seule soutiennent le bon fonctionnement de l'index sur les scénarios étudiés. Elles ne fournissent **pas** une transaction atomique durable entre états propriétaires Stage12, h, index, physique et Scheduler. Une sauvegarde fsyncée du journal ne reconstruit pas automatiquement le même individu vivant.

## Décision de sûreté et travail restant

La PR #139 reste expérimentale. En l'absence d'une génération durable commune contenant physique, Scheduler, WAL et tous les propriétaires cognitifs, un redémarrage après crash doit rester **interdit**. La voie architecturale étudiable sans changer la norme est de réutiliser le coordinateur SQLite M11 pour l'ensemble Stage12, avec candidat privé, commit atomique de l'état courant **et** des occurrences, puis publication du même état ; cela exige de nouveaux tests de crash et ne doit pas être approximé par un « replay » historique.

Préserver `w_C = 0`, le budget de 100 UC/pas et 600 UC/période de sommeil, la mortalité irréversible, et les archives H600 historiques. Maintenir l'issue #133 OPEN et la PR #139 non fusionnée jusqu'à validation opérateur.
