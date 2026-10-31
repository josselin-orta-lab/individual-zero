# I2 : contrat actuel du cycle cognitif synthétique v4

**G2 `TESTED_SYNTHETIC`, proposition inerte.** I1 demeure seul actif. I2 n'a ni point d'entrée, ni naissance, ni autorité motrice.

Source unique : `src/i2/modules/cognitive_cycle_fixture.py`. Tests de cycle, contrôle, terminal et reprise froide : `tests/i2/test_unified_control_cycle.py`, `test_synthetic_lifecycle.py`, `test_cognitive_cycle_fixture.py` et `test_single_transaction_owner.py`.

## Propriété et interface

Le schéma **unique** `i2-unified-cognitive-lifecycle-fixture-v4` possède un fichier SQLite de test, un compte UC synthétique, un état d'intention, un journal d'événements chaînés et un marqueur terminal synthétique. Les ports `observation_source`, `valuation_source`, `current_source`, `safety_source`, `genesis_ref` et `terminal_source` sont obligatoires. Aucun deuxième banc SQLite autonome d'intention, Competition ou Action Control n'est autorisé.

L'appel `open` ou `observe` entre dans `BEGIN IMMEDIATE`, rejoue et vérifie le journal, rejette une capture répétée ou périmée et consulte un port d'observation subjective **synthétique**. Le compte débite une UC de test pour la consultation de l'intention si elle est financée. Les candidats proviennent uniquement de la capture courante. Competition facture **tous** les candidats du cadre ou aucun, puis formule un avis non moteur. La revue Action Control requiert un contrôle de fraîcheur avant et après son travail ; la sécurité garde son veto. Un contrôle Action Control financé peut débiter son UC de test ; aucun avis ne devient une commande.

Un même COMMIT publie le nouvel état d'intention, les débits UC synthétiques, les candidats, l'avis, la revue et l'événement cognitif canonique. Une faute avant COMMIT annule tout ce cycle ; si l'accusé de réception du COMMIT est perdu, `lookup` et `audit` permettent une inspection **sans recalcul ni nouvel acte**. Le terminal absorbant est inscrit ultérieurement dans **un autre COMMIT local du même journal** par `seal_terminal`, avec un port de preuve injecté. Aucune cognition n'est acceptée après un terminal inscrit.

## Vérification et frontières

L'audit froid rejoue la chaîne, le compte UC, l'intention, les possibilités reconstruites, les évaluations Competition, les reçus et le contrôle de sécurité, ainsi que le scellage terminal. L'ancien mode cognition seule v1, le contrôle facultatif v2 et l'ancien schéma terminal v3 sont **refusés** ; aucune migration, compatibilité ni reprise d'une vie ancienne n'est fournie. La PR #703 a retiré leurs trois bancs transactionnels séparés. Le test `test_single_transaction_owner.py` interdit leur retour comme propriétaires concurrents.

| Propriété démontrée en G2 | Limite scientifique non franchie |
| --- | --- |
| Transaction et rejeu SQLite locaux, avec coûts UC de test | Pas de Scheduler UC vivant, de transaction physique ou de M11 authentifié |
| Contrôles de cohérence, de fraîcheur déclarée et veto synthétiques | Pas de témoin indépendant garantissant provenance, fraîcheur et absence de rollback global |
| Terminal absorbant local et vérification de copies | Pas de mort physiologique ni d'autorité de naissance |
| Avis Competition lié à une capture, sans autorité motrice | Pas de commande admise ni d'effet WorldBody |
| Études H2 séparées pouvant influencer les valeurs de test | **La mémoire H2 n'est pas encore publiée atomiquement dans ce journal** |

Les sources de preuve sont des doubles injectés. Un SHA-256 local n'est pas une signature M11. Une copie intégralement réécrite peut rester cohérente en interne. Rejouer le fichier à chaque transaction coûte O(N), acceptable seulement pour ce banc. Le résultat conserve toujours `motor_authority=NONE`.

Vérification ciblée : `python -m unittest discover -s tests/i2 -p 'test_*.py' -v`. Les tests synthétiques ne représentent ni une vie I2, ni un GO G3, ni une preuve de gain adaptatif. Pour les études de crédit et d'apprentissage, voir [DELAYED_CREDIT_STUDY.md](DELAYED_CREDIT_STUDY.md). Pour les états d'avancement, voir [STATUS.md](STATUS.md).
