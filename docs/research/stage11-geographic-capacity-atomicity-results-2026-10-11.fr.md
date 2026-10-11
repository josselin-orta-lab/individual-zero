# Stage 11 : saturation de la mémoire géographique et refus atomique

**Date :** 11 octobre 2026 (Europe/Paris). **Nature :** diagnostic public de développement logiciel, non held-out. **Aucun verdict scientifique.**

## Protocole et code vérifié

- [Protocole déclaré avant les modifications et les résultats](stage11-geographic-capacity-atomicity-protocol.en.md).
- **Commit de code réellement validé :** `92886c2a83dd45b8283cbbbabdaa10c532bbf80e`.
- [GitHub Actions #38122153134](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38122153134) : **843 tests unitaires réussis sur Python 3.12**, et smoke `individual-zero --cycles 3 --seed 0` réussi.
- Reproduction : `python -m lab.stage11_routed_capacity_probe`.
- Protocole technique : `stage11-public-routed-capacity-dev-v1` ; identifiant de budget pour le mode route activé : `+route-site-cap-stop-v1`.
- Runtimes indépendants dans le même couloir/jonction public `junction_open`, démarrant en `(2,2)`, corps de référence, physique et Equipment inchangés, `observe_routes=True` et `refresh_surveys=True`. **Dix pas de monde** par configuration, limite de sites distincts fixée à **3** ou **4**.
- Les protocoles publics existants dépendant du routage sont maintenant identifiés en v2 et leurs anciens résultats restent rattachés à leurs anciens commits sources. Aucune modification rétroactive des empreintes historiques.

**Attention aux commits ultérieurs :** ce succès s'applique strictement au SHA testé ci-dessus. Tout changement de code postérieur sur la branche, notamment au mécanisme de restauration des snapshots, exige sa propre validation. Le simple succès d'une CI antérieure ne constitue pas une attestation de toute la tête de branche future.

## Résultats physiques et coût logique

| Mesure | Limite 3 sites | Limite 4 sites |
| --- | ---: | ---: |
| Sites distincts effectivement perçus | **3** | **4** |
| Sites distincts du propriétaire Exploration | 3 | 4 |
| Déplacements géographiques réellement appliqués | 2 | 5 |
| Transits de retour effectivement appliqués | 0 | 2 |
| UC acceptées pour `geographic_route_search` au total | 0 | 5 |
| UC acceptées pour les routes après saturation | **0** | **0** |
| Recherches de route après saturation | **0** | **0** |
| Découverte physique de l'alternative sud | Non | Oui |

**Captures Perception successives, limite 3 :**
`(2,2), (3,2), (4,2), (4,2), (4,2), (4,2), (4,2), (4,2), (4,2), (4,2)`.

**Captures Perception successives, limite 4 :**
`(2,2), (3,2), (4,2), (3,2), (2,2), (2,3), (2,3), (2,3), (2,3), (2,3)`.

Au plafond de 3 sites, la saturation commence au **pas physique 3** et se poursuit jusqu'au pas 10 ; les diagnostics bornés `stage11_geographic_route_capacity_exhausted` sont enregistrés sur les pas 3 à 10. Au plafond de 4 sites, la quatrième position `(2,3)` est capturée au **pas 6** ; les diagnostics sont enregistrés aux pas 6 à 10. Ces diagnostics sont produits au maximum une fois par pas physique lorsque le cycle de Planning correspondant existe.

La limite à trois sites arrête toute nouvelle recherche de transit vers une destination encore inconnue, qui ne pourrait pas devenir une nouvelle visite comptabilisée. Avec quatre sites autorisés, deux transits par des lieux déjà physiquement visités précèdent la visite attestée de la branche sud. Aucun mouvement non observé n'est ajouté au registre.

## Refus atomique du propriétaire Exploration

Un test unitaire **synthétique** construit deux sites déjà capturés, deux relevés physiques simulés et un transit fondé sur une frontière préalablement observée. Lorsqu'une troisième position distincte est présentée à un registre limité à deux, `observe_capture` lève `ValueError` **avant de supprimer le transit offert**. L'export complet `export_causal_state()` reste strictement identique avant/après l'exception. Revoir le même site déjà connu reste idempotent.

C'est une garantie d'atomicité de **l'état du propriétaire**. Ce n'est ni une preuve que le monde physique n'aurait pas déplacé l'individu, ni une stratégie générale de récupération lorsqu'un événement externe le pousse hors capacité.

## Empreintes reproductibles du code testé

| Limite | SHA-256 des entrées | SHA-256 du résultat canonique | Tête du journal |
| --- | --- | --- | --- |
| 3 sites | `c00bae4d207ebe8e4338f6b2a62fe8dd80077c3ba6632067bf70c4be05c924a5` | `44d003c12abeda4606e954addbfb43a30ed8b913ecec80219c5d748eed7978bd` | `4fb253c6dc66f543ae839d95401dfcfbf244f0d7db156b8fada563022fb7dddd` |
| 4 sites | `5ec8d2499611889c6fb1fc95909641d5da6796feef822ec038654549848c79c2` | `0b3458e72e675f94138ba3ce2f60cb596b4cda0cf64a0d4575854f99b492d1bc` | `9aa9cd43a20abf01771bb0b459e453ebc800d423cceec727fe48255679cf3f91` |

Les empreintes des états Exploration sont `98bd9ee4922000018150eeebec75cb6b2f52791670b7fbc883680df3c5288552` (limite 3) et `1571c5143aad1564413eb8cbda081667c267aba3f28884683292f94413d6dcc4` (limite 4). Les journaux sont vérifiés avec `journal.verify()` et les tests exigent l'égalité exacte de deux exécutions indépendantes pour chaque capacité.

## Limites et prochaines vérifications

- Un propriétaire de mémoire à capacité saturée rejette correctement une nouvelle capture inenregistrable ; la récupération du **runtime entier** après un déplacement externe inattendu reste à concevoir sans falsifier la capture ni effacer des faits.
- La suppression des transits concerne uniquement l'objectif informationnel géographique devenu impossible dans un registre complet ; elle n'empêche pas des déplacements autorisés par d'autres motifs.
- Les relevés actualisés n'établissent ni la sécurité d'une case auparavant inconnue, ni la validité permanente d'une route. Les changements de faits de sécurité canoniques, les échecs de rafraîchissement et les grandes trajectoires demandent des contrôles indépendants.
- La suite complète des Goldens, Python 3.11 et l'acceptation scientifique restent hors du périmètre de cette campagne.

**Stage 11 : EN COURS. Stage 9 : SCIENTIFIC VALIDATION PENDING / NO-GO. La PR #25 doit rester en brouillon et non fusionnée.**
