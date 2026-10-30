# A2-R : co-exposition réelle de candidats Q appris en Competition (30/10/2026)

Objectif #438 : mesurer, sans régler le moteur, combien de cycles *réellement payés* de Competition ont au moins deux options évaluées, puis au moins deux options dont le Q appris a été lu depuis TD authentifié. La présence d'une option alternative est **distincte de sa sécurité et de son admissibilité Action Control**.

L'analyseur d'opérateur `i1_a2r_q_coexposure.py` s'exécute **après** le rejeu M11/TD, l'attestation Stage8, l'audit spécifique des affordances locales et la jonction Action Control, puis rejoint les occurrences exactes `(pas, cycle, option)`. Il refuse des traces manquantes/dupliquées, valeurs Q modifiées, désaccord d'evidence, mélange des familles non vérifiées et décisions sans le chemin exact. Il compte notamment :
- Cycles avec Q appris, au moins une alternative évaluée, au moins deux Q appris, au moins deux équations Q appris recomputées.
- Options apprises franchissant le seuil ; admissions Q apprises effectivement liées aux commandes physiques.
- Quatre catégories mutuellement exclusives et exemples bornés par vie, au lieu de journaux agrégés illisibles.

**Limites constitutives :** les compteurs sont descriptifs, une concurrence n'est pas une expérience indépendante, la sécurité des alternatives n'est pas reconstruite et P-40/besoins ne sont pas isolés. Une divergence Q ou une admission Q-apprise **ne suffit pas** à prouver que Q a *causé* le choix moteur, encore moins son bénéfice. Une co-exposition absente établit une limite de l'expérience observée, pas une incapacité structurelle du moteur.

Critère de décision avant cohorte : si aucune co-exposition réelle et comparable n'est documentée, ne pas lancer H192 pour rechercher artificiellement une inversion ; si elle existe, reprendre l'analyse du premier cas authentifié, sans retoucher les seuils, le reward ou la physique. A1-C NO_GO, A2-R 0/96 non exécutée, L3 NOT_ESTABLISHED. Aucun moteur I1/I0 modifié.