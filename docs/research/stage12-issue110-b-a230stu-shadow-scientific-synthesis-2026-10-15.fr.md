# Décision de poursuite A2.30 après S-shadow / T-archive / U-physique

**15 octobre 2026.** La continuation validée par l'opérateur s'est limitée à des expériences non normatives. La PR [#191](https://github.com/josselin-orta-lab/individual-zero/pull/191) est empilée sur #189 mais **concurrente** des [#190](https://github.com/josselin-orta-lab/individual-zero/pull/190) (observations passives appariées) et [#192](https://github.com/josselin-orta-lab/individual-zero/pull/192) (proxy de planification alimentaire sous modèle P), chacune avec son propre préenregistrement. Les noms des workflows sont disjoints ; une revue d'intégration des dépendances sera nécessaire avant d'envisager une fusion. Aucune de ces PR n'a été fusionnée à `main` par la présente campagne.

## Trois résultats complémentaires

**S-shadow**, run #38740664255 : 72 mondes physiques/perceptifs contrôlés, **196 actes physiques** (64 mondes agis, 8 sans action), 44 ingestions et 24 décès externes. Deux mécanismes physiques alimentaires distincts peuvent donner la **même suite d'observations accessible** après `manger berry_a` : toxicité intrinsèque −7 ou dommage −7 provenant d'une zone activée exogènement au moment de l'ingestion. `attendre` une fois peut séparer les conséquences observables sur 4 paires au prix potentiel de 7 points d'intégrité, alors que manger à nouveau n'apporte pas d'information discriminante dans les 4 autres paires. Il est donc injustifié de traiter une baisse d'intégrité après ingestion comme preuve subjective de la responsabilité exclusive de la baie.

**Shadow Stage6**, dans S : **56/56 recherches `incomplete_model`**, toutes sans première arête prédictible, malgré la disponibilité *dans un modèle hypothétique parfait d'historique local* des deux collectes précédentes et, pour les 24 recherches post-ingestion vivantes, de l'expérience de la première ingestion. Le niveau d'état du moteur exact rend la reprise de ces connaissances hors de leur entrée exacte impossible. Un horizon plus grand ne reconstruit pas la première arête absente. Cela ne démontre pas que I0 réel a déjà appris ces effets, et ne prouve pas un défaut d'algorithme BFS.

**T/U**, runs #38741660739/#38742312358 : audit autonome des octets et recalcul des 56 statuts racine **puis** relecture indépendante `WorldBody.apply` sur 72 mondes techniques/196 pas, avec **0 divergence physique**, **0 action postmortem**, tests de falsification PASS. Ni T ni U ne sont des cohortes scientifiques indépendantes de S ; les deux versions Python ne le sont pas non plus.

## Séparations maintenues

- Observation corporelle accessible `≠` mécanisme causal définitivement identifié.
- Première transition connue `≠` plan alimentaire complet.
- Commandes préengagées par le laboratoire `≠` intention/motivation/choix autonome d'I0.
- Baisse d'intégrité détectée `≠` reconnaissance subjective exacte du danger.
- Agrégat de vérification externe `≠` responsabilité subjective Stage12.
- Relecture physique du même monde déterministe `≠` nouvelle réplication scientifique indépendante.

## Proposition prioritaire

Avant de modifier `EquipmentModel` ou la sémantique publique de Stage6, rassembler les preuves complémentaires des PR #190, #191 et #192 en **un tableau par variable perceptible, moment, coût physique, et impossibilité d'attribution**. Ensuite définir **hors I0** un protocole de choix d'une sonde qui présente un coût/budget UC explicitement borné et une abstention de sûreté lorsqu'une intervention informative exige une première exposition potentiellement létale. Une demande d'arbitrage opérateur sera indispensable avant d'installer un modèle, un planificateur probatoire ou une politique de sécurité différente dans le MVP normatif.

**Verdict : A2.30 PARTIELLE, Stage12 PARTIAL, #110 OPEN, PR #191 DRAFT.** Les preuves ne justifient ni le statut Stage terminé ni une nouvelle capacité cognitive déployée.
