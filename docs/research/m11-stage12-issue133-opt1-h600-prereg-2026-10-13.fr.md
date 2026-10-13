# Issue #133 : audit de vie longue M11/Stage12 OPT1, horizon 600 (préenregistré)

**13 octobre 2026.** Ce protocole est enregistré avant le lancement de la campagne H600. Branche `exp/m11-stage12-atomic-paid-index-20261013`, PR brouillon #140 empilée sur PR #139 ; `main` et la spécification normative `docs/architecture/reference/en/mvp-specification-v1.3.1.md` sont inchangées.

## Pourquoi H600 est maintenant justifié

La référence pré-OPT1 H120 (`48b9d82`) et H120 OPT1 (`082e7008`) ont chacune terminé 120 véritables pas, publié 57 des 59 épisodes, produit exactement 12 activations `h`, 72 checkpoints de six passes, 14 397 événements et le même SHA-256 du journal `8b73d539a39fa6b7bf7583652a5f51e4a0427f9c0d203f015190d4641a648f82`. OPT1 conserve 2 audits exhaustifs M11 par pas et les crashs réels M11/index réussissent. Les deux ZIP H120 OPT1 `11816246706` et `11815976776` ont en outre été relus par un second auditeur **hors I0/Oracle/Bench** : intégrité SQLite, chaîne SHA-256, préfixe SQL après reprise froide, identité des propriétaires, 57 retraits, six passes, 2 épisodes encore en attente, UC aux bornes et reprise génération 121 tous concordants. Le H30 cProfile et le H120 OPT1 suggèrent une meilleure soutenabilité, sans prouver un horizon long.

## Expérience prospective gelée

- Un individu Stage12 mortel réel, monde `stage12_reference_mortal` avec paramètres/état de naissance inchangés de `tests/test_stage12_mortal_runtime.py`, `m11_sqlite_custody=True`, sélection `paid_pending_index=True`, P6-B6.
- **Deux exécutions séparées sur le même commit**, Python 3.11 et 3.12 ; chaque naissance est indépendante. Deux interpréteurs sur le même monde **ne sont pas deux graines scientifiques indépendantes**.
- Au plus **600 vrais pas physiques**, jamais de transitions synthétiques. Stopper sur décès, arrêt technique ou exception ; conserver les preuves et qualifier l'échec/arrêt sans combler les pas manquants. Ne jamais reprendre depuis une ancienne génération.
- Paramètres inviolables : `w_C=0` ; P-42 **100 UC/pas**, **600 UC/période**, `index_maintenance=1`, six passes et six références maximales par lot ; P-43, sommeil, veille, Memory et physique inchangés.
- Un seul propriétaire durable, SQLite M11 `synchronous=FULL`, état WorldBody, Scheduler, SlowHistory `h`, index causal, budget, mémoire, métacognition, registre Stage12 et journal exhaustif dans une seule génération courante. **Pas de WAL JSONL vivant supplémentaire**, pas d'Oracle/Bench.
- Conserver pour chaque Python le SQLite intégral, l'export canonique au checkpoint, la liste des observations de performance **tous les 120 pas**, les paramètres, le SHA de code et la trace exacte de succès/échec. Traces de production et de consolidation à chaque pas disponibles depuis l'archive exhaustive, pas d'export « clean » réécrit.

## Critères mesurés à H120 / H240 / H360 / H480 / H600

1. Episodes `episode_closed` cumulés, références publiées dans `h`, backlog `created-consolidated`, backlog par pas, âge moyen et P90 des épisodes restants. Production d'épisodes **séparée** de l'éligibilité/fermeture, et fenêtre pré-coupure de consolidation vérifiée.
2. Débit et pente `backlog(end600)-backlog(end400)` et `backlog(end600)-backlog(end520)`. Une stabilité locale H600 suppose **les deux pentes non positives**, absence de privation de veille ou de besoins vitaux et conformité UC. Une pente négative ne garantit pas une stabilité illimitée.
3. Pour chaque `h` : six passes ordonnées, lot unique, cut antérieur aux épisodes, facture `index_maintenance` immédiatement avant l'activation et retrait immédiatement après, UC facturées par ref, aucun doublon, aucun retrait de Memory ou du journal.
4. Dépenses et reports P-42, enveloppes 100/600 UC, sommeil et veille (primitives physiques, interruptions, besoins vitaux), intégrité des états propriétaires, exclusivité SQLite, chaînage exhaustif SHA-256, unicité des IDs, absence d'Oracle et d'édition du passé.
5. Génération SQLite = nombre de pas réellement engagés. `pending_intent=false` après checkpoint, `PRAGMA integrity_check=ok`, hachage `state_bytes` et roster identiques. Vérifier indépendamment la coïncidence **octet pour octet** entre export H600 et occurrences SQLite.
6. **Seulement si la vie est encore active et complète** : fermeture propre de l'autorité M11, vérification de la dernière génération, restauration froide unique de cette génération, puis vraie transition 601. L'auditeur hors runtime contrôle que les événements de H600 constituent le préfixe intact du journal de génération 601.
7. Temps par pas et cumulé tous les 120 pas, taille SQLite, croissance du journal et appels éventuels trop coûteux ; ne pas modifier les règles scientifiques pour accélérer la CI.
8. Parité inter-Python sur la version exacte, les journaux SHA-256/bytes, générations et états SQL. Divergence = **NO-GO**.

## Protocole d'audit indépendant et statut

Un second script Python standard en **lecture seule**, sans import I0/Oracle/Bench, relit les ZIP, contrôle les occurrences SQL, la chaîne causale, les états propriétaires, les six passes, la facturation et la file temporelle, puis produit un rapport JSON par interpréteur. Un seul SUCCESS CI **n'est pas un GO scientifique**. Les tests `os._exit` et corruption SQL d'OPT1 déjà réussis ne seront pas relancés si SHA d'implémentation inchangé ; H600 n'est pas un substitut à une nouvelle matrice de crash après tout futur changement de code.

**GO technique local** : les deux vies atteignent 600 pas et satisfont toutes les propriétés ci-dessus ; statistiques de backlog et coût évalués sans sélectionner uniquement les fenêtres favorables. **NO-GO** : toute rupture d'état/journal/UC, une reprise d'une génération historique, un épisode perdu/dupliqué, une altération inter-Python ou une vie tronquée prétendue complète. **Inconclusif** : preuve partielle honnêtement conservée si runner interrompu ou budget hôte non soutenable. H600 est une hypothèse MVP, **pas une validation scientifique définitive**.

L'issue #133 reste ouverte, PR #140 en brouillon, PR #139 ouverte, aucune fusion de `main` ni validation opérateur présumée. Un workflow à déclenchement unique est désactivé immédiatement après mise en file, pour éviter la répétition coûteuse des runs.
