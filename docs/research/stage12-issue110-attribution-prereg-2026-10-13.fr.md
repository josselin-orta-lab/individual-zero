# Issue #110 — Préenregistrement de l'audit de provenance d'attribution (2026-10-13)

**Statut : protocole exploratoire préenregistré, aucune réception scientifique ou opérateur.**
Référence immuable au démarrage : `main` `f9de6aa6cd11f896db204c0277353989d6445f10`.
Norme non modifiée : `docs/architecture/reference/en/mvp-specification-v1.3.1.md`, conservant v1.2.1 §9.6, §16.1, §20.3, DC-06 et DC-07.
Issue : #110. Le Stage 9 reste NO-GO.

## Hypothèses distinctes, décidées avant exécution

- **H-R (résultat vécu) :** le registre de progression à un pas peut parfois préenregistrer, puis vérifier indépendamment, des gains et des non-gains mesurés. Un non-gain n'est pas une mauvaise prédiction et un gain ne démontre ni atteinte du but global ni causalité personnelle.
- **H-A (attribution authentique) :** le runtime courant ne dispose d'aucun producteur explicite d'un jugement subjectif `self/world` portant sur *ce résultat* et doté de sa provenance propre. Les catégories P-47 `self_compatible/world_justified/uncertain` ne peuvent pas servir de conversion implicite. Le résultat attendu est donc **zéro couple admis**, même avec des critères d'objectif vérifiés.
- **H-D (diagnostic) :** tant que H-A manque, `attribution_bias=None` doit persister, même après 600 pas physiques et même si la chaîne cryptographique d'un journal falsifié est recalculée.
- **H-I (isolation) :** les audits et données de laboratoire ne rétroagissent jamais sur I0, ses commandes ou ses propriétaires cognitifs.

## Expérience et contrôles

1. Exécuter les tests réels ciblés du registre de progression, du détecteur pur, de la métacognition et du vérificateur externe, sous Python 3.11 et 3.12. Inclure les cas succès, non-gain, refus UC, disparition d'observation, doublon, falsification avec rechaining, mortalité et restauration.
2. Sur la branche exacte de la PR, exécuter le runner existant `scripts/run_stage12_operator_trial.py` sur une **vie neuve**, jusqu'à 600 pas physiques maximum, avec sa graine/configuration figées. Conserver WAL, journal JSONL, manifeste, arrêts et diagnostics, y compris un résultat négatif.
3. Confronter le journal à `audit_export_bytes`, `audit_stage12_goal_progress`, `audit_stage12_diagnostics` et à l'audit indépendant dédié #110, en utilisant les empreintes `head_hash` et `occurrences` de provenance. Compter les critères préenregistrés, succès et non-gains vérifiés, observations inconnues, débits acceptés et refusés, comparaisons P-47 rapportées, paires admissibles et diagnostics.
4. Contrôles adversariaux : (a) altérer un diagnostic pour revendiquer un biais, (b) injecter un triplet `outcome/agency/attribution_ref` sans origine contractuelle puis recalculer correctement chaque hash ; le vérificateur **doit refuser** dans les deux cas. Une prédiction P-47 différente, à conséquence identique, ne suffit jamais à produire une attribution.
5. Rester sur la seule trajectoire fixe si aucun producteur cognitif légitime n'a été identifié : produire davantage de vies ou baisser les seuils ne résoudrait pas H-A. Toute campagne contrastée destinée à tester un *nouveau producteur* requiert son contrat normatif accepté et un préenregistrement distinct.

## Critères d'interprétation et d'arrêt

- **PASS ciblé logiciel :** les audits reconnaissent les résultats vécus distincts des prédictions, refusent des assertions d'attribution sans source, et le runtime garde `attribution_bias=None` tant que les triplets indépendants sont absents. La CI exacte des deux Python doit être verte avant toute revendication de PASS.
- **Blocage de #110 :** aucun jugement de causalité du résultat authentiquement porté par I0. Une réussite de l'audit d'absence n'est pas une réussite du détecteur en condition vécue.
- **Arrêt :** décès irréversible, refus physique, arrêt opérateur ou défaillance transactionnelle : ne jamais relancer/rejouer l'identité morte, ni la prolonger fictivement pour atteindre 600.
- **Portée :** 3.11 et 3.12 sur la même graine sont une vérification de reproductibilité logicielle, **pas** deux vies scientifiquement indépendantes. Cette campagne ne certifie ni les 4 classes de biais ni la vérité physique externe.

Toute évolution créant des jugements subjectifs `self/world` sur les résultats doit être présentée sous forme de proposition normative non adoptée avant modification du noyau. Le dossier de clôture reste interdit tant que la jointure et l'audit indépendants ne sont pas effectivement démontrés.
