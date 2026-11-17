# i3 · Stage8-A · audit indépendant des 23 040 vies originales (post hoc, lecture seule)

**Nature : audit technique supplémentaire, après l'expérience prospective terminée. Aucune nouvelle vie, aucun nouveau tirage, aucune modification des critères, aucun replay physique.**

Source scientifique de l'expérience **fermée** : Git `ac353a9c4206ee3ecfd90bb101e26d092103958b`, GitHub run [#43950098410](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43950098410), science plan SHA256 `dcd93550453541273c940f78fc459dd3f4deaa807911cb89992c4d1eb7d3b660`. Verdict primaire publié : `STAGE8A_MEAN_PERSISTENCE_ADVANTAGE_F0`, moyenne G2 +14,4874131944 pas, borne inférieure t unilatérale 97,5 % +7,9933122338, 23 populations positives et 9 négatives. Les audits qui ne retrouvent pas ces chiffres **doivent échouer**, pas les réinterpréter.

## Séparation indépendante du code expérimental

Le nouveau `src/i3/lab/stage8a_independent_original_audit.py` importe **uniquement** le lecteur gzip original et vérificateur natif scellé de Stage7 (écrit avant l'étude Stage8-A), ainsi que des modules Python standards. Il n'importe ni `stage8a_mean_persistence.py`, ni le moteur `run_life`, ni l'écologie `WorldSpec`, ni les routines de mutation. Il ne peut ni ouvrir de monde, ni calculer des actions d'individus ni générer de nouvelles graines.

Sur les copies **non modifiées** des trois artefacts du run original :
- plan scientifique **14278546177**, `SCIENCE_PLAN.json`;
- **23 040 vies originales gzip** **14289668087**, comprenant `PANEL_0/` et `PANEL_1/`, `G0/G1/G2`, les manifestes, les 18 phases, les fichiers `SELECT_G1`/`SELECT_G2` et la réduction scientifique scellée ;
- résultat scientifique **14289613177**, `SCIENCE_RESULT.json`.

Il vérifie les deux plans de panneaux de 16 populations et leurs allocations source-exactes ; l'unicité des graines entre panneaux ; chaque fichier original compressé **et** décompressé contre son SHA256 ; chaque identité (population, génération, bras, génome, famille F0, répétition, World et life seed), 400 pas maximum, morts au pas 400 distinctes des censures, coûts de cognition énergie/vigilance, six occasions par individu et 144 vies par population/bras ; les trois manifestes et neuf phases scellées par panneau, les reçus techniques et la réduction finale.

À partir des **pas vécus entiers directement relus**, il recalcule les 32 différences G2 sélectionné − parents uniformes (`/144`), la moyenne, l'écart-type interpopulations, la borne inférieure t unilatérale à 97,5 % et les comptes favorables/défavorables/nuls ; il contrôle également les durées G0/G1 et les taux censurés G2. Tout désaccord avec le résultat préexposé, les 32 indices ou les empreintes déclenche un **échec d'audit technique** ; pas un changement du verdict prospectif, et **aucun retry du run scientifique fermé**.

## Exécution de l'audit

Un workflow distinct `.github/workflows/i3-stage8a-readonly-original-audit-20261117.yml` télécharge **en lecture seule** les artefacts du run historique via le jeton GitHub Actions à permission `actions:read`. Il doit publier un unique `READ_ONLY_AUDIT.json`, avec `original_lives_rehashed=23040`, `populations_reduced=32`, `new_lives=0`, ou échouer explicitement. Sa propre source de vérification a un nouveau HEAD : ce HEAD n'est **pas** le code de la campagne scientifique. La compilation/tests unitaires ne constituent pas une relecture des 23 040 archives.

**Limites de l'indépendance :** la relecture des **enregistrements SHA-liés** est indépendante du réducteur Stage8-A, mais réutilise les fichiers originaux GitHub. Elle n'atteste ni la naissance des individus par un témoin externe, ni l'indépendance des flux de graines, ni le rejeu fidèle de toutes les actions, ni la randomisation des étiquettes des bras ou l'indépendance parfaite des 32 populations. Les neuf populations défavorables et toutes les écologies F0 doivent rester dans le résultat. Stage7 et Stage6 conservent leurs verdicts négatifs sur leurs questions distinctes ; Stage2.1 général demeure `NOT_ISSUED/HOLD_NO_VERDICT`, I1 actif, I3 non promu.

**Au moment de la création de ce protocole d'audit**, le code/tests sont proposés ; l'audit original complet n'est **pas encore exécuté**. Ne pas annoncer `READ_ONLY_REPRODUCTION_OK` sans le job GitHub terminé et l'artefact validé.
