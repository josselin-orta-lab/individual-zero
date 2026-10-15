# A2.30-K : préenregistrement de l'audit indépendant d'impact des cohortes J

**15 octobre 2026, avant code K.** Réutiliser exclusivement les archives GitHub Actions immuables [A2.30-J #38720764403](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38720764403), artefact `a230j-py3.11`, source `73d04843735bdfd60ddbf40ae064057847b614fb`. Les résultats connus **avant l'audit K** sont 16 nouvelles vies J, 512 pas physiques, 185 recherches par bras, 165/162 racines bloquées et 4/4 repas. Ces faits ne seront pas recomptés comme de nouvelles vies ou de nouveaux pas en K.

## Questions

1. La diminution de 3 racines bloquées dans `restored/A2` coïncide-t-elle avec des différences de **commandes effectivement exécutées**, de collecte, de positions et de valeurs corporelles, ou se limite-t-elle aux prédictions sans effet moteur ?
2. Les huit paires OFF/ON diffèrent-elles en exploration (`physically_distinct_sites`), risques/décès, motifs d'actions, coûts UC refusés, séquences de préengagement et jugements proximaux/distaux ? Une absence de différence est un constat borné, pas une preuve d'invariance universelle.
3. Le corpus ON comporte-t-il effectivement les 4 transitions historiques et 46 exemples prénataux supplémentaires, avec SHA distinct, et **au moins une clé unique nouvelle** par profil ? Aucun corpus ne doit inclure de vérité produite par les vies cibles. Le contrôle `berry_b` et l'abstention sur les états inconnus sont repris des tests de la CI J.

## Méthode et contrôles négatifs

Télécharger en lecture seule `a230j-py3.11` depuis le run ci-dessus (`permissions: actions: read, contents: read`). Refuser tout identifiant scientifique inattendu, SHA différent, cohorte incomplète, archive mal formée, journal canonique non conforme ou divergence de WAL. Utiliser `HashChainedJournal.audit_durable_wal`, `audit_export_bytes` et, pour les conséquences physiques, l'auditeur P-48 déjà indépendant. Réconcilier **chaque** compteur du rapport de vie avec les événements canoniques et les ancrages du journal.

Comparer les huit paires sur des pas physiques réellement engagés : séquence de commandes primitives et paramètres observables, suite de positions et de sensations alimentaires, reçus Stage6 par pas (`status`, compte de racine, option retenue), nombre de buts activés, de décisions réellement motivées par objectif, refus UC, et jugements Stage12. Rapporter le **premier pas de divergence**, s'il en existe, sans normaliser ni supprimer une différence gênante.

Ne jamais assimiler parité de commandes à une vérité physique omnisciente : seule la physique vérifiée indépendamment atteste le repas et ses effets. Les identifiants de vie distincts peuvent modifier des aspects déterministes liés à l'identité ; donc une divergence ne démontre pas à elle seule la causalité exclusive du modèle. Un bénéfice prédictif isolé ne démontre pas un gain subjectif d'agence. Aucune correction du runtime, aucune commande imposée, aucun Oracle injecté, aucun changement normatif.

## Seuils et issues

L'audit technique doit être FAIL si l'un des 16 journaux ou WAL ne vérifie pas, si la somme des commandes diffère des 512 pas vécus, si le contraste de modèle est fictif, ou si un compteur se contredit. Tout autre résultat, positif, négatif ou indéterminé, sera publié. **Stage12 PARTIAL et issue #110 OPEN** tant que l'opérateur n'a pas validé la suite.
