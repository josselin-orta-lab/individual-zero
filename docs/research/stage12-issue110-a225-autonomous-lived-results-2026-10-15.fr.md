# Individual Zero Stage12 #110 : résultats A2.25, résultats autonomes et attribution proximale/distale

**15 octobre 2026. Verdict scientifique : PARTIAL.** Préenregistrement avant code `3391805e76ecd2362646eace30d7d3b1f3bd3ec8`, version initiale `edd7d958`, [CI initiale #38649266676](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38649266676) **FAIL sous Python 3.11/3.12**. Diagnostic **post hoc** préannoncé avant le correctif dans `stage12-issue110-a225b-exogenous-followup-confounding-2026-10-15.fr.md` (`5fb7bd0d`). Instrumentation révisée `cdf01013` ; [CI révision #38650443356](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38650443356). Les nombres ci-dessous sont ceux du job Python 3.12 **SUCCESS** de cette version ; le statut de la répétition Python 3.11 doit être vérifié à part avant la fusion. Le rapport est volontairement distinct du verdict de la CI du dernier commit documentaire.

## Résultats physiques

**16 naissances Stage12 autonomes, 16 × 48 pas = 768 vraies transitions fermées**, quatre profils `restored/sustained/episodic/marginal`, obstacle extérieur OFF/ON, impulsion extérieure `set_body(food=80)` OFF/ON. Les deux Python rejouent la même matrice : ils ne doublent pas l'échantillon. Chaque commande est choisie par I0 ; aucun effet de laboratoire n'est promu en jugement subjectif. **8/8 impulsions extérieures `food=80` ont réellement été reçues et appliquées à t4**, confirmées par source de scénario et audit de journal. **4 véritables ingestions** apparaissent dans les vies non perturbées par ce pulse.

La revue originale des archives brutes montre **12 augmentations nettes de nourriture corporelle**, dont 8 en présence du pulse sans commande `manger` à ce pas et 4 ingestions réellement choisies, et aucune coexistence `manger` + pulse dans cette matrice. L'augmentation de nourriture due au pulse n'est **pas** une preuve que l'individu a causé le résultat. Les captures sont durablement journalisées ; les observations et les commandes conservent leur propre provenance.

## Refus scientifique, non transformé en succès

Le premier code de recensement cherchait un nombre JSON `80.0` là où l'archive canonique porte `{"$f64":"0x1.4000000000000p+6"}`. Cela créait **8 erreurs de compteur** sans annuler l'intervention physique. Le correctif `cdf01013` décode uniquement les reçus numériques et relie chaque `external_input_received` à son `external_input_applied`, avec ordre de perception.

Le point important est plus substantiel : dans **3 vies `free/pulse`** (`restored`, `sustained`, `episodic`) une préinscription d'amélioration alimentaire à t3 est évaluée à t4 **après** l'injection exogène avant ce nouveau pas. L'auditeur `audit_stage12_goal_progress` refuse légitimement le suivi : la mesure alimentaire à t4 est différente du `body_after` de la transition t3. Le code A2.25b **ne change pas cet auditeur** et marque ces trois vies `fail_closed_exogenous_confounded`. Leurs totaux `goal_success/agency/pairs` **ne sont pas crédités à la catégorie indépendamment vérifiée**. Les 13 autres vies doivent passer inchangées les audits originaux et être comptées à leur portée propre. Aucune paire fabriquée ni baisse du seuil `2+2/12`.

La première CI rouge demeure donc scientifiquement utile et **le critère initial T4 d'audit complet n'est pas satisfait**. Une CI verte de l'instrumentation révisée atteste la bonne reconnaissance des sources confondantes, pas la validation épistémique des trois suivis d'objectif. Cette violation potentielle du modèle « suivi un pas / intervention prépas » appelle une décision normative indépendante, pas une désactivation de l'audit.

## GA-06 et interprétation

D'après la révision Python 3.12 `cdf01013`, **0 vie n'atteint le seuil 2 succès + 2 échecs dans une fenêtre de 12 diagnostics éveillés**. Au sein des **13 vies à audits complets**, les sommes de reçus vérifiés sont **6 succès d'objectif, 8 échecs, 4 jugements `unknown` et 7 paires GA-06 appliquées**. Ces totaux sont descriptifs à l'échelle du corpus, **ils ne deviennent jamais une fenêtre inter-vies** et excluent les trois vies confondues. Les 12 paires `stage12_attribution_pair_admitted` observables dans le corpus brut initial ne sont pas 12 paires indépendamment validées ni toutes consommées.

**Conclusion :** A2.25 teste enfin des conséquences réellement vécues dans des vies cognitives autonomes, y compris huit améliorations alimentaires entièrement extérieures. Ces expériences renforcent la nécessité de séparer « commande proximale exécutée », « résultat de l'objectif observé » et « cause attribuable à l'individu ». Aucune sonde externe n'est remontée dans sa cognition ; aucune modification normative du jugement d'agence n'est justifiée.

## Statuts

- T1/T2/T3 : **PASS technique borné**, sous réserve de la CI finale répliquée.
- T4 : **FAIL pour 3 suivis confondus** ; refus préexistant conservé, pas de calibration créditée.
- T5/T6 : descriptif des paires et répétition CI à finaliser.
- T7 : PASS en matière de **fichiers modifiés uniquement** (scripts, documentation, workflow).

**Stage12 PARTIAL, issue #110 OPEN, réception opérateur absente**, MVP v1.3.1 inchangé. Pas d'ajout d'UC, de second WAL M-11, de contrôle Oracle, ni de politique de révision subjective. Une nouvelle cohorte préenregistrée indépendante devra reproduire ce résultat et préciser la sémantique temporelle du critère physique lors d'une intervention extérieure avant observation, sans rétroactivité sur les vies existantes.
