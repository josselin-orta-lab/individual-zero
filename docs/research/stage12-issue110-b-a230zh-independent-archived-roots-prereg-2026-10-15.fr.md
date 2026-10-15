# A2.30-ZH : préenregistrement après ZG, audit indépendant en lecture seule du modèle réellement aligné sur les racines B

**15 octobre 2026 ; après résultats ZG connus, AVANT le code et l'exécution de ZH.** Ceci est un **contrôle secondaire rétrospectif** des archives de la même campagne, et non une nouvelle expérience ni de nouvelles naissances. ZG a déjà conclu au run original [#38777542232](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38777542232), au code `f416424292501671eda7f9ed65accb7a2712f9ef` : 6 mondes physiques de démonstration, 14 applications `WorldBody.apply`, 12 racines initiales historiques I0 ZB, 24 recherches Stage6 en shadow, 8/8 premières arêtes B connues et 8/8 `partial_progress` avec premier acte B, contre 8/8 `incomplete_model` pour ces naissances au modèle historique A. **Les résultats préexistants sont publics : l'auditeur ne doit pas prétendre les découvrir prospectivement.**

## Ancrage immuable des deux sources de données

**ZG run original : #38777542232.** Les trois fichiers des artefacts `a230zg-py3.11` et `a230zg-py3.12` sont **identiques octet par octet** ; SHA-256 complets connus :
- `a230zg-physical-demonstrations.json` : `53f0363f09df2e23984d75bcdddb98550adeb1f35b015810a1b8ad5d37c91625`.
- `a230zg-lived-birth-shadow.json` : `fdfafde49f92f2feb26b41b42e71106766b5f30f3c33fb191ef53866705a9875`.
- `a230zg-summary.json` : `6af19338b42d9d3f17d26e9c3f1fe051e55f47e1fc3e04e7b66ccd5301b78617`.

**ZB run original : #38767643472, SHA naissance `2a19742df22f27752635203304097134a3009c45`.** Les deux `a230zb-summary.json` ne sont pas identiques (dérive ULP Stage8 historique déjà constatée par ZD), mais les douze *perceptions initiales et actes physiques* le sont. SHA-256 :
- Python 3.11 : `ea7ed0d4fa92f5b47e71f9e9ba98dc2bf5c49aa39a3de40068a00b284314c85b`.
- Python 3.12 : `ecd2700f119d1e8f7ee2c07c89c5e7acaa5c0c66bc4abd016412b1ee89872362`.

Chaque JSON doit être lu depuis **l'artefact du run indiqué**, vérifier son SHA exact et son **unicité** dans chaque dossier. Ne jamais substituer un fichier généré avec le nouvel auditeur ni une version d'une PR renommée.

## Missions de l'auditeur ZH, strictement indépendantes du runner ZG

1. **Aucun import de `run_stage12_issue110_b_a230zg_lived_root_shadow`, de `WorldBody`, de `EquipmentCorpusRecorder`, d'un modèle exact ni du code du `SimulatorPlanner.search`.** Reconstituer uniquement depuis les archives le graphe de couples `SimulationState × PrimitiveCommand`, et vérifier les empreintes SHA, l'intégrité des suites de transitions, la disponibilité de ressource au `collecter(B)`, la passabilité au `se_deplacer(east)`, et la première vraie perception accessible avant chaque commande de démonstration.
2. Depuis les deux résumés ZB archivés, joindre les douze `birth_id`, les perceptions initiales complètes, les deux profils, les trois dispositions B, les deux effets cachés, l'empreinte A déjà présente à la naissance et la mortalité; comparer chaque valeur avec la copie publiée par ZG, sans permettre d'utiliser le paramètre caché de B comme une entrée de décision ou modèle.
3. Calculer séparément le dictionnaire **A seul** (4 expériences A par profil) et **A+B non ingestif** (3 expériences B additionnelles par profil), sans transférer d'exemple d'un profil à l'autre. **Contradiction physique pour le même état+commande : FAIL**. La différence entre graphes doit contenir les clés B physiquement observées seulement, sans aucune clé `manger(B)`.
4. Énumérer les commandes admissibles de la première perception via les critères publics Stage6, **réimplémentés dans l'auditeur**, et compter les clés exactes prévisibles avec A puis A+B. Comparer les nombres avec les compteurs `root_candidate_edges`, `root_available_edges`, `root_unavailable_edges` publiés par ZG sur **les 24 recherches**, plus les 8 commandes B initiales référencées. Chaque commande shadow présentée comme physiquement dispatchée = FAIL.
5. Contrôler que les résultats publiés sont bien les suivants, sous le périmètre *déjà connu* : B_LOCAL 4/4 `collecter(B)` puis B_EAST 4/4 `se_deplacer(east)` **comme premier acte seulement prédit**, avec `partial_progress`; B_NONE 4/4 conserve une proposition `se_deplacer(north)` issue du modèle A. Aucun `manger(B)` prévu ni certificat de sûreté. Les six paires d'effets cachés doivent produire des racines/perceptions et résultats shadow identiques.
6. Contrôles adversariaux exigés **avant de déclarer PASS** : altérer l'un des trois SHA originaux, falsifier un exemple `collecter(B)` qui ne voit pas B, inventer `manger(B)`, annoncer une arête connue hors source, injecter une variable cachée dans la perception t0, forger un passage `plan_found` ou une action shadow exécutée, déclarer des UC vécues, altérer un identifiant de naissance ou attribuer une transition A à un autre profil. Un conflit d'entraînement exact-key doit faire échouer l'audit.

## Ce que l'audit ne prouve pas

Un recalcul d'archives ne démontre pas indépendamment l'exécution historique `WorldBody.apply`; celle-ci reste attestée par le runner ZG original (et ses tests) ou par une relecture physique séparée. ZH ne peut valider la sûreté ou l'efficacité réelle d'une politique cognitive. Il prouve au plus que la **capacité mécanique de rechercher une sous-étape B** est compatible avec les observations et transitions physiquement consignées. Le modèle enrichi est exclusivement **externe** et contiendrait, s'il était transféré, des expériences d'un autre monde interdites comme vécu propre à I0 sans nouveau contrat normatif.

**Verdict attendu : ZH PASS technique si archivage/origines/recomptages/négatifs passent, sinon FAIL en conservant ZG original intact. Zéro nouveau monde, pas physique, naissance ou UC vécue. A2.30 PARTIELLE, Stage12 PARTIAL, issue #110 OPEN, PR #200 DRAFT, déploiement cognitif NO-GO.**
