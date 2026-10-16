# Option B : résultats B-L600 et B-M48 et verdict d'intégration

**15 octobre 2026.** Préenregistrement avant code : `docs/research/stage12-issue110-b-l600-m48-prereg-2026-10-15.fr.md`. Code expérimental testé à `a29b366a508a388e39f527e4be4873367091fa33`. [GitHub Actions #38687269675](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38687269675) : **4/4 jobs SUCCESS**, deux modes sous Python 3.11 et Python 3.12.

## Résultats observés dans les journaux des jobs

| Contrôle | B-L600 WAL | B-M48 SQLite M-11 |
| --- | ---: | ---: |
| Monde réellement vécu avec B activé à la naissance | 600 pas | 48 pas |
| Distinctes références de vie | 1 | 1 |
| Reprise à froid | non demandée | après génération 24 |
| Statut vital final | active | active |
| Entrées du journal canonique | 163124 | 12980 |
| Préengagements B | 1 | 1 |
| Jugements B | 1 | 1 |
| Indisponibles | 0 | 0 |
| Préengagements non clos | 0 | 0 |
| Émetteurs / attestations originales, duales et hash | PASS | PASS |
| Paires GA-06 héritées interdites en mode B | PASS | PASS |
| Vérification Python 3.11/3.12 | PASS/PASS | PASS/PASS |

B-L600 : `journal_head=3fc2722e2e5d070d7176709d5da9592e778253a9583b2e8fd88c8fc6ecc26ac4`, 163124 événements, SHA256 export `ade4865a1337ab71a309b023a3deebe1af1e3174bc64e0fc1f62411dcfdef513`, identiques dans les deux jobs. Audit WAL accepté. Vie B réellement active au pas 600.

B-M48 : `journal_head=3b4c4fde3ce2a013dd7879b3bfc4204f8f7198e8cc6631f30101b6ee2d493320`, 12980 événements, SHA256 export `931798969d78bcad511d1cd67b28da7a525fe24ce03c9159a59a808ad81bc8c8`, identiques sous les deux Python. La génération 24 a pour tête `c47a4f2797a4591ba5e1d0b3ced40e10ed9c5abcda21fe56b2aca7cd531858de`, conservée dans le préfixe après la continuation ; génération 48 et état vital actif. Aucun replay de commande revendiqué ; audit M-11 de la même vie.

## Verdict scientifique strict

**PASS technique borné** du contrat B, de la conservation des deux types de reçus et de leur continuité sur la durée et sous M-11. **Échec de couverture scientifique suffisante** : dans chaque vie, un seul jugement B a été émis, ce qui représente 1/600 et 1/48 jugements par pas. Les quatre jobs ne sont pas quatre vies randomisées indépendantes : deux versions Python rejouent les mêmes scénarios. Le résultat ne peut tester les contrastes success/failure nécessaires à GA-06, ni la précision subjective, ni établir `self` distal.

Ce constat ne doit pas déclencher de modification ad hoc des seuils ou une production de paires synthétiques. La prochaine investigation doit mesurer **pourquoi** si peu de préengagements cognitifs sont admissibles pendant des vies longues, et quels facteurs de naissance / buts / UC / sommeil expliquent l'attrition, sans imposer les actions à l'individu.

La chaîne de garde de la sensation garantit la concordance journalisée et sa reprise, **pas** la vérité physique de la perception. De même, même une collecte ou une ingestion authentiquement exécutée ne prouve pas la contribution causale distale au résultat alimentaire.

## Gate d'intégration

Le code ne change pas la norme MVP v1.3.1 ; B est une option architecturale approuvée mais pas encore validée comme compétence subjective fiable. La campagne B-L600/B-M48 ne couvre pas les cas exogènes opposés dans des vies longues ni les UC refusées pendant ces mêmes vies. **Ne pas fermer #110 ni déclarer Stage12 PASS scientifique.** L'intégration du code B en mode opt-in peut être étudiée comme étape technique séparée, sous réserve des CI du dernier commit documentaire et des régressions ciblées, sans l'activer par défaut.

**PR #184 actuellement DRAFT, Stage12 PARTIAL, issue #110 OPEN, réception opérateur non effectuée.**
