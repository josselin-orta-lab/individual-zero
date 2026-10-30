# A2-R: source exacte vers naissance reconstruite et M11

**30 octobre 2026.** Cette tranche vérifie une **parité technique**, pas une cohorte. Les ancres source (commit, tree et empreinte oasis) doivent être obtenues **hors archive à auditer**.

Le lecteur hors moteur `i1_a2r_source_birth_audit.py` exige un checkout Git propre et épinglé, vérifie les blobs source, le preset oasis et chaque module construit dans le fork isolé. Il reconstruit ensuite une instance **vierge et non exécutée** pour chaque mode à examiner. La configuration et les empreintes M11 sont comparées au contrat constructeur original, au propriétaire Value/Needs, à la version TD et au premier état corporel. Le rejeu froid indépendant Q/TD doit également réussir. Aucun état mémoriel historique n'est importé.

Test technique borné : 2 naissances M11 jetables à un seul pas, CANONICAL_ABS et RESEARCH_DEFICIT. Les identités utilisent la matrice A2-R mais **les vies ne sont pas des observations de l'expérience H192**. Elles sont détruites après le test, ne peuvent pas alimenter un agrégateur, et ne valident pas l'effet adaptatif.

**Limites et portes ouvertes :** le contrôle local Git/constructeur ne prouve pas à lui seul que le service distant a exécuté ce code au SHA du run réellement déclenché, ni que les 96 archives seront préservées par deux ancres extérieures. Les champs `external_run_event_sha_attested`, `external_ci_run_attempt_attested`, `original_archive_sha_bound` et `study_admissible` demeurent `false`. Un vrai audit post-expérience devra comparer l'identifiant du run, le SHA événement signé et le numéro de tentative au verrou de cohorte, sans confiance circulaire envers les rapports produits par la naissance. La CI est strictement ciblée, sans matrice H192.

**A1-C: NO_GO. A2-R: NOT_EXECUTED. L3: NOT_ESTABLISHED.**