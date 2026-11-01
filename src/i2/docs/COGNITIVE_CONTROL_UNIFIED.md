# I2 : contrat actuel du cycle cognitif synthétique v5

**G2 `TESTED_SYNTHETIC`, proposition inerte.** I1 demeure seul actif. I2 n'a ni point d'entrée, ni naissance, ni autorité motrice.

Source unique : `src/i2/modules/cognitive_cycle_fixture.py`. Tests de cycle, contrôle, terminal et reprise froide : `tests/i2/test_unified_control_cycle.py`, `test_synthetic_lifecycle.py`, `test_cognitive_cycle_fixture.py` et `test_single_transaction_owner.py`.

## Propriété et interface

Le schéma **unique** `i2-unified-cognitive-lifecycle-feedback-fixture-v5` possède un fichier SQLite de test, un compte UC synthétique, un état d'intention, un journal d'événements chaînés et un marqueur terminal synthétique. Les ports `observation_source`, `valuation_source`, `current_source`, `safety_source`, `genesis_ref` et `terminal_source` sont obligatoires. Aucun deuxième banc SQLite autonome d'intention, Competition ou Action Control n'est autorisé.

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
| Études H2 séparées pouvant influencer les valeurs de test | La mémoire H2 est publiée dans le même COMMIT **synthétique v5**, sans M11 ni preuve physique |

Les sources de preuve sont des doubles injectés. Un SHA-256 local n'est pas une signature M11. Une copie intégralement réécrite peut rester cohérente en interne. Rejouer le fichier à chaque transaction coûte O(N), acceptable seulement pour ce banc. Le résultat conserve toujours `motor_authority=NONE`.

Vérification ciblée : `python -m unittest discover -s tests/i2 -p 'test_*.py' -v`. Les tests synthétiques ne représentent ni une vie I2, ni un GO G3, ni une preuve de gain adaptatif. Pour les études de crédit et d'apprentissage, voir [DELAYED_CREDIT_STUDY.md](DELAYED_CREDIT_STUDY.md). Pour les états d'avancement, voir [STATUS.md](STATUS.md).

## Mémoire H2 dans le COMMIT local

Le schéma v5 ajoute une seule table d'état H2 au même fichier SQLite, sans second propriétaire ni migration automatique. Le premier retour inclut sa mémoire initiale vide. Toute transition suivante est validée par digest de prédécesseur et score H2, puis inscrite avec l'événement et le débit UC synthétique avant le même COMMIT. L'audit à froid rejoue les transitions, empêche les références de résultats rejouées à travers tout le journal (même après éviction de la fenêtre de 16), et rapproche le snapshot final. Faute avant COMMIT : rollback intégral. Accusé perdu après COMMIT : inspection seulement, aucun nouvel acte. Ces ports H2 restent synthétiques : aucune source M11 ni effet physique attesté. Les anciennes bases v4 et antérieures sont refusées sans compatibilité.

## Inspection froide des COMMIT incertains (G2)

`inspect_uncertain_cognition` et `inspect_uncertain_terminal` interrogent en **lecture seule** le seul journal v5. L'appelant doit fournir le nombre et la tête exacte du prédécesseur ainsi que la projection de l'événement attendu. Le contrôle rejoue toute la chaîne dans une transaction de lecture SQLite, puis qualifie l'événement situé immédiatement après ce prédécesseur : `RECORDED_LOCAL_ONLY`, `ABSENT_LOCAL_ONLY` ou `CONFLICT_LOCAL`. Le test impose aussi la requête intentionnelle exacte (`open` ou `observe`, identifiant sémantique, preuve et TTL) et la confronte à la requête inscrite dans l'événement. Deux opérations distinctes sur la même capture sont désormais `CONFLICT_LOCAL`, même si le digest de capture concorde. Pour un COMMIT contenant un apprentissage H2, l'inspection exige aussi la mémoire antérieure et la mise à jour exactes ; elle compare leur projection canonique au champ `feedback_transition`. Une opération de même capture et requête mais sans H2, ou avec une autre conséquence déclarée, devient `CONFLICT_LOCAL`. La paire H2 doit être complète, les mises à jour malformées sont refusées avant lecture. Aucune conséquence physique ou source indépendante n'est authentifiée. Il ne sollicite pas les ports d'observation, de sécurité ou de contrôle moteur. Le rapprochement porte sur la requête déclarée, pas sur l'authenticité de l'intention ni sur les valeurs et conséquences.

Ces diagnostics ne vérifient **pas** la source indépendante de la prévision, la réponse exacte de la politique d'intention ni un effet physique. Une capture et son digest cohérents ne suffisent pas à identifier une opération : c'est pourquoi l'inspecteur demande la requête exacte. Même avec une requête identique, le diagnostic ne prouve ni l'authenticité de la provenance, ni la conséquence physique, ni l'autorité des ports injectés. Même `ABSENT_LOCAL_ONLY` ne permet **jamais** de rejouer : un ancien fichier cohérent, un rollback externe ou un effet physique non enregistré échappent au journal local. Tous les résultats portent `retry_authorized=False`, `resumption_authorized=False`, `motor_authority=NONE` et `m11_authenticated=False`. Aucun propriétaire, schema SQLite, commande, M11 ou chemin de récupération vivant n'est ajouté.
