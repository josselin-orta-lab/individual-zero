# Reproduction hors ligne du pilote A1-P H48 (31 octobre 2026)

**Portée strictement historique, descriptive et non confirmatoire.** Le script `tools/research/i1_a1p_h48_reproduce.py` verrouille les 8 ZIP originaux du run [40938021102](https://github.com/josselin-orta-lab/individual-zero/actions/runs/40938021102), code de naissance `012ece9eb0b4531f714bd69af439eeb38d7bf701`, et le capsule de rejeu `I1_A1P_H48_FIRST_PAID_Q_SENSITIVITY_2026-10-31.zip` (SHA-256 `cbe306707c724b0a4c43b628076980d96f4d088092d1bb35e282c0bbf5bada2d`). Les ZIP originaux et le capsule ne sont PAS importés dans le dépôt et doivent être conservés et fournis séparément. Aucun téléchargement automatique, aucune naissance, aucune commande I1 et aucun changement de paramètres. Ne pas utiliser ce résultat pour promouvoir L3.

## Invocation (Python, hors réseau)

Placer les huit ZIP originaux dans un même dossier, sans les extraire, et fournir le capsule séparément :

```sh
python tools/research/i1_a1p_h48_reproduce.py --capsule /chemin/I1_A1P_H48_FIRST_PAID_Q_SENSITIVITY_2026-10-31.zip --originals /chemin/archives-a1
```

Le code contrôle les huit SHA-256 originaux et le SHA-256 du capsule AVANT d'extraire le code d'analyse dans un répertoire temporaire. Il refuse les noms inattendus, doublons, archives imbriquées, liens symboliques et fichiers dépassant les tailles bornées. Ensuite, les **39 tests adversariaux** sont exécutés et le résultat du rejeu du premier cycle payé est vérifié : 188 TD, 14 lectures Q post-crédit, un cas arithmétique de seuil sensible à Q. En cas d'archive manquante, modifiée ou d'échec de rejeu, arrêt sans promotion scientifique. `--verify-only` ne lance pas les tests.

**Résultat local de validation du 31/10/2026** : les huit ZIP historiques accessibles dans la session ont concordé avec les empreintes, puis les 39 tests et le rejeu ont réussi (Python 3.13.5). Les quatre tests synthétiques du garde ont réussi également. La CI GitHub de la PR ne doit lancer que ces quatre tests synthétiques : jamais télécharger ou réexécuter les huit vies.

## Limites et décision

Le capsule est un artefact historique externe figé dont la conservation à long terme **n'est pas assurée par ce dépôt**. Le reproducteur n'établit ni un contrefactuel moteur complet, ni un bénéfice adaptatif, ni la représentativité de la physiologie v4. Les ZIP historiques devaient rester séparés ; aucune nouvelle étude prospective ne découle de cet outil. A1-C `NO_GO`, A2-R `NOT_EXECUTED` (0/96), L3 général `NOT_ESTABLISHED`.
