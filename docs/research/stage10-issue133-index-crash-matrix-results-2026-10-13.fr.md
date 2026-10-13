# Issue #133 : matrice de crash réel os._exit autour de l'index et de h

**Date** : 13 octobre 2026. Source du code exécuté : `fd73af1346ceffeebb91c92bd7f42d71f9fa5ab9`.
**Préenregistrement antérieur au code et à la campagne** : `docs/research/stage10-issue133-index-crash-matrix-prereg-2026-10-13.fr.md`, commit `b00bb92cd716df9a20e0df395678e8bd1d62cae8`.
[GitHub Actions #38378406066](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38378406066) : **SUCCESS** dans les deux jobs Python 3.11 et Python 3.12. Artefacts bruts `11801993863` (3.11) et `11802630180` (3.12). Aucun des six fichiers WAL originaux n'a été modifié.

## Résultats indépendants des deux interpréteurs

| Point `os._exit(76)` | Événements WAL | Dernier événement fsyncé | Publication h durable ? | Index retiré ? |
| --- | ---: | --- | --- | --- |
| Après la facture, avant h | 1 048 | `stage10_consolidation_index_maintenance_charged` | Non | Non |
| Immédiatement après h, avant retrait | 1 049 | `stage10_consolidation_version_activated` | **Oui** | **Non** |
| Après retrait journalisé | 1 050 | `stage10_consolidation_index_retired` | **Oui** | **Oui** |

Toutes les sorties enfant sont `76`, au pas de monde 14, en présence d'un paiement `index_maintenance` de **2 UC** pour le premier lot gelé. SHA-256 final des trois journaux dans les deux Python :
- avant h : `5d7791b64c1d3926da9f9e70a11c8338014819158636356066d5691edbb2f7fd`;
- après h / avant retrait : `293e647a2971c03562d6568da6fefbb2dd870a15a634ea336abb9d60d2b057f1`;
- après retrait : `d150845d2c35001ffb61064c8aba4f9a552cc0993e8739266d91da51667c15d2`.

Le parent a relu le WAL et recalculé les octets canoniques, le chaînage de chaque entrée, l'unicité des identifiants, l'ordre attendu des événements, la correspondance du lot et de ses références, les UC facturées sous plafonds et l'absence de `step_closed` pour ce pas **incomplet**. Aucune vie n'est reconstruite, aucun `run_step` n'est appelé après le crash, aucun décès physique n'est simulé.

## Classification technique

- **Conforme / auditabilité** : la modification `e056359` et son instrumentation produisent des frontières de WAL vérifiables et préservent les preuves de h déjà fsyncé. La matrice de crash est reproductible à l'octet.
- **Limitation conceptuelle effective** : la séquence entre `stage10_consolidation_version_activated` et `ChargedPendingEpisodeIndex.acknowledge_published` n'est **pas une transaction durable atomique unique** entre les propriétaires. Le WAL révèle une publication durable de h sans retrait attesté de l'index. Le fait que les audits du WAL passent n'autorise **aucune** reprise cognitive automatique.
- **Sécurité provisoire** : traiter les trois crashs `os._exit` comme un état dont la récupération Stage12 n'est **pas certifiée** ; ne jamais restaurer un export antérieur, effacer le journal, fabriquer une transition ou autoriser une « deuxième vie ».
- **Développement proposé** : une barrière de reprise read-only qui détecte la séquence incomplète sans charger I0 ou Oracle ; ou une transaction propriétaire commune si un mécanisme durable de Stage12 est préalablement spécifié. Toute évolution de la garantie normative nécessite décision opérateur.

## Résultats de débit préservés

Le changement de traçabilité a été validé précédemment avec deux mondes x deux méthodes x deux Python à 600 pas (source `215b71a`) : 295/299 et 296/299 refs consolidées pour l'index contre 242/299 et 238/299 pour le scan complet, avec 6044/6264 contre 10827/9791 UC. Dans les archives corrigées, chaque publication indexée est immédiatement précédée du paiement et suivie du retrait attesté, pour 61 et 58 h et 295/296 UC de maintenance. Cela soutient la stabilité **locale** mais pas la durabilité au-delà de 600 pas ou la qualité cognitive.

**Décision** : validation technique du débit, de la facturation et du WAL sur les scénarios testés ; **reprise crash Stage12 NON VALIDÉE**. `w_C = 0`, budgets 100/600 UC, norme MVP inchangés. Maintenir #133 et PR #139 ouvertes ; validation opérateur séparée.
