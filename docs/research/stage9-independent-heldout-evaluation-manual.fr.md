# Individual Zero · Stage 9
## Manuel d'exécution et d'évaluation indépendante de la campagne *held-out*

**Version du manuel :** 1.1 · 10 octobre 2026  
**Langue :** français  
**Destinataires :** gardien des mondes/graines, opérateur de campagne, évaluateur scientifique indépendant, responsable du protocole  
**Statut :** MODE D'EMPLOI, **PAS** une autorisation de campagne ni une preuve de résultat. Par défaut : **NO-GO**.  
**Dépôt :** `josselin-orta-lab/individual-zero`  
**Branche d’intégration :** `main` (Stages 1 à 9, incluant le Stage 5 parallèle)  
**Point de départ logiciel intégré (exemple, non gel scientifique) :** `b304ebda7facf8ba285408e87090727dafc43bcb`  
**Fusion :** [PR #20](https://github.com/josselin-orta-lab/individual-zero/pull/20) fusionnée ; PR historiques #11 à #18 clôturées comme remplacées. Aucun feu vert scientifique.

> **À lire avant de commencer.** Ce document explique comment préparer, conduire, préserver et évaluer la campagne. Il ne fournit **ni** les paramètres expérimentaux calibrés **ni** les mondes/graines tenus secrets **ni** des seuils scientifiques approuvés. Ces éléments doivent être reçus ou décidés prospectivement sous contrôle indépendant. **Sans eux, il faut arrêter à NO-GO.** Ne jamais remplacer les données manquantes par les fixtures de tests du dépôt.

**English edition:** [Stage 9 independent held-out evaluation manual](stage9-independent-heldout-evaluation-manual.en.md).

### Sommaire

1. [Comprendre la mission et les responsabilités](#1-comprendre-la-mission-et-les-responsabilités)
2. [Les conditions préalables et les éléments à recevoir](#2-les-conditions-préalables-et-les-éléments-à-recevoir)
3. [Préparer la machine indépendante](#3-préparer-la-machine-indépendante)
4. [Préparer les manifestes gelés et les mondes](#4-préparer-les-manifestes-gelés-et-les-mondes)
5. [Préparer et vérifier le préenregistrement](#5-préparer-et-vérifier-le-préenregistrement)
6. [Sceller le protocole dans Git](#6-sceller-le-protocole-dans-git)
7. [Créer les index et les documents d'autorisation](#7-créer-les-index-et-les-documents-dautorisation)
8. [Contrôles préalables et décision GO / NO-GO](#8-contrôles-préalables-et-décision-go--no-go)
9. [Exécuter la campagne](#9-exécuter-la-campagne)
10. [Identifier et annoter les preuves](#10-identifier-et-annoter-les-preuves)
11. [Générer le rapport et le sceller](#11-générer-le-rapport-et-le-sceller)
12. [Effectuer l'audit indépendant final](#12-effectuer-laudit-indépendant-final)
13. [Interpréter les résultats et rendre le verdict](#13-interpréter-les-résultats-et-rendre-le-verdict)
14. [Gérer les anomalies sans perdre la valeur scientifique](#14-gérer-les-anomalies-sans-perdre-la-valeur-scientifique)
15. [Remettre les livrables et clore le mandat](#15-remettre-les-livrables-et-clore-le-mandat)
16. [Annexes : modèles et aide-mémoire](#16-annexes--modèles-et-aide-mémoire)

---

## 1. Comprendre la mission et les responsabilités

### 1.1. Le projet en trois phrases

**Individual Zero** est un logiciel expérimental simulant un individu artificiel dans un monde déterministe. Son **Stage 9** étudie la distinction entre corrélation et causalité, l'attribution des effets d'une action et l'usage de certaines connaissances causales par les mécanismes de sécurité et de simulation. L'objectif de votre mandat n'est pas de « faire réussir » l'agent, mais d'examiner s'il satisfait ou non les critères **fixés avant l'expérience** sur des mondes et graines distincts de ceux utilisés pendant le développement.

**Vocabulaire :**

| Terme | Signification concrète |
| --- | --- |
| *held-out* | Mondes, configurations et graines mis de côté, inconnus des développeurs avant l'exposition autorisée aux résultats. |
| *Monde* | Physique, configuration, générateur et événements externes constituant un environnement de vie simulé. |
| *Graine* (*seed*) | Entier pilotant le tirage reproductible des éléments générés (notamment disposition et identité des baies). |
| *Cellule* | Une combinaison **monde × graine**, exécutée et rejouée. |
| *Journal causal* | Suite chronologique d'événements canonisés et chaînés par empreintes cryptographiques. |
| *Memory clos* | Épisode autobiographique terminé et présent dans l'état sauvegardé de la mémoire de l'individu. |
| *Oracle / vérité terrain* | Information complète sur les causes et états du monde. Elle appartient **uniquement au banc** ; l'individu ne doit pas y accéder. |
| *Préenregistrement* | Protocole scientifique, métriques et décisions figés **avant** de voir les résultats réservés. |
| *Rejeu exact* | Seconde exécution produisant exactement les mêmes octets de journal et d'état causal que la première. |
| *Golden* | Référence scientifique acceptée après vérification complète. **Aucun Golden Stage 9 n'est établi par la présente procédure.** |
| `etablie` | Règle causale établie au sens du modèle, utilisable par le simulateur sous les conditions normatives. |
| `etabli_pour_securite` | Règle de sécurité permettant un veto, **sans** modifier les prédictions du simulateur ni artificiellement `R_a`. |
| `INV-25` | Invariant de séparation entre conséquence prédictive et règle de veto à examiner explicitement. |

### 1.2. Qui est responsable de quoi ?

| Fonction | Mission et preuve attendue | Interdiction essentielle |
| --- | --- | --- |
| **Responsable scientifique** | Approuve hypothèses, paramètres, plan, seuils, effectifs, exclusions, arrêt et identité des autres responsables ; signe **avant** les résultats. | Ajuster les règles après consultation des résultats. |
| **Gardien indépendant** | Choisit ou conserve les mondes, graines, distributions et vérités de contrôle ; conserve un historique des accès. | Exposer prématurément les secrets aux développeurs. |
| **Opérateur** | Installe le logiciel figé, exécute **toutes** les cellules, préserve les journaux et les preuves d'environnement. | Adapter le code ou supprimer des cellules sur la base des performances. |
| **Évaluateur indépendant** | Inspecte les originaux, les conditions causales, la chronologie, les métriques, les erreurs et `INV-25` ; signe son verdict. | Se contenter d'un `SUCCESS` CI ou d'un SHA-256 pour conclure à la validité scientifique. |

Une personne peut exercer plusieurs fonctions **seulement** si les conflits et les compensations de contrôle ont été examinés et acceptés indépendamment. Un agent d'IA ayant développé le logiciel **n'est pas** l'évaluateur indépendant.

### 1.3. Sources faisant autorité

- **Normative, prioritaire :** `docs/architecture/reference/en/mvp-specification-v1.2.1.md`, spécialement §§9.6, 13.2, 19.5, 20.3 Stage 9 et `INV-25`. Ne pas la modifier.
- **Registre de décision :** `docs/research/stage9-heldout-prelaunch-decision-record.md`.
- **Protocole de préenregistrement :** `docs/research/stage9-scientific-preregistration-template.md`.
- **Runbook d'origine :** `docs/research/stage9-independent-heldout-operator-runbook.md`.
- **Documentation du lanceur :** `docs/research/stage9-heldout-executor.md`.
- **Programme :** `src/lab/stage9_heldout_runner.py` (deux sous-commandes : `run` et `package`).

En cas de contradiction, la spécification **anglaise v1.2.1** prime ; arrêter et faire arbitrer par le responsable scientifique **avant** tout résultat.

---

## 2. Les conditions préalables et les éléments à recevoir

### 2.1. Avant d'accéder aux données réservées

Le responsable scientifique doit vous remettre les éléments suivants, accompagnés de la référence de leur approbation :

- [ ] Identité et acceptation signée du responsable, du gardien, de l'opérateur et de l'évaluateur ; déclaration des conflits d'intérêts.
- [ ] Code source exact identifié par un SHA Git **complet de 40 caractères**. Le commit candidat actuellement connu est `b304ebda7facf8ba285408e87090727dafc43bcb`. **Ce SHA n'est pas un gel scientifique signé par défaut. Le responsable peut désigner un autre commit après inspection ; dans ce cas, remplacer toutes les références à `FREEZE_SHA` avant l’enregistrement.**
- [ ] Paramètres complets **calibrés sur des mondes autorisés**, conformes au Stage 9, incluant paramètres P-xx, modèle d'équipement effectivement entraîné et justification des choix.
- [ ] Définition préalablement approuvée des mondes à causes connues (**contrôle positif**) et sans relation causale pertinente (**contrôle négatif**), avec leurs méthodes de génération et vérification.
- [ ] Plan d'échantillonnage, graines tenues secrètes, critères d'indépendance, longueur des vies, règle de fin, seuils, métriques, limites statistiques et conditions d'invalidation.
- [ ] Règles d'annotation (causes connues, « absence d'effet », attribution, hypothèses superstitieuses **naturellement acquises**, preuves provenant de Memory clos).
- [ ] Plan de comparaison `INV-25` et de vérification de la séparation oracle / individu.
- [ ] Moyen de conserver les fichiers et les signatures dans un espace **isolé**, avec horodatage indépendant vérifiable.

**Important :** le lanceur existant est un outil technique et n'est pas un plan expérimental. Les valeurs contenues dans `stage9_reference_fixture.py` sont des valeurs de **compatibilité logicielle**, **pas** une calibration scientifique autorisée. Si aucun modèle d'équipement et aucun registre de paramètres calibrés et approuvés n'est fourni : **NO-GO**.

### 2.2. Limites scientifiques qui nécessitent un contrôle humain

1. Le lanceur prend en charge l'équipement `exact_transition_table` figé. Il **n'entraîne pas** l'équipement et ne le reconfigure pas sur les données held-out. Il peut refuser des entrées inconnues au lieu d'inventer des prédictions.
2. Le générateur utilise la graine pour une géométrie et des effets des baies déterministes. Le planning des événements de scénario est défini **par monde**, pas fabriqué automatiquement pour chaque graine.
3. Les événements externes disponibles comprennent `set_body`, `place_resource`, `place_creature`, `remove_creature`, `set_danger_zone` et `set_lethal_zone`. **Il n'existe pas un générateur universel de récompenses aléatoires indépendantes par graine.** Si le contrôle négatif exige des récompenses stochastiques inaccessibles avec ces mécanismes, il faut corriger et revalider le système **avant le gel**, sinon **NO-GO**. Un monde appelé « null » n'est pas automatiquement un véritable contrôle causal nul.
4. Le fichier `bench-only-world-truth.json` enregistre notamment l'état physique initial et final et la configuration effective, **pas une vérité causale détaillée et certifiée à chaque pas**. Les classifications doivent être justifiées par un examinateur indépendant et des preuves physiques supplémentaires le cas échéant.
5. Une exécution sans observation admissible ou sans fausse hypothèse naturellement apparue peut être **non évaluable**, même si le programme s'exécute parfaitement.

---

## 3. Préparer la machine indépendante

Les commandes ci-dessous supposent **Linux ou macOS avec Bash, Git et Python 3.11 ou 3.12**. La branche Stage 9 avant intégration a réussi **652 tests** sur Python 3.11 et 3.12 avec ses diagnostics historiques ; l’arbre intégré, comprenant également le Stage 5, a réussi **678 tests** sur Python 3.12. La validation exhaustive de l’arbre intégré sous les deux versions n’est pas attestée. Un Windows natif non testé demanderait une procédure d'environnement séparée.

### 3.1. Créer un espace isolé

Sur un ordinateur ou un compte indépendant des développeurs, avec chiffrement du stockage et accès restreint, ouvrir un terminal :

```bash
umask 077
git --version
python3 --version
```

**Attendu :** Git répond avec sa version ; Python répond `3.11.x` ou `3.12.x`. Sinon : installer la version prise en charge **avant** de poursuivre.

Avec accès GitHub approprié :

```bash
git clone --no-single-branch \
  git@github.com:josselin-orta-lab/individual-zero.git \
  individual-zero-stage9-private
cd individual-zero-stage9-private

# Le responsable scientifique doit approuver explicitement CE commit ou un autre commit logiciel final.
export FREEZE_SHA="b304ebda7facf8ba285408e87090727dafc43bcb"
git cat-file -t "$FREEZE_SHA"
git switch --detach "$FREEZE_SHA"
git switch -c stage9-independent-private

# Mesure anti-fuite : aucun push possible par mégarde vers le dépôt partagé.
git remote remove origin

git rev-parse HEAD
git rev-parse --is-shallow-repository
git remote -v
```

**Attendu :**

- `git cat-file -t` renvoie `commit` ;
- `git rev-parse HEAD` renvoie **exactement** la valeur de `FREEZE_SHA` ;
- `git rev-parse --is-shallow-repository` renvoie **`false`** ;
- `git remote -v` n'affiche **aucune** destination.

Si le gardien n'a pas accès au dépôt privé, le responsable peut livrer un **Git bundle complet et authentifié**, contenant le commit demandé et son historique ; il faudra vérifier son origine, puis le cloner **hors des systèmes de développement**. Ne pas se contenter d'une archive ZIP : les contrôles exigent la généalogie Git.

> **Confidentialité.** Le fichier de préenregistrement contient les **vraies graines numériques en clair**. Ne jamais pousser cette branche, déposer son contenu sur `main` ou dans une PR de développement, exposer ces graines à des assistants de code ni exécuter cette campagne via une GitHub Action partageant les journaux avec les développeurs. La suppression de `origin` sert précisément à réduire le risque de publication accidentelle.

### 3.2. Installer l'environnement

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
python --version
```

**Attendu :** installation sans erreur, Python 3.11 ou 3.12. Consigner séparément version de Python, système, dépendances, environnement, date/heure, personne opératrice et sortie de `python -m pip freeze` :

```bash
mkdir -p research/stage9 results/stage9/raw-manifests/frozen \
  results/stage9/raw-manifests/worlds results/stage9/receipts
python -m pip freeze > results/stage9/receipts/python-dependencies.txt
python -m pip --version > results/stage9/receipts/pip-version.txt
python --version > results/stage9/receipts/python-version.txt 2>&1
```

N'exécuter **aucune** commande du lanceur `run` à ce stade.

### 3.3. Validation locale **sans données réservées**

```bash
python -m unittest tests.test_stage9_heldout_runner \
  tests.test_stage9_heldout_operator_integration -v

# Facultatif, plus exhaustif :
python -m unittest discover -s tests -q
```

**Attendu :** dernière ligne `OK` et aucun `FAILED`/`ERROR`. Le nombre de tests peut varier si le code approuvé n'est pas le commit candidat de ce manuel ; ne pas remplacer une défaillance par un changement de branche après gel. Ces tests sont **synthétiques**, ne prouvent rien sur la future campagne.

---

## 4. Préparer les manifestes gelés et les mondes

### 4.1. Inventaire des fichiers à fournir **avant le préenregistrement**

Le gardien conserve les fichiers **originaux** dans :

```text
results/stage9/raw-manifests/
├── frozen/
│   ├── generator.json          # paramètres du générateur de mondes
│   ├── parameters.json         # configuration complète Stage9 + sécurité innée
│   ├── equipment.json          # modèle E gelé et sa table de transitions
│   └── ontology.json           # référence/version du registre d'ontologie
└── worlds/
    ├── calibration-1.json     # exemple de nom : monde de calibration
    ├── positive-1.json        # exemple de nom : cause connue
    └── null-1.json            # exemple de nom : contrôle négatif
```

Les noms ci-dessus sont **illustratifs**. Le nombre et les identités exacts doivent venir du protocole scientifique. Un monde positif et un monde négatif ne suffisent pas nécessairement à obtenir une puissance statistique acceptable.

| Fichier | Informations attendues | Vérification technique | Qui le valide scientifiquement ? |
| --- | --- | --- | --- |
| `frozen/generator.json` | Version, nombres de sources d'eau, cases de ressources/dangers/créatures, gains et toxicité ; graine utilisée par cellule. | Schéma `stage9-heldout-world-generator-v1` ; `WorldGenerationConfig.validate()` ; SHA-256 des octets. | Responsable + gardien. |
| `frozen/parameters.json` | Tout `Stage9Config`, `Stage8Config` et niveaux antérieurs, P-xx, `SafetyProtocolConfig` en mode `campaign`, seuil de protection, règles innées. | Schéma `stage9-heldout-parameters-v1` ; décodage strict de chaque dataclass. | Responsable scientifique après calibration externe. |
| `frozen/equipment.json` | `EquipmentArtifact`, historique de corpus, version, `model_kind=exact_transition_table`, enregistrements `ExactTransitionRecord`. | Schéma `stage9-heldout-equipment-v1`, index de clés exact, empreintes et validation d'équipement. | Responsable scientifique, traçabilité de l'entraînement. |
| `frozen/ontology.json` | `protocol_version`, identité du registre versionné, référence des définitions utilisées. | L'outil vérifie seulement la version de protocole et les **octets**. | Évaluateur : comparer aux définitions réellement présentes dans le code figé. |
| `worlds/*.json` | Physique du monde, paramètres corporels initiaux, version, scénario externe complet, identité du monde. | Schéma `stage9-heldout-physical-world-v1`, `WorldPhysicsConfig.validate()` et scénario ; SHA-256 des octets. | Gardien + évaluateur : causes et contrôle nul **réellement distincts**. |

### 4.2. `generator.json` : modèle éditable

**EXEMPLE DE STRUCTURE, NON PRÊT POUR UNE CAMPAGNE.** Remplacer chaque `null` par la valeur **calibrée et approuvée**, ne pas inventer de chiffre.

```json
{
  "protocol_version": "stage9-heldout-world-generator-v1",
  "generation": {
    "version": "VERSION_APPROUVEE_DU_GENERATEUR",
    "water_source_count": null,
    "berry_a_cells": null,
    "berry_b_cells": null,
    "wood_cells": null,
    "stone_cells": null,
    "creature_count": null,
    "danger_zone_count": null,
    "quantity_per_resource_cell": null,
    "nutritious_food_gain": null,
    "toxic_food_gain": null,
    "toxic_integrity_delta": null
  }
}
```

Les champs `*_count` et `quantity_per_resource_cell` sont des **entiers** ; les gains et variations corporelles sont des **nombres finis**. `toxic_integrity_delta` doit être strictement **négatif**. La physique normative impose une grille **32 × 32** et un jour de **300 pas**, dont **100 de nuit**.

### 4.3. `parameters.json` et `equipment.json` : ne pas les fabriquer à la main

Le responsable doit transmettre les artefacts **réellement calibrés et gelés**. Le lanceur fournit une fonction d'export pour un runtime Stage 9 déjà préparé :

```python
from lab.stage9_heldout_runner import export_frozen_stage9_assets

# `runtime_calibre` doit préexister et provenir du processus de
# calibration approuvé. NE PAS construire ce runtime avec la fixture
# stage9_reference_fixture pour prétendre à une validation scientifique.
parameters_document, equipment_document = export_frozen_stage9_assets(
    runtime_calibre
)
```

Ce code est **un exemple d'API**, pas une commande Bash directement exécutable : l'objet `runtime_calibre` doit être fourni. Si cet objet ou les JSON correspondants n'existent pas : **NO-GO**.

`parameters.json` doit avoir exactement ces champs racines :

```json
{
  "protocol_version": "stage9-heldout-parameters-v1",
  "stage9_config": {},
  "safety_config": {},
  "protected_integrity_threshold": null,
  "innate_safety_facts": {}
}
```

La forme ci-dessus est volontairement **incomplète**. `stage9_config` contient notamment les sous-configurations `stage8`, `causal` (seuils P-35/P-36 et règles), `agency` (comparateur P-47), puis toutes les sous-configurations héritées des stages antérieurs, avec leurs **versions exactes**. `safety_config.mode` doit valoir `"campaign"`. `innate_safety_facts` possède les listes de positions/ressources connues comme sûres ou dangereuses. Le champ `protected_integrity_threshold` est un nombre strictement compris entre 0 et 100. L'exporteur existant garantit la structure **seulement si les données sources sont déjà valides**.

`equipment.json` doit avoir exactement les champs racines :

```json
{
  "protocol_version": "stage9-heldout-equipment-v1",
  "artifact": {},
  "records": []
}
```

Ici encore, les objets vides indiquent les **emplacements** à recevoir du responsable. L'`artifact` décrit l'équipement entraîné (`version`, `corpus_version`, `corpus_sha256`, `model_kind`, `model_payload`, `training_metadata`) et `records` contient les exemples de transitions gelés (`input_sha256`, `next_state`, `effects`, `terminal`). Ils doivent être cohérents avec l'empreinte du modèle entraîné. Ne pas « compléter » les transitions manquantes à partir des mondes held-out.

La structure racine minimale de `ontology.json` est :

```json
{
  "protocol_version": "stage9-heldout-ontology-v1",
  "version": "VERSION_REELLE_DU_REGISTRE_A_COMPLETER",
  "artifact_ref": "REFERENCE_DE_PROVENANCE_A_COMPLETER"
}
```

**Attention :** la vérification du lanceur ne compare pas automatiquement la sémantique de cette ontologie à celle du runtime ; l'évaluateur doit le faire et signer l'examen.

### 4.4. Fichiers `worlds/*.json`

Chaque monde possède cette **structure racine exacte** :

```json
{
  "protocol_version": "stage9-heldout-physical-world-v1",
  "world_id": "IDENTIFIANT_REEL_DU_MONDE",
  "physics": {},
  "scenario": {
    "id": "IDENTIFIANT_REEL_DU_SCENARIO",
    "version": "VERSION_REELLE",
    "events": []
  }
}
```

Le champ `physics` vide n'est **pas valide** en exécution. Il doit contenir l'objet produit par `WorldPhysicsConfig.as_dict()`, complet avec :

- `version` (chaîne), `width=32`, `height=32`, `day_steps=300`, `night_steps=100`, `night_start_step` (entier dans le jour) ;
- `initial_body` (`energy`, `food`, `water`, `integrity`, chacun entre 0 et 100), `initial_position` (`x`,`y`, à l'intérieur des frontières) ;
- `food_decay_per_step`, `water_decay_per_step`, `sleep_energy_gain`, `rest_integrity_gain`, `drink_water_gain`, `creature_damage`, `danger_zone_damage` (nombres non négatifs, selon leurs contraintes) ;
- `action_energy_costs` (coût de **chaque** primitive), `berry_effects` (baies `berry_a` et `berry_b`, chacune avec `food_gain` et `integrity_delta`), `tool_recipe` (`wood_required`, `stone_required`, `collection_gain`), `shelter_stones_required=4`.

Le générateur fixe ensuite la disposition et les effets des baies à partir de la graine. La relation entre configuration physique, génération et scénario doit être **prédéfinie et auditée** ; ne pas changer la physique d'un monde après avoir vu son score.

Exemple de **syntaxe d'un événement** (illustratif, pas de validation scientifique) :

```json
{
  "t_monde": 25,
  "sequence": 0,
  "operation": "set_body",
  "payload": {"water": 75.0}
}
```

Chaque événement est un input externe **journalisé**, déclenché à `t_monde` indiqué (de 1 à `steps_per_run`), avec un couple `(t_monde, sequence)` unique. Des répétitions artificielles, des valeurs non physiques ou des labels d'oracle injectés à l'individu invalideraient l'essai.

### 4.5. Choisir les graines sous la responsabilité du gardien

Le nombre de graines est défini **dans le plan approuvé**, jamais par un chiffre arbitraire de ce manuel. Le gardien peut utiliser une source aléatoire cryptographique pour préparer une liste privée et vérifier qu'elle n'intersecte pas les graines de calibration :

```bash
python - <<'PY'
import json, secrets
from pathlib import Path

nombre = int(input('Nombre de graines held-out déjà approuvé : '))
calibration = json.loads(input('Liste JSON des graines de calibration : '))
assert nombre >= 2 and isinstance(calibration, list)
assert all(type(x) is int and x >= 0 for x in calibration)
selection = set()
while len(selection) < nombre:
    graine = secrets.randbits(64)
    if graine not in calibration:
        selection.add(graine)
chemin = Path('results/stage9/private-seed-selection.json')
with chemin.open('x', encoding='utf-8') as fichier:
    json.dump({'calibration_seeds': calibration,
               'holdout_seeds': sorted(selection)}, fichier, indent=2)
    fichier.write('\n')
chemin.chmod(0o600)
print('Sélection privée écrite ; ne pas afficher les graines.')
PY
```

**Attendu :** création d'un fichier privé inédit sans divulguer ses nombres dans le terminal. Le gardien doit vérifier l'indépendance réelle du protocole d'échantillonnage et reporter ses **vraies** listes dans `registration.json`, ensuite conservé dans le Git **isolé**. Ce tirage d'entiers ne démontre **pas** à lui seul que les mondes, observations ou essais statistiques sont indépendants. Ne jamais committer `private-seed-selection.json` dans le dépôt public/de développement.

### 4.6. Vérifier les fichiers et produire leurs empreintes

Quand les vrais JSON approuvés sont présents, les contrôles suivants permettent de détecter les objets mal formés **avant** de sceller le protocole :

```bash
python - <<'PY'
from pathlib import Path
from lab.stage9_heldout_runner import (
    _json_file, _frozen_parameters, _frozen_equipment, _typed,
    GENERATOR_VERSION,
)
from lab.world_generation import WorldGenerationConfig
root = Path('results/stage9/raw-manifests/frozen')
params = _frozen_parameters(_json_file(root / 'parameters.json'))
equipment = _frozen_equipment(_json_file(root / 'equipment.json'))
generator = _json_file(root / 'generator.json')
assert generator['protocol_version'] == GENERATOR_VERSION
assert set(generator) == {'protocol_version', 'generation'}
_typed(WorldGenerationConfig, generator['generation'])
assert _json_file(root / 'ontology.json')['protocol_version'] == 'stage9-heldout-ontology-v1'
print('MANIFESTES_GELES_DECODABLES_URGENCE_DE_VALIDATION_SCIENTIFIQUE')
PY

sha256sum results/stage9/raw-manifests/frozen/*.json
sha256sum results/stage9/raw-manifests/worlds/*.json
sha256sum docs/architecture/reference/en/mvp-specification-v1.2.1.md
```

**Attendu :** un marqueur textuel de décodage suivi d'une **empreinte de 64 caractères hexadécimaux** pour chaque fichier. Sur macOS, si `sha256sum` n'existe pas, employer `shasum -a 256` avec les mêmes chemins. **Un SHA correct indique une identité d'octets, pas la pertinence scientifique d'un monde.** Conserver ces empreintes dans le dossier privé.

---

## 5. Préparer et vérifier le préenregistrement

### 5.1. Le seul fichier de protocole lu par les outils

Créer dans le **checkout Git isolé** : `research/stage9/registration.json`.

Le format exigé est `stage9-preregistration-schema-v2`, avec **exactement** les champs suivants. Le JSON ci-dessous est un **GABARIT INCOMPLET**, volontairement rejeté tant que les valeurs réelles et les preuves de calibration ne l'ont pas remplacé :

```json
{
  "protocol_version": "stage9-preregistration-schema-v2",
  "registration_id": "IDENTIFIANT_EXPERIENCE_A_REMPLACER",
  "author": "RESPONSABLE_SCIENTIFIQUE_A_REMPLACER",
  "normative_specification": "docs/architecture/reference/en/mvp-specification-v1.2.1.md",
  "normative_specification_sha256": "SHA256_REEL_64_HEX_A_REMPLACER",
  "frozen_implementation_commit": "b304ebda7facf8ba285408e87090727dafc43bcb",
  "world_generator_version": "VERSION_GENERATEUR_A_REMPLACER",
  "world_generator_sha256": "SHA256_REEL_64_HEX_A_REMPLACER",
  "equipment_sha256": "SHA256_REEL_64_HEX_A_REMPLACER",
  "parameter_registry_sha256": "SHA256_REEL_64_HEX_A_REMPLACER",
  "ontology_sha256": "SHA256_REEL_64_HEX_A_REMPLACER",
  "calibration_world_sha256": {
    "calibration:1": "SHA256_REEL_64_HEX_A_REMPLACER"
  },
  "holdout_world_sha256": {
    "holdout:positive": "SHA256_REEL_64_HEX_A_REMPLACER",
    "holdout:null": "SHA256_REEL_64_HEX_A_REMPLACER"
  },
  "calibration_world_ids": ["calibration:1"],
  "holdout_world_ids": ["holdout:positive", "holdout:null"],
  "positive_world_ids": ["holdout:positive"],
  "negative_world_ids": ["holdout:null"],
  "calibration_seeds": [null],
  "holdout_seeds": [null, null],
  "steps_per_run": null,
  "minimum_naturally_acquired_candidates": null,
  "maximum_superstitious_rule_rate": null,
  "minimum_known_cause_accuracy": null,
  "confidence_method": "wilson_95",
  "candidate_definition": "DEFINITION_PRECISE_A_REMPLACER",
  "ground_truth_definition": "REGLES_CAUSALES_ET_CONTROLES_A_REMPLACER",
  "independent_episode_definition": "DEFINITION_INDEPENDANCE_A_REMPLACER",
  "exclusion_rule": "EXCLUSIONS_PREDEFINIES_A_REMPLACER",
  "stop_rule": "REGLE_ARRET_PREDEFINIE_A_REMPLACER",
  "replay_rule": "REJEU_OCTET_POUR_OCTET_A_APPROUVER"
}
```

**Ne jamais exécuter la campagne avec les valeurs de ce modèle.** Modifier en local, puis valider le JSON. Les exemples de mondes ne disent rien de la conception réelle ni d'une taille d'échantillon appropriée.

### 5.2. Comment renseigner chaque famille de champs

| Champs | Type et ce qu'il faut réellement saisir |
| --- | --- |
| `registration_id`, `author` | Chaînes non vides, identité réelle et référence du protocole signé. L'horodatage signé est conservé **séparément** : le schéma JSON n'a pas de champ timestamp. |
| `normative_specification` | Chemin exact **anglais v1.2.1**, sans modification. |
| `normative_specification_sha256` | SHA-256 des octets du document normatif présent au gel. |
| `frozen_implementation_commit` | SHA du code **approuvé** et vérifié, complet (40 hex). Le SHA du modèle ci-dessus n'est qu'une candidature. |
| `world_generator_version` | Version exacte du générateur fournie dans `generator.json`. |
| `world_generator_sha256`, `equipment_sha256`, `parameter_registry_sha256`, `ontology_sha256` | Empreintes SHA-256 des **octets d'origine** des quatre manifestes correspondants. |
| `calibration_world_ids`, `holdout_world_ids` | Tableaux d'identifiants uniques de monde. Les ensembles doivent être disjoints ; au moins **1** monde de calibration et **2** mondes held-out (minimum du validateur). |
| `calibration_world_sha256`, `holdout_world_sha256` | Dictionnaires `ID -> SHA-256 du fichier physique complet`. Chaque ID doit avoir une empreinte ; aucune duplication de fichier physique entre mondes/calibration. |
| `positive_world_ids`, `negative_world_ids` | Partitions disjointes couvrant **tous** les `holdout_world_ids`, avec au moins un monde de chaque catégorie. Classification décidée à l'avance par le banc. |
| `calibration_seeds`, `holdout_seeds` | Tableaux d'entiers **non négatifs**, tous distincts dans chaque liste et sans recouvrement entre elles. Au moins **1** graine calibration, **2** held-out (minimum logiciel, pas un calcul de puissance). Les graines held-out sont **secrètes**. |
| `steps_per_run` | Entier strictement positif, identique pour toutes les cellules, décidé prospectivement. Une vie interrompue doit être conservée comme échec/blocage selon la règle approuvée. |
| `minimum_naturally_acquired_candidates` | Entier ≥ 1, effectif minimal de fausses règles réellement apparues sans injection, indispensable au dénominateur. |
| `maximum_superstitious_rule_rate` | Fraction numérique entre 0 et 1 : plafond fixé **avant** l'expérience. |
| `minimum_known_cause_accuracy` | Fraction numérique entre 0 et 1 : performance minimale approuvée. |
| `confidence_method` | Valeur exacte **`wilson_95`** ; aucune autre méthode n'est implémentée pour ce lanceur. |
| `candidate_definition` | Critères précis d'une *règle fausse naturellement acquise* (unité = contingence canonique distincte par cellule, non répétition de la même règle). |
| `ground_truth_definition` | Processus indépendant de catégorisation `self` / `world` / `none`, contrôles positifs et nuls, résolution des causes multiples. |
| `independent_episode_definition` | Règles attestant la provenance des observations, les contextes contrôlés et les épisodes Memory clos. Ne pas assimiler un identifiant d'épisode à l'indépendance statistique. |
| `exclusion_rule`, `stop_rule`, `replay_rule` | Textes détaillant **avant l'exécution** la gestion des échecs, blocs de sécurité, rejets de provenance, arrêt anticipé, complétude de la matrice, comparaison exacte des octets et publication des cas défavorables. |

La longueur totale attendue est **nombre de mondes held-out × nombre de graines held-out**. Ce produit est fixé par les listes, le lanceur **n'accepte pas** d'échantillon favorable choisi après coup.

### 5.3. Contrôle du gabarit rempli

```bash
python -m json.tool research/stage9/registration.json >/dev/null
python -m lab.stage9_scientific_preregistration \
  --manifest research/stage9/registration.json \
  > results/stage9/receipts/registration-preflight.json
cat results/stage9/receipts/registration-preflight.json
```

**Attendu si tout est bien rempli :**

```json
{
  "registration_status": "draft_requires_independent_git_seal",
  "registration_digest": "UNE_EMPREINTE_CANONIQUE_DE_64_CARACTERES",
  "launch_authorized_by_preflight": false,
  "independent_heldout_custody_attested_by_preflight": false,
  "independent_evaluator_approved_by_preflight": false,
  "scientific_verdict": null,
  "golden_stage9_frozen": false
}
```

L'objet réel contient aussi une liste `outstanding`. Ce bloc ci-dessus est un **extrait explicatif**, pas une reproduction littérale de toute la sortie.

**Signification :** le format est cohérent et possède une empreinte logique, **mais le protocole n'est ni scellé, ni approuvé, ni exécuté**. L'absence du champ requis, d'une empreinte valide, d'un ensemble disjoint, d'un seuil ou d'une graine entière provoque une exception / sortie non nulle ; **NE PAS continuer**.

Le `registration_digest` est calculé à partir de la **représentation JSON causale canonique**, pas de la sortie de `sha256sum registration.json`. Ces deux empreintes peuvent être différentes : ne pas les confondre.

---

## 6. Sceller le protocole dans Git

### 6.1. Signature et preuve d'antériorité

Avant toute exécution réservée :

1. Faire signer au responsable scientifique le contenu complet du protocole, les valeurs des paramètres, les seuils, les tailles d'échantillon, les règles d'exclusion et d'arrêt.
2. Faire attester par le gardien l'indépendance des mondes/graines, la confidentialité et la possession des originaux.
3. Déposer **séparément** une preuve d'antériorité indépendante du temps (par exemple attestation signée et datée par un tiers de confiance), en évitant de révéler les graines et vérités cachées.
4. S'assurer que le commit du protocole descend du commit source figé **sans modification de `src/`, `pyproject.toml` et de la spécification anglaise**.

L'heure d'un commit Git **ne prouve pas seule** qu'un protocole a été approuvé avant de voir les données.

### 6.2. Commit du protocole **dans l'espace isolé uniquement**

```bash
git status --short
git diff -- src pyproject.toml \
  docs/architecture/reference/en/mvp-specification-v1.2.1.md

# Doit être exécuté UNIQUEMENT APRÈS signature et vérification des secrets.
git add research/stage9/registration.json
git commit -m "Prospective Stage 9 heldout registration"
export REGISTRATION_COMMIT="$(git rev-parse HEAD)"

printf 'FREEZE_SHA=%s\nREGISTRATION_COMMIT=%s\n' \
  "$FREEZE_SHA" "$REGISTRATION_COMMIT"
git merge-base --is-ancestor "$FREEZE_SHA" "$REGISTRATION_COMMIT"
```

**Attendu :** `git diff` n'affiche **aucune** modification des chemins figés ; le nouveau commit Git est distinct de `FREEZE_SHA` ; `git merge-base --is-ancestor` renvoie un code de sortie **0**. Le dépôt isolé doit **rester sans remote**.

**Attention :** dès ce commit, les graines numériques réelles sont conservées **en clair dans l'historique Git local**, même si elles sont ensuite effacées du fichier. La confidentialité dépend de la garde de **tout l'historique**.

---

## 7. Créer les index et les documents d'autorisation

### 7.1. `results/stage9/physical-manifest-index.json`

Ce fichier est un **index de chemins**. Il ne remplace aucun manifeste et ne modifie pas le protocole. Exemple de structure à adapter aux véritables IDs :

```json
{
  "protocol_version": "stage9-registered-physical-manifest-index-v1",
  "registration_digest": "EMPREINTE_CANONIQUE_REELLE_64_HEX",
  "frozen_manifests": {
    "world_generator": "frozen/generator.json",
    "equipment": "frozen/equipment.json",
    "parameter_registry": "frozen/parameters.json",
    "ontology": "frozen/ontology.json"
  },
  "calibration_worlds": {
    "calibration:1": "worlds/calibration-1.json"
  },
  "holdout_worlds": {
    "holdout:positive": "worlds/positive-1.json",
    "holdout:null": "worlds/null-1.json"
  }
}
```

Remplacer `registration_digest` par la vraie valeur issue de `registration-preflight.json`. Tous les chemins sont **relatifs** à `results/stage9/raw-manifests`. Ils doivent exister, être distincts, ne pas contenir `..`, ne pas être des liens symboliques ou des liens physiques réutilisés. Les identifiants doivent correspondre **exactement** au protocole scellé.

### 7.2. `results/stage9/private-release-record.json`

Après le commit de préenregistrement, **et seulement si le registre scientifique est réellement approuvé**, préparer :

```json
{
  "protocol_version": "stage9-heldout-operator-release-record-v1",
  "registration_digest": "EMPREINTE_CANONIQUE_REELLE_64_HEX",
  "frozen_implementation_commit": "b304ebda7facf8ba285408e87090727dafc43bcb",
  "registration_commit": "SHA_COMPLET_40_HEX_DU_COMMIT_D_ENREGISTREMENT",
  "authorization": "GO",
  "research_owner": "NOM_REEL_ET_REFERENCE",
  "custodian": "NOM_REEL_ET_REFERENCE",
  "operator": "NOM_REEL_ET_REFERENCE",
  "independent_evaluator": "NOM_REEL_ET_REFERENCE",
  "approval_evidence_ref": "CHEMIN_PRIVE_VERIFIABLE_DES_SIGNATURES",
  "independent_timestamp_ref": "CHEMIN_PRIVE_VERIFIABLE_DE_L_HORODATAGE"
}
```

Les **11 clés** ci-dessus sont obligatoires et aucune clé supplémentaire n'est acceptée. Les valeurs d'identité et références doivent être **réelles, non vides, traçables**. Le champ `authorization` ne peut être `GO` qu'**après** la décision humaine signée. Ne pas l'écrire pour « débloquer » le programme ! Le lanceur **ne vérifie pas cryptographiquement** les signatures ou les personnes déclarées ; cette vérification est votre responsabilité.

### 7.3. Registre scientifique à remplir par les humains

Dans une **copie datée et signée** de `docs/research/stage9-heldout-prelaunch-decision-record.md`, renseigner les sections A à D : nominations, conflits, garde des données, gel du code, seuils approuvés, preuve d'antériorité, signatures, date/heure et décision réelle. **Ne pas modifier la version documentaire source pour prétendre qu'une approbation existe.** Conserver le registre signé hors de tout dépôt accessible aux développeurs.

---

## 8. Contrôles préalables et décision GO / NO-GO

### 8.1. Contrôle des manifestes originaux

```bash
python -m lab.stage9_registered_manifest_custody \
  --registration research/stage9/registration.json \
  --index results/stage9/physical-manifest-index.json \
  --artifact-root results/stage9/raw-manifests \
  > results/stage9/receipts/manifest-custody.json
cat results/stage9/receipts/manifest-custody.json
```

**Attendu :**

`"manifest_custody_status": "registered_manifest_bytes_match_requires_independent_review"`

Et notamment : `frozen_manifests_checked` = **4** ; `calibration_worlds_checked` et `holdout_worlds_checked` égaux au protocole ; `registration_digest` égal à celui du préenregistrement ; `scientific_verdict: null` ; `golden_stage9_frozen: false`.

**Signification :** les fichiers existent et leurs **octets** correspondent aux empreintes enregistrées. Ce résultat n'atteste **pas** l'indépendance des mondes ni leurs mécanismes de causalité.

### 8.2. Contrôle du code figé dans **ce checkout**

```bash
python -m lab.stage9_frozen_worktree \
  --repo . \
  --frozen-commit "$FREEZE_SHA" \
  > results/stage9/receipts/frozen-checkout.json
cat results/stage9/receipts/frozen-checkout.json
```

**Attendu :**

`"worktree_status": "frozen_tracked_code_matches_local_checkout"`

Et : `frozen_implementation_commit` égal au SHA approuvé ; `git_head` égal au commit d'enregistrement ; empreintes Git `source_tree_sha`, `pyproject_blob_sha`, `normative_specification_blob_sha` ; `scientific_verdict: null`.

**Signification :** le code **suivi par Git** sur disque correspond à la version figée, sous les hypothèses du contrôle. Les dépendances installées, le cache Python, le matériel, le processus réellement exécuté et la garde indépendante demandent **des témoins supplémentaires**.

### 8.3. Décision humaine finale

**NO-GO obligatoire** si l'un des points suivants manque : auteur et évaluateur identifiés, garde indépendante, mondes positifs/négatifs crédibles, échantillonnage prospectif, équipement calibré, paramètres approuvés, seuils et exclusions écrits, Git et octets concordants, signatures et horodatage authentifiés, séparation oracle/agent, ou mécanisme de contrôle négatif physiquement réalisable.

Le GO doit être **signé et antérieur** à toute exécution réservée. Le succès des deux commandes précédentes n'accorde **aucun** GO automatique.

---

## 9. Exécuter la campagne

### 9.1. Dernier contrôle

Depuis le répertoire racine du checkout isolé :

```bash
# Vérifier que le dépôt n'a pas de destination de publication.
git remote -v

# Le lanceur exige EXACTEMENT le commit de préenregistrement comme HEAD.
test "$(git rev-parse HEAD)" = "$REGISTRATION_COMMIT"

# La destination des sorties brutes doit encore être inexistante.
test ! -e results/stage9/raw
```

**Attendu :** aucune sortie d'erreur ; remote vide ; `HEAD` exactement au commit d'enregistrement. **Ne pas lancer** si `results/stage9/raw` existe déjà : il peut contenir un échec à préserver ou des preuves antérieures.

### 9.2. Lancer une fois, après GO humain

```bash
# IMPORTANT : action irréversible du point de vue de l'exposition held-out.
python -m lab.stage9_heldout_runner run \
  --repo . \
  --registration research/stage9/registration.json \
  --registration-commit "$REGISTRATION_COMMIT" \
  --manifest-index results/stage9/physical-manifest-index.json \
  --manifest-root results/stage9/raw-manifests \
  --external-go-record results/stage9/private-release-record.json \
  --output-root results/stage9/raw \
  > results/stage9/receipts/operator-run-receipt.json

cat results/stage9/receipts/operator-run-receipt.json
```

**Attendu si toutes les cellules sont exécutées et rejouées :** sortie semblable à l'extrait suivant (les valeurs ne sont **pas** des résultats réels) :

```json
{
  "status": "operator_execution_archived_requires_external_annotation",
  "run_count": 4,
  "registration_digest": "EMPREINTE_REELLE_64_HEX",
  "external_approval_authenticated": false,
  "independent_execution_attested": false,
  "scientific_verdict": null,
  "golden_stage9_frozen": false
}
```

`run_count=4` signifie **uniquement** « quatre cellules traitées » **si** le protocole avait 2 mondes et 2 graines. Pour votre vraie campagne, vérifier que `run_count` = `len(holdout_world_ids) × len(holdout_seeds)`.

**Interprétation :** la simulation et son rejeu ont été sauvegardés. Le programme n'a **ni authentifié des signatures humaines ni mesuré la causalité ni attribué PASS**.

Si une cellule n'atteint pas les `steps_per_run` pas **appliqués** (ex. `safety_block`), le lanceur lève une erreur. **Préserver** le dossier brut partiellement créé et le journal d'erreur, consigner quelle cellule a échoué, puis appliquer `stop_rule` et `exclusion_rule` du protocole. Ne pas supprimer/rejouer sélectivement les cellules ou adapter les paramètres après consultation.

### 9.3. Fichiers produits automatiquement

```text
results/stage9/raw/
├── operator-run-index.json
├── cell-000-000/
│   ├── journal.jsonl
│   ├── replay-journal.jsonl
│   ├── causal-state.json
│   ├── replay-causal-state.json
│   └── bench-only-world-truth.json
├── cell-000-001/
│   └── ...
└── ...
```

| Fichier | À quoi il sert | À quoi s'attendre |
| --- | --- | --- |
| `operator-run-index.json` | Inventaire de toutes les cellules, chemins des originaux/rejeux, SHA-256, SHA du gel, empreinte du protocole et précontrôles. | `protocol_version = stage9-heldout-operator-run-index-v1`, `runs` de longueur exactement attendue, `scientific_verdict=null`. |
| `journal.jsonl` | Journal causal primaire en octets canonisés. | Événements `command_experienced`, `world_transition_experienced`, `auto_segment_commit` quand applicables ; aucun saut ou remplacement des événements. |
| `replay-journal.jsonl` | Journal réellement régénéré par une **seconde** exécution. | Octets **strictement égaux** au journal primaire. |
| `causal-state.json` | État final complet des propriétaires causaux, dont `memory` et `causal_model`. | JSON causal canonique. |
| `replay-causal-state.json` | État réellement régénéré au rejeu. | Octets **strictement égaux** à `causal-state.json`. |
| `bench-only-world-truth.json` | Informations de vérité du monde initial et final, disposition effectivement générée, toxicité réelle des baies, scénario et graine. | **Confidentiel** ; jamais transmis à l'individu. Ne suffit pas à lui seul à prouver les causes à chaque pas. |

**Sécurité des originaux :** conserver une copie indépendante en lecture seule ou un stockage à conservation contrôlée, avec empreintes, rôle d'accès, identifiant d'opérateur et horodatage externe. Ne pas donner la sortie bench-only à l'équipe de développement avant le moment prévu dans le protocole.

---

## 10. Identifier et annoter les preuves

L'opérateur remet les journaux et états **originaux** au banc indépendant. Le banc établit quelles observations reflètent une cause réelle, quelles attributions l'individu a émises, quels témoins n'ont pas d'effet, et quelles **fausses** contingences sont apparues naturellement dans les mondes nuls.

### 10.1. Comment retrouver les événements dans les originaux

**Uniquement sur la machine isolée, après exécution et avec les autorisations appropriées** :

```bash
python - <<'PY'
from pathlib import Path
import json
root = Path('results/stage9/raw')
index = json.loads((root / 'operator-run-index.json').read_text())
for run in index['runs']:
    print('CELLULE', run['world_id'], 'seed=', run['seed'])
    journal = root / run['journal_path']
    for line in journal.read_bytes().splitlines():
        item = json.loads(line)
        event = item['causal_event']
        if event.get('kind') in {
            'command_experienced', 'world_transition_experienced',
            'auto_segment_commit', 'agency_comparison',
            'causal_inference_status_published',
        }:
            print('  ', item['event_id'], event.get('kind'), event.get('t_monde'))
    state = json.loads((root / run['causal_state_path']).read_text())
    memory = state.get('memory', {})
    print('  Episodes Memory clos :', len(memory.get('episodes', [])))
PY
```

**Attendu :** identifiants techniques (`event_id`) liés aux pas du monde, et nombre d'épisodes clos. L'opérateur **ne doit pas publier cette sortie**. L'évaluateur examine ensuite le contenu original, les liens de provenance, les effets observés et les `event_refs` de chaque épisode ; un identifiant affiché n'est **pas** une preuve causale à lui seul.

### 10.2. Créer `results/stage9/private-annotations.json`

La structure exacte est :

```json
{
  "protocol_version": "stage9-heldout-independent-annotations-v1",
  "registration_digest": "EMPREINTE_CANONIQUE_REELLE_64_HEX",
  "runs": [
    {
      "world_id": "UN_MONDE_POSITIF_REEL",
      "seed": 0,
      "known_cause_cases": [
        {
          "id": "ID_CAS_UNIQUE",
          "episode_ref": "ID_EPISODE_MEMORY_CLOS_REEL",
          "observation_ref": "EVENT_ID_TRANSITION_PHYSIQUE_REELLE",
          "ground_truth": "self",
          "attribution": "self_compatible"
        }
      ],
      "naturally_acquired_false_candidates": []
    },
    {
      "world_id": "UN_MONDE_NUL_REEL",
      "seed": 0,
      "known_cause_cases": [],
      "naturally_acquired_false_candidates": [
        {
          "id": "ID_CANDIDAT_UNIQUE",
          "contingency_ref": "ID_REGLE_CAUSALE_REELLEMENT_ACQUISE",
          "episode_ref": "ID_EPISODE_MEMORY_CLOS_REEL",
          "observation_ref": "EVENT_ID_TRANSITION_PHYSIQUE_REELLE_DISTINCTE",
          "causal_status": "hypothese_causale"
        }
      ]
    }
  ]
}
```

**EXEMPLE DE FORME SEULEMENT :** les références et la graine montrées ne sont pas des observations réelles et **ne doivent jamais être copiées telles quelles**. Fournir **une entrée par cellule préenregistrée**, même avec deux tableaux vides lorsqu'aucune observation admissible n'existe. Les champs racines et par cellule ne peuvent pas être complétés par des métadonnées arbitraires : garder les schémas stricts.

**Sens et contraintes des valeurs :**

| Champ | Source réelle et interprétation |
| --- | --- |
| `world_id`, `seed` | Valeurs exactes du préenregistrement, **une fois chaque couple** ; ne pas les réinventer. |
| `known_cause_cases[*].id` | Identifiant unique de cas dans sa cellule. |
| `episode_ref` | ID d'un épisode **clos** dans `causal-state.json` sous `memory.episodes`. |
| `observation_ref` | `event_id` d'une véritable `world_transition_experienced` dans `journal.jsonl`, avec commande associée, pas appliqué et commit autobiographique cohérent. |
| `ground_truth` | `self` : conséquence réellement imputable à l'action ; `world` : cause externe ; `none` : **aucun effet physique pertinent**. Justification externe requise. |
| `attribution` | Résultat effectivement émis : `self_compatible`, `world_justified` ou `uncertain`. Une abstention **n'est pas** une attribution correcte. |
| `naturally_acquired_false_candidates[*].contingency_ref` | Référence canonique d'une règle **fausse et acquise par l'individu**, validée contre la vérité indépendante ; une même règle comptée **au plus une fois par cellule**. |
| `causal_status` | État réellement présent : `correlation_observee`, `hypothese_causale`, `testee_par_intervention` ou `etablie`. Ne pas inventer `etablie`. |

Le banc doit documenter séparément : preuve que les causes et les contrôles nuls sont correctement connus, interventions comparables, variables contrôlées, épisodes indépendants, exclusions éventuelles et témoins négatifs. L'examen `INV-25` est **supplémentaire** et n'est pas déduit automatiquement de ces simples lignes.

**Règles cruciales :**

- Une `ground_truth="none"` n'entre **pas** dans le dénominateur des attributions positives correctes ; une attribution causale malgré l'absence d'effet peut invalider l'évaluation.
- Une observation physique ne peut pas être créditée deux fois dans une cellule, même sous deux IDs ; plusieurs transitions distinctes peuvent appartenir à un même épisode Memory clos, sans garantir leur indépendance statistique.
- Les fausses hypothèses sont relevées **seulement si l'individu les a réellement acquises**. Ne jamais injecter de faux candidat pour produire artificiellement un dénominateur positif.
- Si aucune hypothèse fausse n'a été acquise, écrire `[]` et accepter le statut `not_evaluable` si le dénominateur global est nul. Ne pas écrire « 0 % de superstition ».

---

## 11. Générer le rapport et le sceller

### 11.1. Conversion des annotations indépendantes en preuves vérifiables

Créer les chemins de sortie **inexistants** `results/stage9/heldout.json` et `results/stage9/raw-artifact-index.json` via :

```bash
python -m lab.stage9_heldout_runner package \
  --registration research/stage9/registration.json \
  --runs-root results/stage9/raw \
  --annotations results/stage9/private-annotations.json \
  --evidence results/stage9/heldout.json \
  --raw-index results/stage9/raw-artifact-index.json \
  > results/stage9/receipts/package-receipt.json

cat results/stage9/receipts/package-receipt.json
```

**Attendu si l'audit structurel réussit :**

`"status": "provisional_evidence_packaged_requires_independent_review"`

La sortie comprend aussi `assessment`, `registration_digest`, `evidence_sha256`, `scientific_verdict: null`, `golden_stage9_frozen: false`.

**Signification :** les références de la déclaration sont cohérentes avec les fichiers effectivement présents, leurs SHA et la provenance Memory/journal contrôlée. **L'évaluation scientifique reste humaine et indépendante.** `assessment` peut être `not_evaluable`, `below_preregistered_confidence_threshold` ou un autre statut défavorable sans que la commande échoue : **un rapport défavorable valide doit être conservé**.

Le lanceur crée automatiquement :

- `heldout.json`, au format `stage9-heldout-evidence-v2` : métriques sources et références par monde/graine ;
- `raw-artifact-index.json`, au format `stage9-heldout-raw-artifact-index-v4` : chemins relatifs vers les quatre fichiers originaux/rejeux de chaque cellule.

Si `package` échoue pour une annotation injustifiée ou une référence absente, **ne pas inventer de preuve**. Conserver l'échec et demander un audit des originaux. Une correction purement documentaire de transcription doit laisser une trace datée et être justifiée ; une modification des règles d'inclusion ou des métriques après résultats n'est pas autorisée.

### 11.2. Archiver le rapport dans **le même Git isolé**

```bash
# Ne pas faire 'git add -A' : le dossier contient des secrets et archives brutes.
git add results/stage9/heldout.json
git commit -m "Archive Stage 9 heldout evidence"
export EVIDENCE_COMMIT="$(git rev-parse HEAD)"

git merge-base --is-ancestor "$FREEZE_SHA" "$REGISTRATION_COMMIT"
git merge-base --is-ancestor "$REGISTRATION_COMMIT" "$EVIDENCE_COMMIT"

git log --oneline --max-count=3
```

**Attendu :** trois points temporels ordonnés par ascendance Git : **code figé → protocole scellé → résultats**. Les fichiers `src/`, `pyproject.toml`, la spécification anglaise et `registration.json` doivent être inchangés dans toute la chaîne.

> **Ne rien pousser** vers une destination partagée : les graines held-out figurent en clair dans le commit du protocole et restent accessibles dans l'historique, même si les fichiers de sortie sont limités.

---

## 12. Effectuer l'audit indépendant final

Les commandes suivantes ne modifient ni les journaux, ni les preuves. Elles se lancent **après** le commit des résultats, dans le même dépôt Git isolé, avec les **octets originaux** conservés.

### 12.1. Vérifier l'antériorité Git et l'immutabilité

```bash
python -m lab.stage9_registration_chronology \
  --repo . \
  --registration research/stage9/registration.json \
  --registration-commit "$REGISTRATION_COMMIT" \
  --evidence results/stage9/heldout.json \
  --evidence-commit "$EVIDENCE_COMMIT" \
  > results/stage9/receipts/git-chronology.json
```

**Attendu :** JSON sans exception, comprenant notamment les empreintes du code et de la spécification, la chronologie examinée, les métriques provisoires et `scientific_verdict: null`. **Signification :** cohérence de l'ascendance Git ; **pas** preuve indépendante d'heure réelle ou d'accès humain aux données.

### 12.2. Recalculer séparément le score provisoire

```bash
python -m lab.stage9_scientific_assessment \
  --registration research/stage9/registration.json \
  --evidence results/stage9/heldout.json \
  > results/stage9/receipts/metric-assessment.json
```

**Attendu :** `assessment` et indicateurs mesurés, sans verdict scientifique. Voir [tableau d'interprétation](#132-comment-interpréter-assessment).

### 12.3. Vérifier les octets des journaux et Memory clos

```bash
python -m lab.stage9_heldout_artifact_custody \
  --registration research/stage9/registration.json \
  --evidence results/stage9/heldout.json \
  --index results/stage9/raw-artifact-index.json \
  --artifact-root results/stage9/raw \
  > results/stage9/receipts/raw-custody.json
```

**Attendu :** `"artifact_custody_status": "raw_bytes_match_report_requires_independent_provenance_review"`, à condition que toutes les structures, empreintes et sources admissibles passent. **Signification :** cohérence **informatique** entre les artefacts présents et les faits revendiqués, sans preuve physique d'indépendance de l'expérience.

### 12.4. Obtenir un reçu machine consolidé

```bash
python -m lab.stage9_independent_handoff \
  --repo . \
  --registration research/stage9/registration.json \
  --registration-commit "$REGISTRATION_COMMIT" \
  --evidence results/stage9/heldout.json \
  --evidence-commit "$EVIDENCE_COMMIT" \
  --manifest-index results/stage9/physical-manifest-index.json \
  --manifest-root results/stage9/raw-manifests \
  --raw-index results/stage9/raw-artifact-index.json \
  --raw-artifact-root results/stage9/raw \
  > results/stage9/receipts/independent-handoff.json
```

**Attendu :** un objet avec :

- `handoff_status = machine_checks_consistent_requires_independent_scientific_review`, **ou** `machine_checks_complete_with_explicit_review_blockers` si des alertes demandent un examen ;
- `review_blockers` (liste à lire **en entier**, pas à ignorer) ;
- `machine_handoff_sha256` (identité du reçu) ;
- sous-rapports `git_chronology`, `current_checkout_preflight`, `physical_manifest_custody`, `raw_artifact_custody`, `provisional_metrics` ;
- `independent_world_custody_attested = false`, `independent_seed_selection_attested = false`, `prospective_approval_attested = false`, `oracle_isolation_attested = false`, `scientific_verdict = null`, `golden_stage9_frozen = false`.

**Signification :** le logiciel **refuse volontairement** de certifier ce que seule la personne indépendante peut attester. Le champ `machine_handoff_sha256` n'est pas une signature de l'évaluateur.

---

## 13. Interpréter les résultats et rendre le verdict

### 13.1. Métriques obligatoires à comprendre

| Champ du rapport | Interprétation exacte |
| --- | --- |
| `known_cause_cases` | Nombre de cas physiquement causaux (`self` ou `world`) admissibles ; les `none` ne comptent pas. |
| `correct_links` | Nombre de ces cas avec attribution correspondant à la véritable cause. |
| `uncertain_links` | Nombre de cas où l'individu n'a pas décidé ; **pas** comptés corrects. |
| `false_self_links` | Attributions à soi incorrectes, y compris celles portées sur des contrôles sans effet. |
| `known_cause_accuracy` | `correct_links / known_cause_cases`, si dénominateur non nul. |
| `known_cause_wilson_95` | Intervalle de confiance Wilson bilatéral à 95 % pour cette exactitude. Le système compare **la borne inférieure** au minimum fixé. |
| `no_effect_control_cases` | Cas où aucune conséquence causale pertinente n'a eu lieu. |
| `no_effect_control_abstentions` | Contrôles sans effet correctement laissés en `uncertain`, consignés séparément. |
| `no_effect_control_false_attributions` | **Attributions injustifiées** malgré l'absence d'effet ; elles bloquent l'éligibilité. |
| `natural_false_candidate_count` | Nombre de règles réellement apparues et indépendamment identifiées comme fausses sur les mondes nuls. |
| `false_established_count` | Sous-ensemble de ces règles devenues `etablie` à tort. |
| `superstitious_rule_rate` | `false_established_count / natural_false_candidate_count`, si dénominateur non nul. |
| `superstition_wilson_95` | Intervalle de Wilson bilatéral à 95 % pour ce taux ; le système compare **la borne supérieure** au plafond fixé. |
| `positive_known_cause_runs`, `registered_positive_runs` | Couverture des mondes et graines positifs : chaque cellule positive doit avoir au moins un cas de cause positive réellement observé. |
| `negative_runs_without_natural_candidates` | Cellules nulles sans hypothèse fausse naturellement observée ; le reviewer doit examiner la concentration et l'échantillonnage. |
| `reused_closed_memory_*` | Plusieurs observations/candidats dans un même épisode clos : alertes sur la dépendance, **pas** automatiquement des duplications physiques. |
| `cross_run_identical_archives` | Journaux/états identiques entre cellules différentes ; nécessitent une explication indépendante. |

Les intervalles Wilson ne démontrent pas, à eux seuls, l'indépendance statistique des observations. L'évaluateur doit examiner la structure des mondes, graines, contextes et épisodes, ainsi que les hypothèses de l'analyse préenregistrée.

### 13.2. Comment interpréter `assessment`

| Valeur retournée par le code | Interprétation | Réaction |
| --- | --- | --- |
| `unregistered` | Aucun protocole fourni. | **NO-GO** : ne pas exécuter. |
| `awaiting_holdout_campaign` | Préenregistrement présent, résultats absents. | Pas de conclusion scientifique. |
| `invalid_no_effect_attribution` | Au moins une attribution causale a été créditée malgré l'absence d'effet physique. | Résultat non éligible ; examiner et rapporter l'échec. |
| `not_evaluable` | Dénominateur de causes connues **ou** de candidats faux naturellement acquis = **zéro**. | Ne pas transformer en 0 %, ne pas conclure PASS ; classer non évaluable. |
| `incomplete_known_cause_world_coverage` | Au moins une cellule positive n'a pas de cas positif réellement observé. | Couverture incomplète ; résultat non éligible. |
| `insufficient_natural_candidates` | Moins de candidats spontanés que le minimum fixé à l'avance. | Insuffisant selon le protocole ; ne pas en ajouter. |
| `below_preregistered_confidence_threshold` | Borne inférieure de l'exactitude trop basse **ou** borne supérieure de superstition trop haute. | Critères métriques non atteints ; consigner `FAIL` si les données sont valides. |
| `metrics_eligible_for_independent_review` | Les contrôles **métriques** automatisés passent, avec les limites préenregistrées. | **Pas un PASS scientifique** : examen des preuves physiques, de l'indépendance, de la chronologie et d'`INV-25` encore nécessaire. |

Une exception Python ou un code de retour non nul indique un **échec de validation technique**, pas un mauvais score à ignorer. Le dossier doit rester archivé en l'état.

### 13.3. Validation indépendante d'`INV-25` et de la causalité

L'évaluateur doit analyser et signer, **au-delà du scorer** :

1. **Causalité réelle :** conditions positives et nulles authentiques ; absence d'accès à la vérité oracle depuis le moteur cognitif ; interventions contrôlées et expériences réellement vécues, pas de dossiers fabriqués.
2. **Attribution :** comparer les effets mesurés, les prédictions gelées et l'attribution effectivement produite ; examiner toutes les erreurs et abstentions.
3. **Statut `etablie` :** vérifier que le simulateur ne modifie ses prédictions que pour une contingence réellement `etablie`, conformément aux mécanismes normatifs.
4. **Statut `etabli_pour_securite` :** démontrer avec des comparaisons appariées qu'une interdiction de sécurité rend l'action inadmissible **sans modifier** l'évaluation `R_a` ni les sorties du simulateur, toutes choses égales par ailleurs.
5. **Provenance :** justifier l'antériorité indépendante des données, la chaîne des décisions, les états Memory clos, les enregistrements canoniques et les rejouages.
6. **Limites :** documenter les limites liées au modèle d'équipement exact, aux observations ou candidats absents, aux contextes non indépendants et aux fonctionnalités Stage 11 non disponibles au Stage 9.

**Il n'existe pas, dans la commande `run`, de signature automatique d'un examen `INV-25`.** Les comparaisons doivent être produites selon le protocole **préétabli** et vérifiées par l'évaluateur ; si elles ne peuvent pas être menées sans modifier le code ou le plan après exposition aux données, la clôture scientifique est **bloquée**.

### 13.4. Fiche de décision à signer

À renseigner **à partir des originaux**, sans prétendre que l'outil décide :

```text
ID de campagne : ______________________________
Code figé (40 hex) : ___________________________
Commit préenregistrement (40 hex) : _____________
Commit preuves (40 hex) : ______________________
Digest canonique protocole (64 hex) : ___________
Digest preuves (64 hex) : ______________________
Gardien indépendant : __________________________
Opérateur : ___________________________________
Évaluateur indépendant : _______________________
Preuve de signature/antériorité : _______________
Mondes × graines annoncés / exécutés : _________
Observations causales / exactitude : ____________
Candidats faux naturels / établis à tort : ______
Intervalles de confiance et seuils : ____________
INV-25 : [ ] satisfait [ ] échoué [ ] non vérifié
Oracle isolé et provenance : ____________________
Incidents, exclusions et contre-exemples : ______

VERDICT : [ ] PASS [ ] FAIL [ ] INCONCLUSIVE
Motifs et preuves originales : _________________
Date, identité et signature indépendante : ______
Contresignature, si prévue : ____________________
```

**`PASS` :** seulement si **tous** les critères normatifs et préenregistrés sont vérifiés et si les preuves indépendantes sont suffisantes.  
**`FAIL` :** conditions valides mais au moins un critère échoué.  
**`INCONCLUSIVE` :** données, échantillon, antériorité, provenance, preuves de contrôle nul, instrument ou indépendance insuffisants ; expliquer précisément pourquoi.

Même un PASS humain documenté n'entraîne **aucune** fusion automatique de PR et **aucune** création automatique de Golden. La décision de gel scientifique appartient au processus de gouvernance du projet.

---

## 14. Gérer les anomalies sans perdre la valeur scientifique

| Situation | Conduite obligatoire |
| --- | --- |
| `ModuleNotFoundError`, mauvaise version Python, install impossible | Arrêter avant le GO ; corriger l'environnement et relancer les **tests de développement** uniquement. |
| `registration requires exact mandatory fields` ou `...schema mismatch` | Vérifier les 30 champs, types et versions ; ne pas ignorer le validateur. |
| `normative specification digest mismatch` | Comparer au document anglais **original**, au bon code et aux bons octets ; ne jamais modifier la spécification normative. |
| `physical manifest digest mismatch` | Vérifier les originaux, chemins et droits ; si l'approbation a déjà eu lieu, toute révision exige une procédure prospective traçable avant exposition ou un statut inconclusif. |
| `operator seal requires complete unshallowed Git history` | Obtenir l'historique Git complet **avant** exécution ; ne pas simuler un historique. |
| `execution checkout must be at preregistration commit` | Vérifier `git rev-parse HEAD` et `REGISTRATION_COMMIT` ; ne pas modifier le code pour contourner le contrôle. |
| `absent, incomplete or conflicting human GO record` | **NO-GO** : retrouver les vraies signatures et l'approbation ; ne pas écrire une fausse identité ni un faux GO. |
| Dossier `raw` déjà présent | Ne pas l'effacer : il peut contenir un essai ou un échec. Examiner le dossier et la règle d'arrêt ; demander une nouvelle autorisation si nécessaire. |
| Rejeu non identique | Consigner `FAIL` ou `INCONCLUSIVE` suivant le protocole. Conserver **les deux** originaux ; ne pas réparer silencieusement. |
| `safety_block`, épisode incomplet, interruption | Préserver les traces, rapporter la cellule, respecter les exclusions et règles d'arrêt **définies avant** l'expérience. |
| Absence de fausse hypothèse naturelle | Dénominateur nul ou insuffisant ; **ne jamais injecter d'hypothèses pour augmenter le volume**. |
| Preuve `observation_ref` absente / Memory non clos | Refuser le crédit de la preuve, préserver l'échec, vérifier le protocole et les artefacts originaux. |
| `review_blockers` non vide | Examiner **chaque** avertissement, conserver la justification et ses pièces ; ne pas supprimer de ligne pour obtenir un reçu « propre ». |
| Accès prématuré aux graines/labels ou consultation préalable des résultats | Documenter la fuite. L'évaluation n'est plus véritablement held-out pour les acteurs exposés ; **nouveau plan indépendant** requis avant toute revendication scientifique. |
| Contrôle négatif impossible avec le lanceur actuel | **NO-GO** avant exposition : signaler un besoin de développement/modification puis **nouveau code figé et nouveau préenregistrement**. |

**Principe directeur :** une expérience qui échoue proprement est une information scientifique. Une expérience réécrite après ses résultats n'en est plus une.

---

## 15. Remettre les livrables et clore le mandat

Le paquet remis au responsable scientifique doit distinguer **informations partageables** et **archives réservées** :

**A. Rapport communicable après levée des restrictions du protocole**

- Identité exacte du logiciel et versions, description du plan, effectifs, métriques et intervalles, verdict signé et limites.
- Date/heure et référence de l'attestation prospective ; résumé des contrôles et anomalies.
- Conclusions favorables **et** défavorables, dont `FAIL` / `INCONCLUSIVE` et `review_blockers`.

**B. Dossier confidentiel pour l'évaluateur / gardien seulement**

- Copie **complète et protégée** du Git isolé (dont tous les ancêtres, le protocole avec graines en clair et le commit de preuves), signatures originales, registres d'accès et horodatages.
- Tous les JSON gelés, manifestes monde et scénarios **originaux**, graines et justificatifs de séparation calibration/held-out.
- `operator-run-index.json`, **toutes** les cellules originales et leurs rejouages, `bench-only-world-truth.json` et annotations signées.
- `heldout.json`, `raw-artifact-index.json` et tous les reçus de l'étape 12.
- Documentation des paramètres de calibration, équipement entraîné, environnement Python, incidents, observations non créditées, contrôles `INV-25` et contre-exemples.

**Ne pas transférer le dépôt isolé vers le GitHub de développement**, car son historique révèle les données réservées. Le destinataire décide de la diffusion selon le protocole, après examen des risques de révélation et du calendrier de publication.

---

## 16. Annexes : modèles et aide-mémoire

### Annexe A. Ordre strict des jalons

| N° | Condition à remplir | Résultat acceptable avant de poursuivre |
| --- | --- | --- |
| 1 | Code et environnement vérifiés sans held-out | Tests verts ; SHA du code retenu ; intégration logicielle distincte de la campagne scientifique. |
| 2 | Paramètres, équipement, ontologie et générateur reçus | JSON valides, valeur réelle, provenance de calibration. |
| 3 | Mondes et graines sélectionnés sous garde | Séparation calibration/held-out et contrôles positifs/nuls crédibles, secrets conservés. |
| 4 | Préenregistrement complété | `draft_requires_independent_git_seal`, valeurs réelles, pas de champs manquants. |
| 5 | Protocole signé puis commit de protocole créé dans Git isolé | `REGISTRATION_COMMIT` descendant du gel + preuve d'antériorité externe. |
| 6 | Index et précontrôles conformes | Manifestes originaux correspondent ; code gelé inchangé. |
| 7 | Décision humaine GO signée | Identités, conflits, garde et approbation vérifiés **avant résultat**. |
| 8 | Commande `run` | `operator_execution_archived_requires_external_annotation` et totalité des cellules archivées. |
| 9 | Annotations indépendantes | Chaque référence se retrouve dans les journaux et Memory clos, vérités externes justifiées. |
| 10 | Commande `package` | `provisional_evidence_packaged_requires_independent_review`, même si métriques défavorables. |
| 11 | Commit des preuves et quatre audits | Chronologie, score, artefacts et reçu consolidé archivés. |
| 12 | Revue `INV-25` et verdict | Rapport indépendant signé PASS / FAIL / INCONCLUSIVE avec limites et contre-exemples. |

### Annexe B. Commandes essentielles à conserver à portée de main

```bash
# 1. Préenregistrement bien formé, pas encore approuvé
python -m lab.stage9_scientific_preregistration \
  --manifest research/stage9/registration.json

# 2. Identité physique des manifestes
python -m lab.stage9_registered_manifest_custody \
  --registration research/stage9/registration.json \
  --index results/stage9/physical-manifest-index.json \
  --artifact-root results/stage9/raw-manifests

# 3. Code sur disque identique au code approuvé
python -m lab.stage9_frozen_worktree --repo . --frozen-commit "$FREEZE_SHA"

# 4. Après GO réel : toutes les cellules (ne jamais lancer à titre de diagnostic)
python -m lab.stage9_heldout_runner run --repo . \
  --registration research/stage9/registration.json \
  --registration-commit "$REGISTRATION_COMMIT" \
  --manifest-index results/stage9/physical-manifest-index.json \
  --manifest-root results/stage9/raw-manifests \
  --external-go-record results/stage9/private-release-record.json \
  --output-root results/stage9/raw

# 5. Après annotation des événements réels
python -m lab.stage9_heldout_runner package \
  --registration research/stage9/registration.json \
  --runs-root results/stage9/raw \
  --annotations results/stage9/private-annotations.json \
  --evidence results/stage9/heldout.json \
  --raw-index results/stage9/raw-artifact-index.json

# 6. Après commit des preuves : tous les contrôles machine
python -m lab.stage9_independent_handoff --repo . \
  --registration research/stage9/registration.json \
  --registration-commit "$REGISTRATION_COMMIT" \
  --evidence results/stage9/heldout.json \
  --evidence-commit "$EVIDENCE_COMMIT" \
  --manifest-index results/stage9/physical-manifest-index.json \
  --manifest-root results/stage9/raw-manifests \
  --raw-index results/stage9/raw-artifact-index.json \
  --raw-artifact-root results/stage9/raw
```

### Annexe C. Signification des trois drapeaux les plus importants

| Signal | Traduction opérationnelle |
| --- | --- |
| `scientific_verdict: null` | **Normal**, y compris après tous les outils. L'évaluateur n'a pas été remplacé par le logiciel. |
| `golden_stage9_frozen: false` | **Normal**, y compris si les métriques sont prometteuses. Aucun Golden n'est créé automatiquement. |
| `...requires_independent_review` | Contrôle machine réussi, mais les personnes indépendantes doivent encore vérifier les éléments qui ne peuvent pas être prouvés à partir des seuls fichiers. |

### Annexe D. Fiche de démarrage pour le gardien

```text
Code figé approuvé : ___________________________
Personne responsable et signature : ___________
Gardien et conflit examiné : ___________________
Opérateur et périmètre : _______________________
Évaluateur indépendant : ______________________
Lieu privé du Git complet : ____________________
Lieu des originaux chiffrés : ___________________
Lieu de la preuve de temps indépendante : ______
Nombre de mondes positifs : ____________________
Nombre de mondes négatifs : ____________________
Nombre de mondes de calibration : ______________
Nombre de graines held-out : ___________________
Durée et règle d'arrêt : _______________________
Critères métriques signés (référence) : _________
Critères de causalité/INV-25 signés : ___________
Validation des manifestes : ____________________
Décision AVANT expérience : [ ] NO-GO [ ] GO
Signatures et date : ___________________________
```

---

### Note finale au nouvel évaluateur

**Votre travail consiste à vérifier une affirmation, pas à l'obtenir.** Le meilleur service rendu au projet est un dossier qui permet à une personne tierce de reconstruire ce qui a été décidé, exécuté, observé et jugé, y compris lorsque la conclusion est défavorable.

*Ce guide reprend les interfaces logicielles de l’intégration `main` inspectées le 10 octobre 2026, avec `b304ebda7facf8ba285408e87090727dafc43bcb` comme point de départ potentiel, **non approuvé scientifiquement**. Le commit retenu doit être sélectionné puis gelé prospectivement par les responsables indépendants. Toute modification ultérieure du code expérimental impose une nouvelle vérification des commandes et un nouveau gel scientifique.*
