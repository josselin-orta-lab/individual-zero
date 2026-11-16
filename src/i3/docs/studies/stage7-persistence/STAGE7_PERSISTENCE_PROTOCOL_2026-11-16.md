# i3 Stage7: préenregistrement du gain de persistance héritable (16 novembre 2026)

**Statut initial : NO_LIVES_OPENED_BY_THIS_SOURCE_CHANGE / PROSPECTIVE_CONTRACT_PROPOSED.** La présente expérience est **nouvelle**, indépendante de l'étude du poids de curiosité Stage-6 du 15 novembre, conclue `STAGE6_LIGHT_NO_SIGN_CONCORDANCE` (9 signes positifs contre 7). **Aucun original, population, graine, parent ni contraste observé à Stage-6 ne sera réutilisé comme donnée prospective Stage7.** Les témoins externes réels sont facultatifs pour les expériences de laboratoire sous ADR-0022, sans revendication d'attestation indépendante ni promotion du moteur I3.

## Question scientifique falsifiable

La sélection des parents sur leurs **vies effectivement persistantes et corporellement financées**, suivie uniquement de transmission de génomes natifs v4 et de mutation, augmente-t-elle la **durée moyenne de vie réelle de la deuxième génération G2** relativement à des parents sélectionnés uniformément, sur des **mondes identiques dans chaque génération**, sans agir sur les décisions individuelles P1.3 funded-v2 ?

La génération G0 est commune aux deux bras. G1 et G2 comportent chacune `selected` et `random_parent`, 24 génomes par population et 6 opportunités F0 (stable/depletion/pulse × deux répétitions). **16 populations** sont l'unité statistique. Aucune vie, aucun individu, aucun contexte écologique ou aucun pas de simulation ne constitue une réplication indépendante supplémentaire. Le seul motif d'apprentissage hérité est le génome. Les souvenirs et le vécu de la génération précédente ne sont jamais copiés.

Les graines des mondes **changent entre générations**. En conséquence, une amélioration brute `G2 - G0` peut être due à des conditions écologiques différentes, pas à l'hérédité. Ce contraste sera donc affiché **descriptivement seulement**, jamais utilisé pour conclure.

## Critère primaire prospectif, décidé avant toute naissance

Pour chaque population `p` et chaque génération `g`, tous les génomes vivent sur les **six mêmes opportunités de mondes** pour les deux bras, avec les mêmes graines de vie fixées à l'avance. On calcule :

```
M[g, p, arm] = somme(steps_lived des 24 génomes × 6 mondes) / 144
D2[p] = M[2, p, selected] - M[2, p, random_parent]
```

L'horizon individuel est **400 pas**, avec aucune modification du traitement de la mort : un individu mort compte sa durée réelle observée, un survivant au pas 400 est **censuré à 400**, jamais considéré mort. Aucun remplacement ni nouveau tirage après décès, échec, censure ou résultat défavorable. Les deux bras payent exactement les mêmes contraintes natives de cognition à deux monnaies (énergie et vigilance).

**Succès du critère primaire : au moins 13 D2[p] strictement positifs sur 16, et une moyenne des 16 D2 positive.** Les zéros ne comptent jamais comme positifs. Direction positive **uniquement** : nous cherchons un gain de persistance, et non un déplacement de paramètre arbitraire. Le seuil de signes indépendant/équiprobable a une probabilité unilatérale nominale `697/65536 ≈ 1,064%` ; l'indépendance écologique des populations n'est pas considérée prouvée par les seules graines et le résultat est borné aux F0 de ce plan. Les effets par famille et les incertitudes d'estimation seront décrits, non utilisés pour autoriser un nouveau test.

**Rejet du critère :** moins de 13 populations strictement positives ou moyenne D2 non positive. La conclusion doit alors être `PERSISTENCE_G2_NO_REPRODUCIBLE_ADVANTAGE_F0`. Ce rejet ne prouve pas l'impossibilité d'un comportement adaptatif ou d'un effet hors F0.

## Résultats secondaires descriptifs, sans ajustement après observation

Publier pour chacun des 16 `p` :

- G0 commun : durée moyenne observée et part de vies encore présentes au pas 400 ;
- G1 et G2, sélectionné et aléatoire : durée moyenne et part au pas 400 ;
- `D1[p] = M[1,p,selected] - M[1,p,random_parent]` ;
- `D2[p] - D1[p]` (variation de l'avantage relatif de génération 1 à 2, **descriptive**) ;
- `G1-G0` et `G2-G0` pour chaque bras, **explicitement non causaux du fait de mondes différents** ;
- différence sélectionné − aléatoire en survie à l'horizon 400 en G2 ;
- écologies stable/depletion/pulse, décès, censures, défaites, valeurs nulles et causes terminales conservés intégralement.

Il n'existe **aucune correction automatique post hoc**, prolongement de G2, tri des mondes, modification de l'échelle de mutation ou remplacement de populations décevantes. Ne jamais dire « gain hérité entre G0 et G2 » à partir d'un simple changement brut de durée ; le témoin aléatoire apparié est indispensable.

## Sélection et hérédité verrouillées

Les méthodes de naissance, de scellement des générations, de sélection et de mutation sont **celles déjà testées du transport natif Stage6**, sous une nouvelle identité de source/protocole Stage7. Les parents du bras `selected` sont tirés au rang avec poids linéaires **24,23,…,1**, ordre imposé par `(nombre de vies encore présentes à 400, somme des pas vécus, numéro de slot)`, uniquement après scellement de tous leurs six originaux. Le témoin `random_parent` échantillonne uniformément **sans lire le moindre score de persistance**. Mutation `genome-v4` natif `scale=0.1`. Aucun souvenir appris ne franchit une génération. La règle motrice de chaque individu reste `reference P1.3 funded-v2`, sans action forcée.

## Chronologie à respecter / limites

Un seul workflow nouveau `i3-stage7-persistence-one-shot-20261116.yml`, déclenché **une seule fois après fusion sur main**, à une source Git HEAD propre et immuable. Il prépare une première planification d'ingénierie Python 3.11 et une seconde sous Python 3.12 avec graines **distinctes**, affectation d'un chemin d'archive fixé, empreintes du code, du protocole et de la décision ADR-0022, puis publie chaque plan **avant la première naissance**. Les deux répétitions doivent ensuite exécuter **11 520 vies réelles chacune**, neuf phases `G0/SEAL_G0/SELECT_G1/G1/SEAL_G1/SELECT_G2/G2/SEAL_G2/R_FINAL`, et publier chacune les originaux gzip complets (décès, censures, valeurs nulles), les empreintes des manifestes des trois générations et le reçu technique. Les résultats directionnels d'ingénierie sont cachés (seul leur SHA est conservé).

Le job scientifique reste bloqué par `needs: engineering` jusqu'à **deux succès complets**. Il vérifie les reçus **Stage7** (anciens reçus Stage6 rejetés), la source exacte, les 11 520 originaux et les neuf phases, génère une **troisième allocation distincte**, et publie le plan scientifique avant sa première naissance. Il exécute une seule cohorte native de **11 520 vies**, scelle et contrôle les originaux à chaque phase, vérifie les 1 536 tirages parentaux et 1 536 mutations héréditaires à partir des originaux avant de divulguer les 16 contrastes et le verdict.

Total maximal : **34 560 vies** (23 040 d'ingénierie + 11 520 de science), et **16 unités statistiques pour le test primaire**. Un arrêt de job, une corruption d'archive, un dépassement de quotas ou une erreur de provenance est un **défaut technique irréversible pour l'allocation consommée**, jamais un résultat négatif biologique. Aucun `rerun` GitHub d'une tentative consommée n'est autorisé.

**Représentativité et honnêteté.** Ce protocole peut établir au mieux un avantage de persistance *hérité des génomes sélectionnés* sur la famille de mondes P2 F0 utilisée, relativement au témoin aléatoire. Il ne démontre ni adaptation générale hors F0, ni indépendance écologique parfaite, ni plus-value de la réflexion, ni intelligence générale, ni mise en production. La chaîne d'archives est `INTERNAL_PROSPECTIVE_NOT_EXTERNALLY_ATTESTED`, avec I1 actif, I3 référence de développement et Stage 2.1 `NOT_ISSUED/HOLD_NO_VERDICT` inchangé.

## Statut à inscrire après exécution

L'état doit être observé **dans les vrais jobs et artefacts GitHub**, jamais deviné depuis un code ou un test unitaire. Conserver les empreintes exactes des trois plans publiés, des deux reçus techniques, des trois archives de vie et du résultat final, y compris s'il est négatif, avant toute interprétation.
