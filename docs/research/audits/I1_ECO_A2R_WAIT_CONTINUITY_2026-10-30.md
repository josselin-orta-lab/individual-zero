# A2-R : continuité froide de l'accumulateur d'attente (30 octobre 2026)

Extension conservatrice des audits #645-#647 : contrôle entre cycles du même pas pour `permanent:attendre`, puis, pour deux pas consécutifs avec décision appliquée, la remise à zéro si attente engagée ou la multiplication par le résiduel source-born sinon. La dernière trace est rapprochée de l'owner Competition scellé dans la génération M11 courante. Les états sans preuve d'une mutation intermédiaire sont explicitement exclus ou rejetés.

Ce n'est **pas** un rejeu complet des candidats de Competition : les autres identités, semantic refresh, changements de buts, invalidations, transitions non publiées et historiques de refus de sécurité ne sont pas reconstitués. Le propriétaire initial et les éventuels anciens engagements ne sont pas attestés par cette unique chaîne. Ne pas transformer l'accord de `accumulator_before` en preuve de bénéfice moteur Q.

Tests négatifs sur image finale falsifiée, exécution native technique M11 et postflight strict. Aucun moteur I1/I0 modifié. Cohorte H192 0/96; A1-C NO_GO; L3 NOT_ESTABLISHED.