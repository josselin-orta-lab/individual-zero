# Stage 11 : carrefour observé, impasse à plusieurs pas, résultat négatif

**Date :** 11 octobre 2026. **Nature :** développement logiciel public, non held-out, non scientifique. **Norme :** `docs/architecture/reference/en/mvp-specification-v1.2.1.md`. **Stage 9 : NO-GO scientifique inchangé.**

## Antériorité, source et campagne

- [Protocole enregistré avant l'implémentation](stage11-observed-junction-dead-end-protocol.en.md), commit `c7e36028460f6bff8a8d5030e0860a79d4b24941`.
- Sonde `src/lab/stage11_junction_probe.py`, version `stage11-public-observed-junction-dev-v1` ; tests `tests/test_stage11_junction_probe.py`.
- **Code vérifié :** `916ac9c912cc823f18eeef5813ccb86022f904b8`.
- [GitHub Actions #38116293389](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38116293389) : **786/786 tests Python 3.12 PASS**, test de démarrage PASS. La vérification complète sous Python 3.11 et les Goldens ne sont pas exécutés. Les tests comparent deux exécutions exactes de chaque variante, y compris le journal.

## Observations : dix pas physiques par variante

| Variante | Voisin sud réellement observé au départ | Captures Perception successives | Déplacements exploratoires appliqués | Retour au carrefour après l'impasse | Nouvelle branche sud après l'impasse |
| --- | --- | --- | ---: | --- | --- |
| `junction_open` | Passable | (2,2), (3,2), (4,2), puis (4,2) sept fois | 2 | Non | Non |
| `junction_sealed` | Bloqué | même trajectoire | 2 | Non | Non |

Dans les deux conditions, les étapes 3 à 10 exécutent `attendre` via l'option permanente, au point (4,2). Les trois positions comptées par Exploration correspondent exclusivement aux captures physiques. Aucune visite fictive de la branche sud ou du mouvement terminal non observé n'a été créditée.

**Interprétation :** l'agent conserve un registre de nouveauté géographique locale, mais ce comportement ne suffit pas à traverser des cases déjà visitées afin d'atteindre une cible informative connue plus loin. La seconde branche était réellement visible au point de départ de `junction_open`, mais ne constitue pas une destination explorée. Les tests de cohérence et de reproductibilité sont PASS ; la **capacité de désengagement de l'impasse est non démontrée**.

## Empreintes des sorties brutes CI

| Variante | SHA-256 d'entrée | SHA-256 du résultat | SHA-256 du journal | Tête du journal |
| --- | --- | --- | --- | --- |
| `junction_open` | `4a375c35a901584a5999218d92f96a468403ad4090ac1bafbb3ac25592b8539d` | `1aaaaa8efe36a3506836c2e57205d737040d28baa22ae536242cbda03038e81e` | `fcb8758139c996209c62a92537240244652efb544f9dbeebb4dcfabf8284ca8d` | `5508abfe68a7dae587e87a2c9b431d82e29ec7877e0180746168ad6a5050d538` |
| `junction_sealed` | `c21e9c992323ef36117d2da3b2afe535647e3e6e72c1751a788758b37ad3a096` | `93a447cf035457f7542becf7fd9b4681305399c8aae701590e4bfad209b591c7` | `d0dd427f41251fe680161b6c522a2a2f40de12023e643a8d915d31726b284b2e` | `644e04112145648ab7cbedf9840eedc6543214b8da43164dd628518ddaa25d07` |

## Reproduction minimale

```sh
python -m pip install -e .
python -m unittest tests.test_stage11_junction_probe -v
python -m lab.stage11_junction_probe
```

Conserver les deux objets JSON et leurs empreintes. Les conclusions ne s'appliquent qu'aux deux dispositions connues, à dix pas et à la version logicielle identifiée. Une future voie de retour par des sites connus exige sa propre version, ses propres coûts cognitifs, ses snapshots et un protocole préalable. Aucun mécanisme n'est considéré comme validé avant exécution.
