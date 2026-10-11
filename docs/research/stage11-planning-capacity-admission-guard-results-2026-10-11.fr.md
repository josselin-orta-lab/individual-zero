# Stage 11 : admission précoce de capacité Planning, sans calcul cognitif gratuit

**11 octobre 2026. Diagnostic logiciel public de développement, non held-out, non Golden et non scientifique.** Source normative exclusive et inchangée : `docs/architecture/reference/en/mvp-specification-v1.2.1.md`, notamment P-43, DC-07, INV-08, §8.11, §14 et §17.6. **Stage 11 EN COURS ; Stage 9 NO-GO scientifique ; PR #25 ouverte en Draft, non fusionnée.**

## Protocole préalable et historique source

- État antérieur documentaire : `3f32fd9afa6373d1536c0baf186d280942a79bdd` ; campagne technique négative et diagnostic post-résultat de concurrence des UC au pas 5, validés à `6bfa9e7ecbbbb6d95b027714bbbbe2085400fff2` dans [CI #38135794852](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38135794852), **893/893 Python 3.11 et 893/893 Python 3.12 PASS**. Ce résultat négatif historique demeure indépendant et inchangé.
- [Protocole d'optimisation enregistré **avant** modification du code](stage11-planning-capacity-admission-guard-protocol.en.md) : commit `d7af5ac88276bb1c7833998d944bf29dd643a958`. Il s'agit d'un **nouveau test logiciel déclaré prospectivement**, pas d'un protocole scientifique.
- `53e8e88cbb229c940c313c4af68f84f05b61bb07` : `src/lab/compute_budget.py`, nouvelle interrogation pure de capacité `quote_operations` ;
- `c8b96d8dbfcf6125318c809e75b8963dfd6ed27f` : garde-fou Stage 11 strictement optionnel ;
- `69ae304909121503176aa997697e1dd1c74c227c` : activation explicite et versionnée dans la fixture de carrefour public ;
- `96e655447ff9d877191ce42a3ae229118a6c56d4`, puis `f80dee985e5b856d78067becec6fb8b1f6ed6154` : sonde A/B et suppression d'une fonction utilitaire inutilisée, sans changement de mécanisme cognitif ;
- `86c44a87b998efff3588c2a02fc82a12770aac5f` : trois contrôles sur l'admission UC du Scheduler ;
- `fa17694076c8725d8d6dce1218b8c64fd73c7a7a` : quatre tests de Stage 11, [CI courte #38137986526](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38137986526) : **900/900** Python **3.12.15** PASS, en **141,686 s**, smoke bootstrap PASS ;
- `d64643c881f139de5be6d1e9900e9504ee61fd6a` et **`69a9037e90e0c3e7280331d695b51342c6e4d8a7`** : interdiction explicite d'activer le garde-fou avec le mode de préconsultation *eager* sans frontière et test associé. SHA exact du code et des tests de la campagne complète.

**Campagne définitive :** [CI complète #38138214167](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38138214167), sur le SHA **`69a9037e90e0c3e7280331d695b51342c6e4d8a7`** : **900/900 tests Python 3.11.17 PASS en 126,023 s**, **900/900 tests Python 3.12.15 PASS en 75,592 s**. Les **deux jobs complets sont SUCCESS**, aucun échec d'étape, **15 artefacts** de diagnostic/référence conservés. Le job unitaire séparé de cette campagne est `skipped` par le contrôle de coût et n'est pas compté comme troisième validation. Les diagnostics Stage 9 produits ne remplacent ni un Golden indépendant ni une campagne scientifique held-out.

## Correction exactement introduite

`CycleComputeBudget.quote_operations(module, operations)` est une **lecture sans mutation** des compteurs UC détenus par le Scheduler. Il calcule à partir des coûts de campagne existants si une séquence nommée est finançable compte tenu de l'enveloppe module, du plafond de cycle et de la capacité protégée. Il ne réserve ni ne consomme aucune UC, n'appelle aucun service cognitif, ne prédit aucune action et n'interroge pas Action Control. Les demandes effectives restent soumises à `charge()`. Les tests dédiés comparent état du Scheduler, devis et charges indépendantes, ainsi que les refus sur entrées malformées ou cycle non ouvert.

`Stage11Config.geographic_capacity_guard_enabled=False` est **désactivé par défaut**, avec un identifiant de version et de budget propre lorsqu'il est activé. L'activation exige une géographie optionnelle, une préconsultation canonique payante et un accès borné par l'existence d'une frontière observée. Le mode historique de préconsultation *eager* est incompatible avec l'opt-in. Aucun historique antérieur n'est « migré » automatiquement.

Le garde-fou intervient en **Phase 1 Planning**, après la tentative normale du plan lié au besoin ou but, et après toute recherche de route réellement financée, **avant** la préconsultation géographique. Pour une cible courante issue d'une capture physique antérieure, il examine le coût fixe `geographic_admissibility_preflight=1 UC` + `planning_build=2 UC`. Si au moins 3 UC restent réellement finançables, **aucune opération n'est sautée** : les deux charges ordinaires et le contrôle final d'Action Control demeurent nécessaires. Si cette somme n'est pas finançable, seule l'offre géographique locale est retirée ; la trace `stage11_geographic_capacity_deferred` déclare le coût demandé, la capacité disponible, **zéro UC facturée pour le devis**, `canonical_admissibility_consulted=False`, `safety_decision=null` et `no_new_option=True`. Elle ne falsifie ni une `compute_charge` refusée, ni une décision de sécurité, ni un plan réussi. La construction antérieure de Planning pour le besoin conserve sa priorité.

**Important :** une simple lecture de compteur du Scheduler est un contrôle d'admission infrastructurel, pas une simulation, une recherche exploratoire ou un raisonnement gratuit. La réduction réelle des charges UC peut modifier la fatigue cognitive ultérieure ; les trajectoires A/B ne sont donc pas forcées à être identiques, et leurs identifiants techniques restent distincts par version.

## Résultats reproductibles de la sonde publique

Sonde : `src/lab/stage11_geographic_capacity_guard_probe.py` ; tests : `tests/test_stage11_geographic_capacity_guard.py` et `tests/test_compute_budget.py`. Même couloir public `junction_open`, mêmes injections physiques journalisées au pas 3 puis au pas 5, mêmes 10 étapes du monde et **snapshots complets après les pas 4 et 5**. Chaque condition de test est exécutée deux fois à partir d'individus indépendants, avec même calendrier de snapshots et deux restaurations **après** les dix pas. Les octets canoniques du journal, les états propriétaires, les identifiants/hashes des snapshots et l'objet de diagnostic sont identiques entre les deux exécutions d'une même configuration versionnée.

| Variante | Planning/Exploration | Garde-fou | Action au pas 5 | Préconsultations payées au pas 5 | Rejets de construction géographique au pas 5 | Verdict physique sur dix pas |
| --- | --- | --- | --- | ---: | ---: | --- |
| Témoin | 4/4 | NON | mouvement sud | 1 | 0 | carrefour et branche sud atteints |
| Témoin | 4/4 | OUI | mouvement sud | 1 | 0 | même trajet physique |
| Danger caché transitoire | 4/4 | NON | `attendre` fallback | **5** | **5** | retour au carrefour, pas de branche sud |
| Danger caché transitoire | 4/4 | OUI | `attendre` fallback | **0** | **0** | même trajet physique, aucune prétention à un repos autonome |
| Témoin | 3/4 | OUI | `attendre` fallback | **0** | **0** | impasse persistante |
| Témoin | 0/0 | OUI | `attendre` fallback | **0** | **0** | stationnaire |

**Cas critique 4/4 avec danger caché, pas 5 :** les cinq cycles commencent par `planning_build` lié au but/besoin, charge **2 UC acceptée**. Le devis infrastructurel constate qu'il faut **3 UC** pour consulter Action Control puis construire l'option géographique, mais **2 UC seulement** restent dans l'enveloppe Planning de **4 UC**. Les cinq événements de report portent `required_uc=3`, `available_uc=2`, `charged_uc=0`, aucun statut de sécurité ni résultat de simulation. Cela supprime **5 UC de préconsultations** auparavant réellement dépensées lors de ce pas et cinq demandes de construction de 2 UC auparavant rejetées et non consommées. Les charges liées au besoin sont conservées. Le monde a toujours infligé 10 dommages dans cette variante ; l'intégrité reste 90 et la disparition extérieure du danger n'est pas devenue connaissance canonique.

**Cas 3/4 :** la recherche réelle de route `geographic_route_search=1 UC` reste payée, puis l'admission constate à nouveau 3 UC nécessaires pour 2 disponibles. Aucun transit gratuit, aucune préconsultation inutile et aucune récompense fictive ne sont créés. **Cas 0/0 :** aucun moyen d'exécuter Planning ; le garde-fou ne crée aucun travail de remplacement.

**Absence de régression dans la configuration par défaut :** les deux journaux des dix pas plus snapshots, **avant restauration**, reproduisent exactement les SHA-256 du diagnostic de danger transitoire `#38134913304` et de la trace `#38135794852` :
- témoin 4/4 : `97ce45cb83a16329442d4da94bdde4ecc8d7346c2bebb0ae5dca04a9d234ad41` ;
- danger caché 4/4 : `a93ef4d2326eea618be7a47a4db8ab7957c2678cd88fa07040fff15ff413fd6e`.

L'opt-in a **un autre** manifeste de configuration, un autre journal et des hashes de snapshots distincts, intentionnellement. Sous SHA de code `69a9037`, les empreintes de diagnostics avec garde-fou mesurées dans les logs Python 3.12 complets sont :

| Configuration opt-in | Journal SHA-256 avant restauration | Evidence SHA-256 |
| --- | --- | --- |
| 4/4 témoin | `9882f1ee3ae90aaf635545053539d01adf810d94cc6c6edfbfaa6bc2e5241acf` | `f45d8072bd8503c7d209c2a01e6d9c5ffa18d69cacb9ac637936e1c578d6d0c4` |
| 4/4 danger caché | `646d946405c96f8b7dded65d01b617827dbb40df4f8bcd699417925270f80e33` | `9e4cdbedb55e4724e9e2c02ab1d1932c2a2ec95de4d86f76081a0b80879e6b41` |
| 3/4 témoin | `b816b70b0e21bb52e554aa4625b1c5c2a7cb5eb7394265032e213c52b6cfe37b` | `72b1aa9a7bf0a5b7aa326719fd26c6c60f9abde7d106ff1ccf4b9c1d89b963a4` |
| 0/0 témoin | `6ed73e9405f5f4995486b9fe2e56d8a32c62898df124289fbe7a3f12d070932e` | `c4024effd08fd45104bf81f8302f629b2c247f33cbf1f14c7fb3025bc77374a2` |

Les deux snapshots périodiques par trajectoire sont vérifiés puis restaurés intégralement. Les restaurations ajoutent leurs propres événements au journal append-only : l'empreinte après restauration est légitimement différente de celle d'avant. Les comparaisons byte-à-byte indépendantes reproduisent exactement **les mêmes** points de capture, dans le même ordre, pour une même configuration.

## Limites, discipline de preuve et prochaine priorité

**Démontré logiciellement :** interrogation atomique non consommatrice du Scheduler ; absence de réservations ou faux refus ; préconsultation et construction réelles toujours facturées lorsque finançables ; conservation des priorités de besoin ; rejet du mode eager incompatible ; snapshots exacts ; absence de crédit à une visite jamais perçue ; replay canonique et rétrocompatibilité byte-identique du mode désactivé dans les cas mesurés.

**Non démontré :** arbitrage optimal entre intégrité et exploration, levée de l'impasse sous budget 3/4, apprentissage de danger inconnu, connaissance de la disparition du danger, récupération autonome, comportement sur des environnements cachés nouveaux, longévité arbitraire, validité scientifique held-out ou acceptation Golden indépendante. Le garde-fou n'est **pas** présenté comme une correction de sécurité. Il économise des UC, mais ne force ni connaissance ni comportement.

Prochaine investigation technique indépendante : auditer la robustesse de `CycleComputeBudget.restore_causal_state` face à des états invalides (plafonds de modules, capacité protégée, types booléens et incohérences de cycle), puis poursuivre la matrice comportementale Stage 11 sur horizons prolongés et priorités de besoins sans modifier arbitrairement P-43. Avant toute nouvelle expérience, séparer son protocole et les SHA déjà validés.

### Reproduction

Depuis le **SHA exact de code/tests** `69a9037e90e0c3e7280331d695b51342c6e4d8a7`, dans un environnement Python 3.11 ou 3.12 compatible avec le dépôt :

```sh
python -m pip install -e .
python -m unittest discover -s tests -p 'test_compute_budget.py' -v
python -m unittest discover -s tests -p 'test_stage11_geographic_capacity_guard.py' -v
python -m lab.stage11_geographic_capacity_guard_probe
python -m unittest discover -s tests -q
```

La sonde imprime huit combinaisons A/B déclarées, tandis que les tests exhaustifs utilisent la sous-matrice explicitement fixée au protocole et capturent les journaux. Les résultats CI 3.11/3.12 et les 15 artefacts peuvent être consultés dans [#38138214167](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38138214167).

**Stage 11 EN COURS ; Stage 9 scientifique NO-GO. Aucun changement de `main`, aucun merge, aucune permission GitHub ou protection modifiée, aucun changement de la spécification normative anglaise v1.2.1.**
