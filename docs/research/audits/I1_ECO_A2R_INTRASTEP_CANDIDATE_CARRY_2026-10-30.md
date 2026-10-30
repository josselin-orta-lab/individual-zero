# A2-R : continuité observable des candidats entre cycles payés (30/10/2026)

Prolongement borné de la PR #649, sans modification du moteur I1/I0. L'audit froid impose des cycles Competition strictement chronologiques. Pour une même option non permanente présente dans deux **cycles immédiatement adjacents d'un même pas**, il vérifie la conservation de l'accumulateur seulement lorsqu'aucun enregistrement, changement de but, admission, veto ou continuation mémorielle n'est intercalé. Dans les autres cas, la transition est quarantinée, jamais supposée correcte.

Les reprises de mémoire `i1_place_memory_intention_reconsidered` sont vérifiées pour leur chronologie et leur borne supérieure source-born, sans les qualifier de causalité motrice. L'accord des nombres publiés n'atteste pas leur origine complète : plans, changements sémantiques, invalidations silencieuses et engagement restant non rejoués. Il ne suffit pas de satisfaire une égalité numérique pour prouver que Q appris est utile.

Tests adversariaux purs + quatre vies M11 techniques ; 0/96 vies H192 confirmatoires. Aucun réglage TD/Competition/UC. A1-C NO_GO, A2-R NOT_EXECUTED, L3 NOT_ESTABLISHED.
