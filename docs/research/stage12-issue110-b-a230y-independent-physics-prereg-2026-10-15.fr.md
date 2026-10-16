# A2.30-Y : préenregistrement de la relecture physique indépendante de W

**15 octobre 2026, APRÈS résultats W et recalcul X, AVANT code Y.** Source scientifique originale figée [W Actions #38753518412](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38753518412), SHA `aecb8d1172846620c3038a4bc10e7716ec7bde1e`. X [#38754552318](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38754552318) confirme les archives mais **ne réexécute pas le monde**. Y vise une vérification physique distincte du runner de W. Résultats **connus avant code Y** : 80 mondes agis/240 actions, 12 témoins passifs, 16 morts, 160 paires indistinguables au moment de la décision ; les statistiques X doivent être recoupées, pas proclamées nouvelles.

## Indépendance du replay et physique autorisée

Télécharger uniquement l'artefact `a230w-py3.11` du run original W, et en vérifier les **trois SHA-256 intégralement** :

- agis `999b0ade7734b5591e26eec0c4e2fbfa57a8d6742f5aa229476df9b8caca1889`
- contrôles `dcfcacc9f44644a137f6c334dc13fcbac0173d3b07787b6e7ee1b548352fc666`
- summary `859806366dea71e30c791889e6cef0f4195bd40d78fa9c135b32c894f24a23c9`.

Créer 80 **nouvelles instances `WorldBody` détachées** +12 témoins passifs. Reconstituer les `WorldPhysicsConfig`/`WorldLayout` de la matrice W avec le **constructeur indépendant** `independently_configure` déjà développé pour A2.30-R (ce code n'importe pas W et ne reprend pas son builder P), et contrôler leurs hashes contre ceux des reçus **avant chaque première action**. Reconstituer les préfixes W seulement depuis le protocole : `immediate` (), `wait_twice` (attendre×2), `collect_first` (collecter berry_a), `west_return` (ouest puis est), suivis de la phase de collecte éventuelle et ingestion physique. Les commandes doivent être fixées avant de comparer leurs conséquences archivées.

À chaque pas, capturer `SymbolicPerception.capture` + `state_from_capture` avant l'action, appeler **`WorldBody.apply` réellement**, re-capturer l'état, et comparer **octet logique par octet logique** les états accessibles avant/après, commandes, labels de terminalité et empreintes SHA de chaque reçu original. Ne jamais importer `run_stage12_issue110_b_a230w_prospective_probes`, `EquipmentCorpusRecorder`, `SimulatorPlanner`, Oracle, Bench ni le modèle P dans ce runner Y. Cesser définitivement à l'issue létale : `freeze_terminal_state()`, aucune action ou création de capture vécue postmortem. Pour les 12 témoins passifs, reconstituer l'espèce visible ou l'obstacle ouest et vérifier la capture t1, sans acte.

**Relecture prévue : 92 instances physiques distinctes, 240 actions supplémentaires de REPLAY TECHNIQUE**, dont 16 décès, **zéro nouvelles conditions scientifiques indépendantes, zéro I0 autonome**. Ces 240 pas ne doublent **pas** la cohorte scientifique originale W dans l'interprétation des preuves. Python 3.11/3.12 peut redoubler les relectures techniques mais ne multiplie pas les échantillons.

## Contrôles négatifs obligatoires

Une altération de hash de configuration ou de layout physique, une conséquence corporelle falsifiée **même après recalcul de son hash**, un pas terminal remplacé, une observation pré-exposition fabriquée, une commande préfixe modifiée, une observation prétendument vécue après la mortalité, et une ressource/obstacle visible falsifié doivent tous provoquer FAIL. Une vérification de physique Y réussie reste **relative aux règles de `WorldBody`**, non une démonstration de vérité externe, de politique alimentaire universellement sûre ou d'agence subjective.

**A2.30 PARTIELLE, Stage12 PARTIAL, #110 OPEN, PR #194 DRAFT.** Aucune autorisation d'intégration normative ou cognitive n'est impliquée.
