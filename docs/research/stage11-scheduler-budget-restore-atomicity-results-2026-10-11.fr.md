# Stage 11 : restauration atomique et canonique des compteurs UC du Scheduler

**Date : 11 octobre 2026.** **Nature : validation logicielle publique et déterministe, non held-out, non Golden, non scientifique.** Source normative exclusive : `docs/architecture/reference/en/mvp-specification-v1.2.1.md`, §§16.3, 17.2, 17.6 et 17.8, P-43, INV-21, DC-08, INV-33. La spécification normative est **inchangée**. **Stage 11 EN COURS ; Stage 9 NO-GO scientifique ; PR #25 ouverte, Draft, non fusionnée.**

## Chronologie vérifiable et défaut préalable

HEAD de départ de cet incrément : `2b6199c707a1dab748cec323673e3732b8ea8551` (dernières modifications documentaires du garde-fou de capacité Planning). La dernière campagne antérieure complète, [CI #38138214167](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38138214167), a obtenu **900/900 tests** sous Python 3.11 et 3.12 sur **`69a9037e90e0c3e7280331d695b51342c6e4d8a7`** ; elle ne constitue pas une preuve sur le présent correctif.

Le [protocole logiciel préalablement figé](stage11-scheduler-budget-restore-atomicity-protocol.en.md) a été enregistré au commit **`3976c8ce0fb8e69af7b566e502a471299087f4e2`**, **avant** toute modification du code et des tests. Il définit le défaut ciblé, les types et enveloppes acceptables, les cas négatifs et les limites de preuve, sans modifier les expériences scientifiques.

**Constat sur le code antérieur :** `CycleComputeBudget.charge()` imposait déjà le plafond total `B_cycle`, l'enveloppe par module et la capacité réservée aux modules de sécurité et de contrôle. En revanche, `restore_causal_state()` validait surtout les totaux, sans réappliquer la limite de chaque module ni la somme maximale des UC ordinaires. Une valeur `bool` pouvait également passer le test de type `isinstance(..., int)`, et une restauration à cycle `None` pouvait porter des compteurs incohérents. Un snapshot syntaxiquement valide mais causalement impossible pouvait alors contaminer la prochaine décision du Scheduler. Il s'agissait d'une **acceptation indue d'état restauré**, non d'une preuve de fuite du danger ou d'une dérive des budgets de campagne.

## Implémentation et tests

**Code :** commit `c5efceda6c78110a0a7337de71c666bbafc413c7`, fichier `src/lab/compute_budget.py`. Toutes les valeurs sont lues et vérifiées **avant** les trois affectations aux champs `_cycle`, `_consumed_cycle` et `_consumed_by_module` :
- jeu de clés strictement identique au schéma exporté, version de configuration correspondante ;
- cycle `None` avec total zéro et mapping vide, ou cycle `int >= 1` **exact** (ni booléen, ni fraction, ni texte) ;
- compteurs par module et total en entiers exacts non négatifs, clés de modules de type texte déclaré, sans nouveaux identifiants ;
- chaque module dans son enveloppe ; somme par module égale au total ; total sous `B_cycle` ;
- somme des dépenses des modules **non protégés** au plus égale à `B_cycle - protected_capacity`, sans réduire l'accès des modules protégés à leur propre réserve.

La correction ne modifie **aucun** montant P-43, la logique de `charge()`, `quote_operations()`, `open_cycle()`, les politiques de sécurité, les étapes cognitives, les expériences de dangers cachés, le journal ni `SnapshotManager`.

**Tests :** commit **`435fa15a81a54f6a407774a76834e4ef2c6627e7`**, quatre nouvelles méthodes dans `tests/test_compute_budget.py` :
1. **27 variantes invalides** d'un état normalement exporté : version/schéma, types de cycle, compteurs `bool/float/str`, valeurs négatives, mauvais mapping, clé inconnue/non textuelle, total incohérent, dépassement d'enveloppe, dépassement du plafond global et ponction de la réserve protégée. Chaque `ValueError` conserve exactement le contenu de `export_causal_state()`, les `canonical_causal_bytes` et les réponses de `quote_operations()`. Après ces rejets, une restauration et un débit légitimes fonctionnent.
2. **Restaurations positives indépendantes** : Scheduler non ouvert, ouvert sans dépense, coût nul avec clé UC explicite à zéro, dépenses ordinaires + protégées atteignant le plafond global et dépenses de contrôle exclusivement protégées. Les états et octets canoniques restent identiques, de même que le résultat du prochain débit.
3. **Intégration `SnapshotManager`** : capture périodique d'un vrai propriétaire `scheduler.compute_budget`, ouverture d'un cycle suivant, restauration de l'ancien état, vérification de la chaîne et des deux reçus `snapshot_taken` et `snapshot_restored`. Deux reproductions indépendantes ont les mêmes identifiants, octets de journal et hashes.
4. **Cas d'incompatibilité difficile** : un snapshot artificiel cryptographiquement valide contient 9 UC ordinaires d'une source dont la réserve vaut 1 ; on tente de restaurer dans un propriétaire dont la réserve vaut 3. La fixture réutilise **volontairement** le même identifiant de version, ce qui représente une violation synthétique de discipline de version. Le propriétaire et `SnapshotManager` rejettent la restauration : **pas de mutation des compteurs du destinataire, pas de reçu `snapshot_restored` fabriqué, chaîne technique et snapshot d'origine toujours vérifiables**. Ceci ne légitime pas le partage d'un identifiant de version entre configurations différentes.

Les fixtures sont des **cas unitaires logiciels synthétiques** ; elles ne constituent ni des observations physiques de danger ni des expériences comportementales ou scientifiques indépendantes.

## CI exécutée sur le SHA exact

| Contrôle | SHA du code et tests | Environnement | Tests | Résultat |
| --- | --- | --- | --- | --- |
| [CI courte #38138928648](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38138928648) | `435fa15a81a54f6a407774a76834e4ef2c6627e7` | **Python 3.12.15** | **904/904 PASS**, 103,793 s | **SUCCESS** |
| [CI complète #38139076290](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38139076290) | **même SHA** | **Python 3.11.17** | **904/904 PASS**, 121,138 s | **SUCCESS**, diagnostics terminés |
| [CI complète #38139076290](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38139076290) | **même SHA** | **Python 3.12.15** | **904/904 PASS**, 73,766 s | **SUCCESS**, diagnostics terminés |

Dans `ci-full`, les deux jobs complets ont réussi, aucune étape n'a échoué et **15 artefacts** de diagnostics et journaux de référence ont été conservés. Le job unitaire supplémentaire du workflow complet a été volontairement `skipped` par le mécanisme de contrôle des coûts : il n'est pas comptabilisé comme validation exécutée. L'exécution sur `main`, les campagnes Goldens historiques et les essais held-out restent des contrôles distincts.

## Portée, limites et prochaine priorité

**Démontré dans ces tests et la CI :** le Scheduler refuse les états restaurés impossibles vis-à-vis des enveloppes et de la réserve P-43, ne publie pas d'état partiel après rejet, préserve les octets de ses états légitimes, conserve les propriétés de `SnapshotManager`, n'efface aucun journal et laisse passer les régressions intégrées disponibles sous Python 3.11/3.12.

**Non démontré :** protection contre du code Python hostile modifiant des attributs privés, intégrité universelle d'un stockage externe, compatibilité de snapshots de configurations qui ne respectent pas leur version, adoption d'une meilleure politique d'Exploration, apprentissage du danger, récupération autonome, validité scientifique held-out ou acceptation Golden indépendante. Le changement ne résout **pas** le budget partagé au pas 5 : dans la configuration déjà analysée, l'individu conserve la commande de repli `attendre`.

**Verrou restant identifié par inspection statique, non corrigé dans cet incrément :** les frontières d'**entrée** `open_cycle(cycle)` et `charge(count)` utilisent encore une comparaison numérique permissive avant toute écriture. Un booléen ou une quantité fractionnaire peut, selon le cas, franchir cette validation ; toute correction devra être spécifiée et testée séparément, sans attribuer de coût gratuit ni modifier la sémantique des opérations P-43 existantes. Puis restent les scénarios Stage 11 de priorités besoins/exploration sur horizons plus longs, dangereux et à budget contraint.

### Reproduction exacte

Sur le **SHA de code/tests `435fa15a81a54f6a407774a76834e4ef2c6627e7`**, avec l'environnement du dépôt et Python 3.11 ou 3.12 :

```sh
python -m pip install -e .
python -m unittest discover -s tests -p 'test_compute_budget.py' -v
python -m unittest discover -s tests -p 'test_snapshots.py' -v
python -m unittest discover -s tests -p 'test_stage11_geographic_capacity_guard.py' -v
python -m unittest discover -s tests -q
```

L'ajout de ce **rapport documentaire post-CI** ne constitue pas une nouvelle version testée du code. **Stage 11 EN COURS ; Stage 9 NO-GO scientifique. PR #25 reste ouverte en Draft et non fusionnée. Aucun changement à `main`, aux protections ou à la spécification normative.**
