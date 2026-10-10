# Individual Zero : vérification avant ouverture publique

**STATUT : PUBLICATION BLOQUÉE / AUDIT INCOMPLET / DÉPÔT PRIVÉ.**

Ce document est une checklist de préparation, **pas une attestation d'absence de secrets** ni une autorisation de rendre le dépôt public. Il doit rester exact après son éventuelle publication. La spécification normative anglaise v1.2.1 n'est pas modifiée.

## État observé le 10 octobre 2026

- Dépôt source : `josselin-orta-lab/individual-zero`, visibilité `private`, propriétaire de type compte personnel.
- Référence examinée : `main` à `773cd84557d661977568c318413510096d15fed0`, **avant** l'ajout de la présente documentation.
- Inventaire API : 267 fichiers suivis à cette révision et 11 branches consultables. Aucun chemin explicitement intitulé `.env`, clé privée ou fichier de secrets détecté dans les noms des fichiers de tête de ces branches.
- Analyse de motifs effectuée sur les **267 contenus de fichiers du HEAD `main`** : aucune signature évidente parmi les motifs examinés (clés privées PEM/SSH, tokens GitHub usuels, clés API courantes, clés AWS, URLs intégrant une authentification et affectations simples suspectes). Ce n'est **pas** un scan complet Gitleaks ni un audit de comportement du code.
- Les autres références ont été inventoriées mais **la totalité de leurs contenus et de leur historique n'a pas encore été scannée avec un détecteur de secrets complet**.
- Historique GitHub Actions : **715 exécutions** recensées via l'API lors de ce contrôle. Quelques journaux seulement ont été échantillonnés ; certains anciens journaux ne sont plus récupérables via la connexion GitHub. Aucun contrôle exhaustif des journaux et artefacts n'est établi.
- Fichiers de politique existants : `SECURITY.md`, `CONTRIBUTING.md`, `LICENSE` (Apache-2.0) et `LICENSE-DOCUMENTATION` (CC BY 4.0).
- Des fichiers de préparation `CODEOWNERS` et de modèle PR peuvent être ajoutés, mais **n'appliquent aucune restriction sans protection de branche configurée**.
- Règles GitHub : lecture des protections administratives non accessible à cette intégration ; l'API Rulesets de ce dépôt privé a refusé l'accès en indiquant que le plan devait être mis à niveau ou le dépôt rendu public. **Ne pas confondre impossibilité de lecture et preuve qu'aucune protection n'existe.**

## Conditions à satisfaire AVANT toute publication

- [ ] **Historique complet** : analyser localement les références de toutes les branches et tags, y compris les contenus supprimés des versions précédentes. Examiner également les anciens PR, commits accessibles par SHA, releases et artefacts distincts.
- [ ] **Secrets** : examen humain des alertes Gitleaks et des configurations. Révoquer et remplacer tout secret réellement exposé ; ne pas croire qu'une simple suppression dans `main` efface l'historique.
- [ ] **Actions** : contrôler les anciens logs/artefacts, traces de jobs, informations d'environnement et outputs, ainsi que les permissions `GITHUB_TOKEN`. Si certains éléments sont irrécupérables, documenter explicitement cette limite et décider s'il faut publier un dépôt assaini plutôt que l'historique original.
- [ ] **Confidentialité scientifique** : confirmer qu'aucun monde/graines `held-out`, vérité oracle, identité protégée ou enregistrement indépendant non exposable ne figure dans les commits, tests, discussions, Issues, PR, logs ou assets.
- [ ] **PII et propriété intellectuelle** : vérifier les emails personnels de commits, données de tiers, licences de dépendances, modèles, datasets, images et autorisations de publication. Les licences actuelles permettent les forks et les réutilisations conformément à leurs conditions.
- [ ] **Organisation** : créer l'organisation voulue, vérifier 2FA, permissions par défaut, accès administrateur, applications autorisées et éventuels collaborateurs directs préexistants.
- [ ] **Transfert** : vérifier les effets sur l'URL et les références scientifiques. GitHub peut **retirer définitivement l'ancien couple `owner/repo`** en cas d'utilisation importante d'Actions dans les sept jours précédant le transfert. Le volume récent observé justifie une vérification spécifique : [documentation GitHub](https://docs.github.com/en/repositories/creating-and-managing-repositories/transferring-a-repository).
- [ ] **CODEOWNERS et relecteurs** : vérifier que les propriétaires indiqués ont effectivement l'accès `Write` après transfert et qu'il existe un relecteur indépendant pour les PR du mainteneur lui-même.
- [ ] **Protection de `main`** : PR obligatoire, validation(s), CODEOWNERS si applicable, absence de push direct, restrictions de mise à jour aux seuls mainteneurs, blocage force-push/suppression, règles applicables aux administrateurs, vérifications manuelles des permissions.
- [ ] **CI et PR externes** : vérifier les workflows à privilèges réduits ; ne jamais accorder de secrets à du code de PR non fiable. Les `paths` actuels empêchent de rendre un check obligatoire sans adaptation, car les PR de documentation pourraient rester en attente indéfiniment.
- [ ] **Décision de publication** : contrôle final du propriétaire sur un SHA figé, accès corrects, revue des risques résiduels puis décision humaine explicite ; aucune publication automatique.

## Analyse complète de l'historique depuis Arch Linux / Proxmox LXC

À lancer dans le clone privé et avec `i0dev` (jamais dans GitHub Actions pour cet audit préparatoire). `gitleaks` est disponible dans le dépôt Arch `extra`. En cas de restriction Landlock déjà diagnostiquée :

```bash
sudo pacman -S --needed gitleaks --disable-sandbox-filesystem
cd ~/Projets/individual-zero
git fetch --all --tags --prune
mkdir -p artifacts/pre-publication
git rev-parse HEAD > artifacts/pre-publication/commit.txt
git branch -a > artifacts/pre-publication/branches.txt
gitleaks git --log-opts="--all" --redact=100 --report-format=json \
  --report-path=artifacts/pre-publication/gitleaks-history.json .
gitleaks dir --redact=100 --report-format=json \
  --report-path=artifacts/pre-publication/gitleaks-working-tree.json .
```

**Important :** un code de retour non nul indique potentiellement des secrets. Examiner les résultats sur le poste sécurisé. Même les rapports « expurgés » peuvent contenir noms de fichiers, chemins, commits ou autres éléments sensibles : **ne jamais les committer ou les coller tels quels dans une conversation publique**. `artifacts/` est ignoré par Git. Un scan sans alerte ne garantit pas l'absence de secrets inconnus ou des traces dans les logs GitHub.

Si `gitleaks` détecte des éléments, examiner, révoquer/remplacer les vrais secrets et choisir avec soin la stratégie d'historique (nettoyage contrôlé ou publication d'un dépôt propre). Ne pas forcer une réécriture destructive du dépôt de recherche sans sauvegarde et coordination.

## Règles GitHub proposées

Voir [Politique des accès et fusions](GITHUB_ACCESS_POLICY.md). Une Pull Request externe est une **proposition**, pas un droit de fusion. Les seuls développeurs ajoutés aux équipes autorisées pourront pousser dans le dépôt canonique ; seuls les mainteneurs désignés doivent pouvoir fusionner vers `main`.

Pour un dépôt GitHub Free **privé**, la protection/rulesets ne sont pas nécessairement accessibles ; pour un dépôt GitHub Free **public**, elles le deviennent selon les règles GitHub. Si l'exigence est que la protection soit active **avant même la première seconde de publication**, évaluer un plan payant permettant de la configurer pendant la phase privée.

**Décision actuelle : BLOQUÉ.** Aucun transfert, ajout de contributeur, changement de visibilité, acceptation Stage 9 ni campagne `held-out` ne découle de ce fichier.
