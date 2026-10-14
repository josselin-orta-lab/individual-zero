# Stage12 #110 - A2.22 : résultats de garde durable après crash et origine non authentifiée

**14 octobre 2026.** Préenregistrement `5c1e47137cefd227ad717a2c994602c8302a0ee0` antérieur au code expérimental `f08436ce76ebb5980f1fccfd6f31f113c165a6a4`. Exécution vérifiée au SHA `a87e1273304057a0ced8644b5165139b0cdba359`, [GitHub Actions #38643987588](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38643987588) : **SUCCESS Python 3.11 et Python 3.12** sur les mêmes graines 131–134. Le SHA de ce document est postérieur et sa CI finale est une vérification distincte.

## Résultats physiques et transactionnels

Le banc a créé **96 mondes physiques `WorldBody` distincts**, exécuté **192 véritables `WorldBody.apply`** et provoqué **96 morts abruptes de processus** sur six fenêtres `os._exit`. Quatre sorties abruptes supplémentaires concernent uniquement les contrôles d'entrée forgée, sans nouvelles transitions physiques. La garde est un processus indépendant utilisant sa propre base SQLite WAL / synchronous FULL ; la reprise d'audit est toujours réalisée depuis un nouveau processus froid (116 audits au total, comprenant 16 tentatives post-ACK de corruption et 4 contrôles pré-scellement).

| Frontière | Cas | État durable attendu et obtenu | Candidat autorisé |
|---|---:|---|---:|
| Avant intention | 16 | `fresh` | 0 |
| Après intention | 16 | `pending` | 0 |
| Après publication candidate prématurée | 16 | `pending` | 0 (16/16 refus) |
| Après écriture transactionnelle avant COMMIT | 16 | `pending` | 0 |
| Après COMMIT avant ACK | 16 | `sealed` | 0 (candidat absent) |
| Après ACK | 16 | `sealed` | 16/16 |
| **Total** | **96** | **16 fresh, 48 pending, 32 sealed** | **16** |

Après ACK, **16/16 falsifications de candidat** ont été refusées à froid contre la copie scellée. Le banc interdit de continuer depuis une intention pendante ; il ne simule aucune nouvelle action cognitive après le crash et ne prétend pas recréer un état d'I0.

## Résultat négatif déterminant : falsification antérieure au scellement

**4/4 dossiers perceptifs modifiés avant remise à la garde ont été acceptés** et relus comme sources scellées cohérentes. L'auditeur externe, possédant la capture originale, les reconnaît comme faux. Il s'agit du résultat négatif prévu, pas d'un échec masqué : SQLite et les SHA garantissent une conservation contrôlée de ce qui leur est soumis, pas l'origine véridique des données entrantes. **La garde durable seule n'authentifie pas Perception.**

## Limites d'architecture

Le laboratoire reproduit plusieurs fenêtres de crash de processus, non les garanties d'une panne disque, d'un système d'exploitation compromis, de l'usurpation du producteur perceptif, ni d'une partition distribuée. La garde est un second dépôt expérimental, **pas** une nouvelle composante d'I0, **pas** le même COMMIT que le journal causal et le corps M-11, et ne possède aucune autorité pour redémarrer une vie. L'atomicité de la vraie intégration à M-11 n'est pas prouvée ici. Les hachages ne deviennent jamais un signal de causalité pour I0.

**Verdict :** T1–T6 conformes au protocole sur le SHA testé, T7 respecté au niveau des fichiers modifiés. Ce verdict reste borné à l'outil de laboratoire ; **0 vie cognitive autonome, 0 révision intégrée, 0 preuve GA-06 / 2+2/12, pas de coût UC, pas de réception opérateur**. Il faut spécifier le reçu perceptif au propriétaire transactionnel existant **sans double WAL** et démontrer des crashs réels au bon point d'intégration, avant toute modification normative. La séparation agence proximale / responsabilité distale n'est pas arbitrée.

**Stage 12 PARTIAL ; issue #110 OPEN ; spécification MVP v1.3.1 inchangée.**
