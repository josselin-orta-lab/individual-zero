# Stage 11 : première divergence de décision et arbitrage UC après danger caché transitoire

**11 octobre 2026. Recherche logicielle rétrospective PUBLIQUE : NON HELD-OUT, NON GOLDEN, NON SCIENTIFIQUE.** Source normative inchangée : `docs/architecture/reference/en/mvp-specification-v1.2.1.md`. **Stage 11 : EN COURS. Stage 9 : NO-GO scientifique. PR #25 : ouverte, Draft, non fusionnée.**

## Antériorité et historique vérifiable

La campagne initiale `stage11-transient-hidden-route-uc-snapshots-results-2026-10-11.fr.md`, protocole préalable `5ba46e53`, code/test `00619fecae037269b60b47cff0141a4e7019adc1`, [CI #38134913304](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38134913304) (**891/891 Python 3.12 PASS**), a **déjà observé** un résultat négatif : sous Planning/Exploration `(4,4)`, le témoin explore la branche sud au pas 5, mais l'individu exposé à une zone dangereuse inconnue (activée au pas 3, retirée au pas 5) exécute `attendre` malgré son retour au même carrefour. Le monde a enregistré **10 dommages** et l'intégrité finale est **90**. La sécurité canonique pour la zone reste `unknown`. Les limites et les SHA des huit variantes restent attachés au protocole original ; ils ne sont pas rétroactivement recalculés ni rebaptisés « held-out ».

La présente investigation est **explicitement postérieure** à cette observation. Son [protocole de traçage séparé](stage11-transient-route-first-divergence-protocol.en.md) a été fixé **avant** l'instrumentation, au commit `4a6982cc5e0ba4db9bbed1c72b406f2f84af7333`. Le protocole ne change pas le comportement et ne prétend pas être une prédiction scientifique préalable. Il demande d'inspecter uniquement les traces techniques déjà émises au **premier pas de décision différent, t=5**, dans deux copies indépendantes par variante, avec le **même calendrier** de snapshots périodiques après les pas 4 et 5.

Historique code/test et CI :
- `7b0c99aaf1b7096c70b5f13e272096f9e5e28585` : nouvelle sonde `src/lab/stage11_route_divergence_trace_probe.py`, en lecture seule côté Lab après la décision ;
- `2b574c0eb78219fa306550ab9243cff6bb3c04f9` : tests `tests/test_stage11_route_divergence_trace.py`, [CI #38135354491](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38135354491), **893/893 Python 3.12 PASS** (140,917 s). Les premières traces montrent le budget différé mais n'incluent pas son nom de champ `failed_operation` ;
- `e2e70ad6e7b54cbb812a86ee547ced14ede6f339` : correction **uniquement diagnostique** du champ `failed_operation`, plus lecture des `compute_charge` Planning déjà publiés au pas 5 ;
- **`6bfa9e7ecbbbb6d95b027714bbbbe2085400fff2`** : tests imposant la présence de ces éléments, [CI courte #38135597584](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38135597584), **893/893 Python 3.12.15 PASS** (131,628 s), bootstrap réussi ;
- [**CI complète #38135794852**](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38135794852), exactement sur **`6bfa9e7ecbbbb6d95b027714bbbbe2085400fff2`** : **893/893 tests Python 3.11.17 PASS** (120,544 s) et **893/893 tests Python 3.12.15 PASS** (135,890 s). Les deux jobs complets sont **SUCCESS**, **15 artefacts** de référence/diagnostic conservés, aucune étape en échec. Le job unitaire additionnel est volontairement `skipped`, non présenté comme une troisième validation.

**Aucun changement aux algorithmes Exploration, Planning, Gatekeeper, modulation ou Competition ; aucune modification de physique, seuils, enveloppes UC, Action Control, spécification normative ni source du danger caché.** Tous les changements de ce suivi sont des lectures Lab et des tests logiciels.

## Réexécution exacte et frontières causales

La sonde relance les deux variantes `(Planning, Exploration)=(4,4)` à partir de deux nouvelles naissances chacune. Le protocole et les événements externes sont identiques à la première matrice, ainsi que les deux snapshots après les pas **4 et 5**, sans restauration avant la fin des dix pas. Les **octets complets du journal** et les identifiants/hashes des snapshots reproduisent exactement les empreintes originales :
- Témoin, journal avant restauration : `97ce45cb83a16329442d4da94bdde4ecc8d7346c2bebb0ae5dca04a9d234ad41` ;
- Danger transitoire, journal avant restauration : `a93ef4d2326eea618be7a47a4db8ab7957c2678cd88fa07040fff15ff413fd6e`.

Les deux premières captures et les **quatre premières actions** sont identiques. La première différence d'action est **au pas 5**, après les 10 dommages subis au pas 3. Le danger extérieur a été retiré physiquement avant la capture du pas 5, sans être transformé en connaissance certaine de l'individu.

## Traces techniques observées au pas 5

| Mesure effectivement émise | Témoin | Monde avec danger caché apparu puis retiré |
| --- | --- | --- |
| Intégrité après les pas 3, 4 et 5 | 100 / 100 / 100 | **90 / 90 / 90** |
| Profil Global Modulation aux pas 3–5 | `normal` à chaque pas | `normal` à chaque pas |
| Transitions de modulation aux pas 3–5 | **0** | **0** |
| Référence du besoin `integrity` dans le S_t publié au pas 5 | Absente des références observées | **`need-alert:integrity:4:1` présente** |
| Propositions géographiques émises au pas 5 | **1**, cible sud (2,3) | **0** |
| Évaluations de cette proposition au pas 5 | **1** | **0** |
| Valeur intrinsèque de l'option sud | **0,7** | Non calculée pour une option absente |
| Poids P-15 effectivement journalisé | **0,75** | Pas d'option géographique évaluée |
| Accumulateur / seuil de Competition | **0,525 / 0,5**, franchissement | **0 franchissement géographique** |
| Commande appliquée au pas 5 | `se_deplacer` sud, option Exploration | `attendre` via option permanente `fallback` |

Le profil restant **normal** n'établit aucun déclenchement de préemption de menace ni de récupération autonome. Le choix `attendre` après dommage n'autorise pas à l'appeler un « repos de récupération ». Aucune admission d'un danger connu n'est revendiquée.

### Pourquoi l'option sud n'a pas atteint Competition

L'instrumentation corrigée montre, pour **chacun des cinq cycles cognitifs du pas 5** dans la variante exposée :

| Ordre | Opération Planning | UC demandées | Verdict |
| --- | --- | ---: | --- |
| 1 | `planning_build` antérieur au branchement géographique | **2** | Acceptées |
| 2 | `geographic_admissibility_preflight` | **1** | Acceptée |
| 3 | `planning_build` pour la cible géographique | **2** | **Refusées : `module_envelope`** |

L'enveloppe Planning est fixée à **4 UC par cycle**. Après 2+1 UC acceptées, il ne reste pas assez de budget pour la construction géographique de 2 UC. La raison émise cinq fois par `stage11_geographic_budget_deferred` est `incomplete_budget`, le champ `failed_operation` indique **`planning_build`**, et les propositions géographiques ne sont pas conservées. Les demandes refusées ne sont **pas** comptées comme UC consommées.

Dans le témoin, la trace du pas 5 contient seulement **1 UC de préconsultation** et **2 UC de construction** côté Planning ; la proposition géographique est publiée, évaluée et franchit le seuil de Competition. Cette différence de commandes s'explique **proximalement** par la différence de disponibilité du budget **pour cette option**, non par un veto technique d'Action Control ni un franchissement attesté du seuil de menace. La présence simultanée d'un besoin `integrity` et d'une première construction Planning de 2 UC est observée ; la chaîne de causes interne menant spécifiquement à cette première construction n'est pas isolée par une intervention indépendante, donc **aucune attribution causale scientifique** supplémentaire n'est faite.

Cette découverte ne justifie **ni** d'augmenter silencieusement les UC, **ni** de rendre gratuite la préconsultation canonique d'Action Control, **ni** de forcer le passage vers la branche sud. Le résultat négatif antérieur est inchangé.

## Empreintes du nouveau diagnostic rétrospectif

Sous `#38135597584`, le champ `evidence_sha256` versionné (avec charges Planning détaillées) vaut :
- Témoin : `9a075f37a8b92593ad6d46ae679a57f3a2540d885c3e38622c7240c439cb6091` ;
- Danger transitoire : `721e77c33b2da62a456eca443f734fa49ea906d86c2c06baf380a91d697c026a`.

Ces digests portent sur la **trace rétrospective**, pas sur les résultats initiaux à huit conditions. Les deux instances indépendantes de chaque variante produisent le même objet et les mêmes octets JSON. Le hash de journal pré-restauration, qui reproduit les huit-conditions précédentes, n'a pas été modifié par l'analyse.

## Portée de la preuve et prochaine étape

**Établi par ces tests :** non-interférence des décisions initiales vis-à-vis de la vérité future cachée dans cette fixture, caractère strictement borné des opérations UC, non-promotion de la disparition de danger dans le statut canonique, snapshots et journaux déterministes, et localisation d'une **suspension géographique pour indisponibilité de budget** au premier pas de divergence.

**Non démontré :** apprentissage autonome du danger, reconnaissance de sa disparition, politique optimale de sûreté, repos de récupération, arbitrage général de l'intégrité, sécurité sur cartes inconnues, planification arbitrairement longue, Golden historique scientifiquement accepté ou expérience scientifique held-out indépendante. **Stage 9 reste NO-GO scientifique. Stage 11 reste EN COURS.**

Prochaine question technique, **sans changer les résultats présents** : auditer l'identité de la première construction `planning_build` du pas 5 et évaluer, sous protocole logiciel séparé, si une prévision de capacité Planning peut empêcher une préconsultation géographique inutile sans jamais financer gratuitement l'admissibilité, supprimer une option de besoin prioritaire ni contourner Action Control. Si les budgets ne permettent légitimement pas les deux plans, conserver le choix négatif plutôt que d'imposer une exploration.

### Reproduction

À partir du SHA exact **`6bfa9e7ecbbbb6d95b027714bbbbe2085400fff2`**, avec le projet installé :

```sh
python -m unittest discover -s tests -p 'test_stage11_transient_hidden_route_uc_snapshots.py' -v
python -m unittest discover -s tests -p 'test_stage11_route_divergence_trace.py' -v
python -m lab.stage11_transient_hidden_route_probe
python -m lab.stage11_route_divergence_trace_probe
```

La première sonde produit **huit JSON**, la seconde **deux JSON**, toujours publics, sans claims scientifiques. Le seul SHA normatif reste `mvp-specification-v1.2.1.md` ; ses contenus n'ont pas été modifiés. Aucun merge de PR, aucun force-push, aucune écriture sur `main` et aucune modification des paramètres GitHub.
