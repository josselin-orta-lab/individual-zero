# Individual Zero : contrôle de sécurité après publication

**Statut au 11 octobre 2026 : dépôt public, branche main protégée, audit historique incomplet.**

Le dépôt `josselin-orta-lab/individual-zero` est public. La publication a eu lieu ; le présent document ne certifie pas l'absence de secrets ou de données confidentielles dans les anciennes versions.

## Vérifications confirmées

- Le ruleset GitHub `Protect main` (ID 24874656) est actif et cible `main`.
- Il bloque les suppressions et les force pushes, exige une Pull Request pour les acteurs ordinaires et autorise la fusion squash.
- Aucune approbation n'est requise. L'administrateur du dépôt dispose d'un bypass permanent. Les discussions non résolues ne bloquent pas la fusion.
- Les autres branches ne sont pas protégées par ce ruleset.
- Les fichiers `SECURITY.md`, `CODEOWNERS` et les licences du code et des documents sont présents.
- Les workflows consultés ont des permissions GitHub en lecture seule et ne déclenchent pas `pull_request_target`.
- Plus de mille exécutions GitHub Actions figurent dans l'historique ; seuls certains journaux ont été examinés.
- Des métadonnées de commits déjà publics contiennent une adresse électronique personnelle.

## Contrôles non terminés

- [ ] Analyse exhaustive des anciens commits, branches, tags et objets Git avec un outil de détection de secrets.
- [ ] Examen des anciens journaux et artefacts GitHub Actions, notamment les traces des expériences.
- [ ] Contrôle des données expérimentales non destinées à être publiques, y compris les jeux de test indépendants.
- [ ] Examen manuel des collaborateurs, invitations et applications avec accès Write, Maintain ou Admin.
- [ ] Vérification des réglages de sécurité du compte, authentification à deux facteurs et email GitHub noreply.
- [ ] Validation des autorisations accordées aux Pull Requests extérieures et aux workflows.
- [ ] Compte rendu d'audit daté, sans divulgation de données sensibles.

## Procédure locale recommandée

Sur une machine privée disposant de Git, de Gitleaks et d'un clone complet, récupérer toutes les références et utiliser Gitleaks sur l'historique entier (`gitleaks git --log-opts="--all" --redact=100`). Inspecter les résultats sans diffuser ni committer les rapports bruts. Les journaux et artefacts GitHub doivent être inspectés séparément. Les données supprimées de l'historique accessible peuvent nécessiter d'autres archives.

Si un véritable secret est trouvé, le révoquer et le remplacer avant d'envisager toute modification historique du dépôt. Éviter une réécriture destructive sans sauvegarde et plan pour les forks.

## Limites de la vérification

La connexion GitHub ne permet pas l'inventaire administratif exhaustif des collaborateurs et applications. L'environnement local de cette session n'a pas d'accès réseau au dépôt et n'a pas pu exécuter le scan historique complet. Les éléments non vérifiés restent ouverts. Aucune preuve scientifique ni campagne held-out ne découle de ce contrôle.

Consulter [la politique d'accès](GITHUB_ACCESS_POLICY.md) pour les règles effectives.
