# A2-R : preuve des indices Stage8 natifs

Audit du 30 octobre 2026. Les événements natifs Stage8 publient la signature, Q, valeur simulée, état, indice et versions, mais pas les champs internes de risque/intrinsèque que le comparateur antérieur utilisait comme si leur absence prouvait une parité. Le nouvel outil recalcule exactement le mélange défini dans src/i1/modules/stage8_evaluator.py avec le compteur réel des mises à jour TD, puis contrôle toute la suite des événements et le rejeu Q froid. Les paramètres de fusion doivent provenir de la naissance source reconstruite, jamais de l'archive auto-déclarée.

Cela constitue une preuve numérique du chemin Q/simulation vers indice Stage8, non une preuve que seule la modification de Q explique le changement de commande. Le comparateur apparié #630 et le postflight #635 restent diagnostics descriptifs; ne pas convertir leurs booléens en exposition confirmatoire sans audit indépendant plus strict. La CI est pure et ciblée ; aucune naissance. A1-C NO_GO, A2-R NOT_EXECUTED, L3 NOT_ESTABLISHED.


## Intégration ultérieure au témoin natif et au postflight

L'audit utilise désormais les paramètres Stage8 extraits d'une naissance vierge reconstruite depuis le code source épinglé, vérifie le mélange à partir des événements M11 d'origine et rapproche ses compteurs du rejeu Q/TD. Les quatre vies techniques courtes et l'audit postflight réutilisent cette même vérification. L'égalité des paramètres Stage8 est requise au sein de chaque paire de naissances. Ce contrôle ne constitue ni l'attestation externe du run, ni une preuve que Q, seul, a causé la différence motrice.