# A2.30-ZR : préenregistrement d'une vérification indépendante des morts motrices vécues en ZQ

**15 octobre 2026. Audit rétrospectif préenregistré APRÈS connaissance des résultats ZQ, mais AVANT tout code ZR.** Source physique et cognitive immuable : ZQ run [#38796937894](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38796937894), SHA du runner original `850256d02cdc9a2fc9be78f7ce1f66ca5dc98347`, étude prospectivement préenregistrée en ZQ à `cbd95fc2f0d6a5d66b682b7c97db6782605dbf1b`. **ZR ne crée aucun monde, aucune naissance, aucune action, aucun événement subjectif, aucune UC**. Il audite les deux archives originales Python 3.11 et 3.12 ; leur identité octet pour octet n'est pas supposée.

## Résultats ZQ déjà connus, donc NON prédictions de ZR

24 individus réellement autonomes, 408 pas, 208 recherches Stage6, 274 commandes east, 12 morts sous zone létale cachée, 12 paires mort/survie, 7954 UC acceptées, 0 refus UC, 0 collecte B, 0 ingestion B. Deux digests globaux de naissances diffèrent entre Python, `bb20c382ed5035b947735260674970afc541e9cd38a455b674b2c1c8a139a306` (3.12) et `f06c6fb0b4660c7593aad9c9bd37b948925bf4f3ec8773e448fe15c043211785` (3.11), tandis que le digest des 12 paires est `f9492892e50a21ddab3ebbab9534a38be4cf5f582856b284e9cb380acf1317a4`. **Les fichiers bruts doivent être récupérés et leurs SHA-256 complets fixés dans un second commit AVANT toute implémentation ZR**, sans altérer les fichiers sources. Si ces artefacts ne sont plus accessibles, statut `BLOCKED`, jamais preuve inventée.

## Questions indépendantes, sans importer le runner ZQ

**ZR1 : provenance des 24 naissances et du dénominateur.** Vérifier les 24 identités distinctes, les 12 cellules profil × layout × toxicité cachée, deux bras motor-clear/lethal par cellule, les 408 pas à partir des événements d'origine, l'absence de relance de corps mort et l'unicité des reçus de clôture. Les deux Pythons sont une réplication numérique, pas 48 naissances statistiques.

**ZR2 : véritable choix et parité pré-exposition.** Pour chacune des 12 paires, reconstruire en lecture seule, depuis les événements originaux et non depuis les compteurs de résumé, les commandes `command_experienced` et leurs `world_transition_experienced` joints par `(t_monde,attempt_ref)`, l'entrée à `(3,1)` depuis `(2,1)` par commande `se_deplacer(east)`, les captures sensorielles effectivement enregistrées (ou leur absence), les raisons et reçus de mortalité. Les identités distinctes ne prouvent pas l'identité des états internes ; **ne pas inventer une capture manquante**. La parité des seules observations enregistrées ne démontre pas l'identité de l'ensemble de la cognition cachée. Les labels de zone létale restent externes.

**ZR3 : frontière d'attribution causale.** Séparer explicitement (a) sélection de la commande motrice, (b) issue physique externe, (c) éventuel jugement proximal `self`, (d) jugement distal sur la cause de la mort. Un jugement `self` sur la commande ne constitue **jamais** une attribution subjective de la mort à la zone cachée. Si aucune attribution distale vivante n'existe, conserver `unknown`, même si la cause externe est certaine. Refuser tout récit d'expérience post mortem.

**ZR4 : comptabilité UC, WAL et terminalité.** Recalculer indépendamment les reçus `compute_charge` par module et `accepted`, les refus et les sommes ; ne pas compter les pas comme UC. Vérifier l'unicité des morts, la présence des commandes finales et transitions physiques, l'absence de nouvelle capture ou transition après mort. Si les journaux WAL bruts ne sont pas dans l'archive, **ne pas prétendre** les avoir revérifiés ; utiliser le niveau de preuve des artefacts disponibles.

**ZR5 : robustesse et falsification.** Exiger des tests négatifs qui altèrent les identités, le bras caché, l'emplacement de zone, les commandes choisies, les liens attempt_ref, les états perceptifs, la présence d'un journal terminal, la provenance d'un motif, les UC, une collecte B imaginaire, les timestamps post mortem, et un verdict `cause_death_subjectively_self` inventé. Un fichier de résumé qui reproduit les compteurs n'est pas une preuve indépendante si les reçus ne sont pas recomptés.

## Procédure et décisions

1. Télécharger les artefacts ZQ **de la première CI scellée à SHA `850256d...`**, contrôler tous les noms et les SHA complets et publier le manifeste de provenance avant le code de relecture.
2. Écrire un auditeur **standard library** sans importer le runner ZQ, le runtime I0, WorldBody, Stage6, Oracle ou les scripts d'évaluation ZB ; il doit opérer uniquement sur les reçus réellement archivés. Aucun moteur de simulation.
3. Exécuter des tests adversariaux et les vérifications sous Python 3.11 et 3.12 dans GitHub Actions, comparer explicitement les champs stables et les divergences numériques, conserver les fichiers bruts immuables.
4. Conclure `PASS` uniquement sur les assertions effectivement démontrées. Un audit des résumés seuls donne `INSUFFICIENT_SOURCE_EVIDENCE` sur la causalité vécue, pas un succès.
5. Ne modifier ni `src/i0`, ni le MVP v1.3.1, ni M11, ni Stage9/DC-05, ni UC ; ne pas merger les PR scientifiques empilées.

**Verdict initial ZR : EN ATTENTE, résultats ZQ connus, aucun nouveau résultat ZR. Stage12 PARTIAL ; A2.30 PARTIELLE ; issue #110 administrativement CLOSED, sans preuve de compétence alimentaire ni attribution subjective du décès ; NO-GO de déploiement.**
