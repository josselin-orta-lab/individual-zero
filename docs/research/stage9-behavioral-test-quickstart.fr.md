# Stage 9 : test comportemental minimal pour les observateurs

**Objectif :** reproduire localement le diagnostic de développement d'Individual Zero (I0), observer la formation d'hypothèses causales et vérifier si les tests proposés débouchent sur des actions réellement exécutées.

**Statut : diagnostic exploratoire reproductible, PAS une campagne scientifique indépendante.** Les graines 41 et 42 et les mondes cités ici sont **publics et connus des développeurs**. N'utiliser aucune graine ou donnée réservée à la campagne `held-out`. Aucun score obtenu ici n'autorise un GO, un Golden Stage 9 ou la clôture d'INV-25.

**Durée :** dépend de la machine. **Coût CI :** nul si les commandes sont exécutées localement. **Machine utilisée pour le premier constat :** Arch Linux `x86_64`, Proxmox LXC, Python 3.12.15. Le diagnostic lui-même est du Python et peut aussi s'exécuter sur un autre système Linux avec les mêmes dépendances.

Ce guide reproduit le protocole documenté dans le [rapport français du 10 octobre 2026](stage9-development-behavior-2026-10-10.fr.md). Il est distinct du [manuel de campagne held-out](stage9-independent-heldout-evaluation-manual.fr.md).

## 1. Prérequis

Il faut disposer d'un compte ayant **accès au dépôt GitHub privé** `josselin-orta-lab/individual-zero`, d'une connexion Internet pour l'installation, de Git, de `uv` et de Python 3.12. Aucun GPU, Docker, interface graphique ou GitHub Actions n'est nécessaire.

**Arch Linux** (avec un utilisateur normal disposant de `sudo`) :

```bash
sudo pacman -Syu
sudo pacman -S --needed git uv github-cli
```

Dans **certains conteneurs Proxmox LXC**, `pacman` peut échouer avec `Landlock is not supported by the kernel` ou `switching to sandbox user 'alpm' failed`. Dans ce cas seulement, réessayer la commande qui a échoué en ajoutant `--disable-sandbox-filesystem` :

```bash
sudo pacman -Syu --disable-sandbox-filesystem
sudo pacman -S --needed git uv github-cli --disable-sandbox-filesystem
```

Cette option réduit l'isolation des accès aux fichiers **pour cette invocation** de `pacman`. Ne pas désactiver globalement la sécurité du conteneur. Si l'utilisateur est déjà `root`, ne pas préfixer `pacman` par `sudo` ; utiliser ensuite de préférence un compte normal pour travailler sur I0.

Sur un autre système Linux, installer les mêmes outils avec son gestionnaire de paquets. Le reste des instructions utilise un terminal Bash.

## 2. Récupérer le dépôt (une seule fois)

Le dépôt étant privé, se connecter à GitHub ; suivre le code de connexion dans son propre navigateur :

```bash
gh auth login --hostname github.com --git-protocol https --web
gh auth setup-git
mkdir -p ~/Projets
cd ~/Projets
gh repo clone josselin-orta-lab/individual-zero
```

Si le dépôt est **déjà cloné**, ne pas le re-télécharger. Entrer directement dans `~/Projets/individual-zero`.

**Ne jamais partager** les jetons GitHub, mots de passe ou codes temporaires.

## 3. Préparer Python et enregistrer l'environnement

```bash
cd ~/Projets/individual-zero
git switch main
git pull --ff-only
git status --short --branch

uv python install 3.12
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip install -e .
python --version
individual-zero --help
```

Le résultat attendu pour `python --version` est `Python 3.12.x`. `individual-zero --help` vérifie uniquement que la commande est installée ; **elle ne lance pas le diagnostic cognitif**.

Créer un dossier local de conservation (ignoré par Git) et noter les métadonnées **avant de lancer le test** :

```bash
mkdir -p artifacts/stage9-behavior-dev
{
  printf 'utc_start='; date -u +%Y-%m-%dT%H:%M:%SZ
  printf 'commit='; git rev-parse HEAD
  printf 'branch='; git branch --show-current
  printf 'git_status='; git status --short --branch
  printf 'kernel='; uname -sr
  printf 'architecture='; uname -m
  printf 'python='; python --version
} > artifacts/stage9-behavior-dev/environment.txt
```

Conserver le **SHA complet** de `git rev-parse HEAD` : le nom `main` évolue et ne suffit pas à identifier une expérience. Si le dépôt comporte des modifications locales, les signaler dans le compte rendu : le SHA Git seul ne couvre pas ces modifications.

## 4. Lancer le diagnostic comportemental

Toujours dans `~/Projets/individual-zero`, avec `(.venv)` actif :

```bash
python -m lab.stage9_hydration_contrast_report \
  > artifacts/stage9-behavior-dev/results.txt
```

Le protocole `stage9-hydration-contrast-diagnostic-v1` exécute **8 cellules**, avec les graines 41 et 42, **18 pas simulés par cellule**, et quatre mondes :

| Monde | Rôle |
| --- | --- |
| `null_water_reference` | Témoin : boire n'augmente pas l'eau |
| `small_water_gain` | Effet physique positif modéré (+12) |
| `recurrent_water_need` | Variante exploratoire : gain (+35) et décroissance d'eau modifiés |
| `model_aligned_water_gain` | Variante exploratoire : gain (+40), conforme à la prédiction de référence |

Ces paramètres sont **déjà définis dans le code**. Aucune hypothèse ou action causale correcte n'est injectée par ce script. La variante `recurrent_water_need` ne doit pas être présentée comme un contraste où seule la quantité d'eau gagnée varie.

Vérifier que le fichier a été créé :

```bash
test -s artifacts/stage9-behavior-dev/results.txt && echo 'Diagnostic enregistré'
```

## 5. Afficher un résumé lisible

Copier tout ce bloc :

```bash
python - <<'PY'
import json
from pathlib import Path

path = Path("artifacts/stage9-behavior-dev/results.txt")
raw = path.read_text(encoding="utf-8").strip()
prefix = "stage9_hydration_contrast="
if not raw.startswith(prefix):
    raise SystemExit("Sortie inattendue : diagnostic absent ou incomplet.")
report = json.loads(raw[len(prefix):])

fields = (
    ("Statut causal", "causal_status"),
    ("Options distinctes", "distinct_causal_test_options"),
    ("Propositions émises", "causal_test_proposals"),
    ("Enregistrements acceptés", "accepted_causal_test_registrations"),
    ("Évaluations indisponibles", "unscored_test_evaluations"),
    ("Contextes d'eau accessibles", "accessible_test_context_steps"),
    ("Tests causaux exécutés", "applied_causal_test_drinks"),
    ("Interventions publiées", "published_interventions"),
    ("Raison du blocage", "causal_test_unpredicted_proposal_reasons"),
    ("Preuves manquantes", "missing_evidence"),
)
for case in report["cases"]:
    print(f"\nMonde : {case['world']} | Graine : {case['seed']}")
    for label, key in fields:
        value = case.get(key)
        print(f"  {label} : {'non renseigné' if value is None else value}")

positives = [
    case for case in report["cases"]
    if case["world"] in {"small_water_gain", "recurrent_water_need"}
]
print("\nTotaux des quatre cellules positives :")
for key in (
    "causal_test_proposals",
    "accepted_causal_test_registrations",
    "unscored_test_evaluations",
    "accessible_test_context_steps",
    "applied_causal_test_drinks",
    "published_interventions",
):
    print(f"  {key} : {sum(case.get(key) or 0 for case in positives)}")

print("\nAcceptation scientifique :", report["acceptance_status"])
print("Golden gelé :", report["golden_stage9_frozen"])
PY
```

**Interprétation :** `hypothese_causale` signifie qu'une hypothèse a été publiée. `causal_test_proposals` dénombre des **émissions**, pas des expériences indépendantes ; `distinct_causal_test_options` dénombre les options différentes. Seules les **actions réellement appliquées** et leurs preuves permettent d'attester des interventions. `None` / `null` dans les témoins signifie *non renseigné ou non applicable*, **pas zéro observé**.

### Point de comparaison historique (pas un résultat garanti)

Dans le [constat du 10 octobre 2026](stage9-development-behavior-2026-10-10.fr.md), les quatre cellules positives totalisaient 163 propositions émises, 163 enregistrements acceptés, 163 évaluations indisponibles, 44 contextes d'eau accessibles et **zéro intervention causale exécutée**. Les chiffres peuvent changer si le code change. Toujours comparer en utilisant le SHA Git conservé.

La prédiction `equipment_input_unseen` indique une entrée non couverte par l'Equipment. Mais la cause structurelle du défaut de sélection des tests est également connue : la motivation intrinsèque des options `test_causal` reste `not_evaluated` en attendant Exploration/P-48 (Stage 11). **Ne pas contourner ce mécanisme ou forcer des actions pour obtenir un score positif.**

## 6. Conserver et partager les preuves

```bash
sha256sum artifacts/stage9-behavior-dev/results.txt \
  > artifacts/stage9-behavior-dev/results.sha256
sha256sum -c artifacts/stage9-behavior-dev/results.sha256
cat artifacts/stage9-behavior-dev/environment.txt
cat artifacts/stage9-behavior-dev/results.sha256
```

Le dossier `artifacts/` est ignoré par Git : **il ne sera pas publié automatiquement**. Pour transmettre un résultat à l'équipe, conserver les trois fichiers `environment.txt`, `results.txt` et `results.sha256`, en précisant la date, le SHA complet et toute modification locale. Le hash atteste l'intégrité du fichier **que l'on possède**, pas son antériorité ni la validité scientifique indépendante.

**Optionnel : vérifier la répétabilité sur la même machine** :

```bash
python -m lab.stage9_hydration_contrast_report \
  > artifacts/stage9-behavior-dev/results-repeat.txt
cmp artifacts/stage9-behavior-dev/results.txt \
    artifacts/stage9-behavior-dev/results-repeat.txt \
  && echo 'Deux sorties identiques'
```

Une correspondance parfaite témoigne du déterminisme de ce diagnostic sur la configuration utilisée ; elle ne prouve pas une compétence cognitive générale.

## 7. Dépannage rapide

- **`cannot run less`** : `git --no-pager log -1 --oneline` affiche le commit sans `less`.
- **`uv` avertit que `~/.local/bin` est absent du PATH** : tant que `.venv` est activé et que `python --version` affiche Python 3.12, l'expérience fonctionne.
- **`ModuleNotFoundError: No module named 'lab'`** : revenir à la racine du dépôt, activer `.venv` puis relancer `uv pip install -e .`.
- **`Repository not found`** : vérifier l'accès au dépôt privé et `gh auth status` ; ne pas publier le jeton d'authentification.
- **Échec Landlock sous Proxmox LXC** : utiliser uniquement l'option `--disable-sandbox-filesystem` décrite à l'étape 1.

## 8. Ce que le test ne démontre pas

Cette procédure utilise des scénarios de développement connus, des durées et des graines fixes. Elle peut documenter des hypothèses, des propositions, des blocages et des interventions réellement enregistrées **dans ces scénarios**. Elle ne mesure pas à elle seule la généralisation, l'autonomie complète, le taux scientifique de superstitions, l'acceptation d'INV-25 ou l'atteinte d'un Golden. La [campagne held-out indépendante](stage9-independent-heldout-evaluation-manual.fr.md) suit un protocole séparé avec garde des mondes et préenregistrement. Son statut reste **NO-GO** jusqu'à autorisation et preuves indépendantes.
