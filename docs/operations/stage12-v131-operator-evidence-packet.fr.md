# Réception technique Stage 12 : paquet opérateur v1.3.1

**Statut : EN COURS.** Cette procédure vise l'opérateur, sans déclarer de réussite scientifique ni de conformité M-11. La branche de test combiné est la [PR #109](https://github.com/josselin-orta-lab/individual-zero/pull/109), **à ne jamais fusionner**. Source normative : `docs/architecture/reference/en/mvp-specification-v1.3.1.md`.

## 1. Préparer le contrôle reproductible

Sur un checkout *détaché* du SHA précis affiché par la PR #109 :

```bash
python3 -m pip install -e .
python3 -m unittest discover -s tests -p 'test_stage12_operator_packet.py' -v
python3 -m unittest discover -s tests -p 'test_stage12_occupancy_runtime.py' -v
python3 -m unittest discover -s tests -p 'test_stage12_operator_alert_runtime.py' -v
python3 -m unittest discover -s tests -p 'test_v131_stage12_autonomous_600_steps.py' -v
```

La dernière commande exécute **600 véritables transitions de monde** avec un plafond d'arrêt non létal à la dernière transition. C'est un protocole logiciel à paramètres de développement, avec sommeil rendu inactif par configuration déclarée. Il **ne valide pas les effets du sommeil**, la survie en conditions variées ni le biais d'attribution. Le test supprime son répertoire temporaire : il ne sert pas d'archive opérateur persistante.

## Essai opérateur conservé (nouveau)

Pour garder une vraie archive au lieu du seul répertoire temporaire des tests :

```bash
python3 scripts/run_stage12_operator_trial.py \
  --output-dir /chemin/vers/nouvel-essai-stage12 \
  --steps 600
```

Le répertoire cible **doit ne pas exister**. La commande crée un WAL fsync, un `canonical-export.jsonl` sans saut final et un `trial-manifest.json`, puis vérifie de façon indépendante les données techniques. **L'essai exige, avant toute naissance, un checkout Git identifié, propre et complet.** Le dépôt Git doit avoir sa racine exactement à la racine du runner, les fichiers critiques (runner, auditeur, spécification, moteur déterministe, runtime Stage 12, détecteurs et manifeste Python) doivent être effectivement suivis dans l'index Git, et les modules Python critiques importés doivent provenir des fichiers attendus de ce checkout. Un fichier de référence seulement présent mais non versionné ne suffit pas. Il refuse un checkout sale, un Git absent ou un fichier de référence indisponible sans créer de dossier ni d'individu. Le manifeste conserve le commit Git exact, le SHA-256 de l'ensemble des fichiers suivis (chemins, contenus et modes), leur nombre, la version corrective de Python et les SHA-256 de la spécification, du moteur de déterminisme et de `pyproject.toml`. Toutes ces empreintes sont comparées avant et après l'essai pour détecter une modification du code durant la vie. Elle refuse tout écrasement ou poursuite d'une ancienne identité. Le code de retour `0` signifie que les pas demandés ont réellement été appliqués, suivis de l'arrêt opérateur terminal et d'un audit technique cohérent ; `2` signifie une campagne incomplète à ne **jamais** reprendre, et `1` une configuration ou écriture refusée. Les traces partielles d'une campagne interrompue peuvent subsister : ne pas les interpréter comme une vie toujours active.

La configuration est **figée pour ce démonstrateur**, avec mode veille désactivé volontairement ; elle n'est **pas** une expérience scientifique représentative ni une campagne de sommeil. Conserver hors de ce dossier la valeur `head_hash` et `occurrences` du manifeste, avant toute manipulation de l'archive. Le manifeste seul dans le même dossier **n'est pas une ancre indépendante**. La version exacte des dépendances n'étant pas verrouillée par un fichier de lock dans ce dépôt, l'essai ne prétend pas certifier un replay déterministe entre machines ou environnements différents. Un checkout modifié pendant la vie rend l'essai technique incomplet. Les fichiers non suivis hors de ces chemins critiques et la totalité des dépendances importées ne sont pas couverts par une garantie de provenance complète ; le contrôle initial et final ne gèle pas les octets pendant l'exécution. La validation humaine et la preuve physique restent externes.

## 2. Contrôler un export réel et conservé

À partir d'un runtime Stage 12 ou d'Individual Zero Observer, conserver un **export causal canonique complet** en dehors du runtime cognitif et relever **séparément** son hachage de tête et son nombre d'occurrences dans un registre opérateur. Ne pas passer le fichier WAL brut terminant chaque enregistrement par un séparateur ; le vérificateur attend l'export canonique sans saut de ligne terminal.

```bash
python3 scripts/report_stage12_operator_packet.py /chemin/export-canonique.jsonl \
  --expected-head <SHA256_DE_CONFIANCE> \
  --expected-count <NOMBRE_OCCURRENCES_DE_CONFIANCE> \
  --expected-world-steps 600 \
  --require-terminal-stop
```

Le programme ne charge **aucune vie d'I0** et ne lit ni l'Oracle ni le banc d'évaluation. Les six contrôles exécutés sur les **mêmes octets et mêmes ancres** sont : intégrité causale complète, diagnostics et coûts UC, occupation de S_t par module, alertes persistantes, alignement buts/actions physiques, et **cohérence du contrôle opérateur** (configuration, plafonds monotones, arrêt final et identité des événements). Les événements non reconnus sont signalés par l'auditeur générique ; ils ne constituent pas une preuve implicite de conformité. L'audit opérateur vérifie une **séquence technique cohérente**, pas l'identité physique ni la signature cryptographique d'un humain ayant approuvé la commande.

Si l'opérateur demande exactement 600 pas, un pas seulement fermé mais **sans commande physique exécutée** ne compte pas. Les 600 commandes doivent avoir de vrais reçus de monde ; chaque **pas physique distinct réellement exécuté** doit disposer d'un diagnostic Stage 12 payé et d'au moins une mesure de S_t valide. Plusieurs cycles et plusieurs mesures pendant un même pas ne compensent jamais l'absence de preuve pour un autre pas. Un refus de budget ou un décès précoce n'est pas maquillé en 600 pas accomplis.

**Codes de retour :** 0 signifie uniquement que l'export respecte les contrats logiciels testés et les attentes explicites ; 1 indique une incohérence, une couverture insuffisante, une ancre fausse ou un export indisponible.

## 3. Limites et décision humaine

- Un hachage et un compteur calculés **à partir du même export potentiellement tronqué** ne fournissent aucune provenance physique indépendante ; conserver les ancres à part. Même avec un hachage valide, l'audit ne vérifie pas la vérité physique cachée du monde.
- Les statistiques d'alignement utilisent des justifications traçables, pas des intentions objectivement prouvées. La catégorie « sans justification traçable » ne signifie ni irrationnel ni dangereux.
- La calibration d'attribution vécue reste absente [issue #110](https://github.com/josselin-orta-lab/individual-zero/issues/110), aucun `conforming` de P-47 ne vaut réussite. L'auditeur refuse donc les attributions non vérifiées. Le paquet contient désormais `lived_attribution_evidence` : nombre de réussites, échecs et références **indépendamment admis par l'auditeur** (actuellement zéro), et nombre de diagnostics non accompagnés de paires vécues authentifiées. « Zéro admis » ne signifie ni que l'individu a échoué, ni qu'il n'a eu aucune attribution subjective non enregistrée. Même après 600 pas, ce verrou reste ouvert.
- **M-11 reste FAIL** jusqu'à ce que la version complète de l'option A soit reliée à la génération courante du monde, des états cognitifs et du journal, avec crash/reprise sans résurrection.
- Une campagne de 600 pas n'est qu'une **hypothèse de bon fonctionnement**, pas la validation scientifique finale. L'approbation Stage 12 est réservée à l'opérateur, module par module et après examen des lacunes.

À conserver : SHA Git exact, paramètres de simulation, résultat terminal, compte des pas effectivement appliqués, état des alertes, hachage de tête/compteur indépendant, anomalies et décision explicite `EN COURS`, `PRÊT POUR VALIDATION OPÉRATEUR` ou `VALIDÉ PAR L'OPÉRATEUR`. Ce paquet de tests **n'autorise aucun merge automatique**.
