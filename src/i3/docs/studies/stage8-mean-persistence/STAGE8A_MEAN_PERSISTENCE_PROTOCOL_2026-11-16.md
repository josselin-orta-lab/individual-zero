# Individual Zero · Stage8-A · validation prospective de l'avantage MOYEN de persistance

**Préenregistrement du 16 novembre 2026, avant toute naissance Stage8-A.** Ce protocole est une expérience distincte de Stage7, avec nouvelles racines de graines, nouvelles populations et critère **défini sans utiliser la nouvelle cohorte**. Les chiffres Stage7 sont des *données historiques utilisées pour dimensionner*, non une réplication de validation. Source réelle, allocation, artefacts et statut de la campagne seront consignés après exécution, jamais déduits de ce document.

## Décision scientifique de départ

Stage7 (run unique [#43830174125](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43830174125)) a terminé **12 contrastes G2 positifs sur 16**, seuil prospectif **13/16 non atteint** ; résultat `PERSISTENCE_G2_NO_REPRODUCIBLE_ADVANTAGE_F0`, `CLOSED_NO_RETRY`. Le contraste moyen était **+11,9036458 pas** et l'écart-type entre populations ≈20,6808 pas. Ce résultat **ne devient pas positif** si Stage8 confirme une autre hypothèse.

**Question Stage8-A :** la sélection des parents sur leur persistance corporelle effectivement financée augmente-t-elle **la moyenne entre populations de la durée vécue par leurs descendants G2**, relativement à des parents tirés uniformément au hasard, même si certaines lignées évoluent défavorablement ?

## Design et unité de réplication

- **32 nouvelles populations** disjointes, réparties en **deux panneaux de 16** dont les racines, seeds, génomes et 288 occasions World chacun sont générés avec une nouvelle racine OS de 256 bits et un domaine HMAC explicitement Stage8. Le code natif du transport Stage7 est utilisé **uniquement comme générateur technique de vies**, jamais comme autorité sur le nouveau verdict. Chaque panneau possède ses propres archives, neuf phases G/S/R et SHA de source.
- **24 génomes fondateurs par population** ; G0 est vécu une seule fois et partagé entre les deux branches. En G1 et G2, deux lignées : `selected` (parents choisis selon les scores de persistance **après scellement** : censure au pas 400, somme des pas, slot, poids de rang 24 à 1), et `random_parent` (parents uniformément tirés, **sans lire les scores**). Descendance par mutation génomique native v4 échelle 0,1, sans transfert de mémoire ni récompense imposée.
- **Six occasions de World** par individu et génération (stable/depletion/pulse × deux répétitions), mêmes conditions et graines au sein d'une population entre `selected` et `random_parent` **à la même génération**. Le même moteur individuel `P1.3 funded-v2`, ses deux monnaies énergie/vigilance, et la politique motrice de référence sont conservés. Horizon 400 ; mort au temps réel, survie au maximum censurée et conservée. Les World changent entre générations, donc **les différences brutes G0→G1→G2 ne sont pas des effets causaux**.
- Le plan source/owner/méthode/graines/chemins SHA est entièrement **publié avant la première naissance** de chaque exécution. Les deux branches utilisent des flux PRNG propres et préalloués, mais **n'ont pas de randomisation explicite indépendante de leurs étiquettes** ; ce point limite l'interprétation causale, même avec fondateurs et Worlds appariés.

## Hypothèse et unique critère primaire FIXÉS avant exposition

Pour chaque population `p=0..31`, les 24 génomes G2 du bras sont évalués sur six mondes chacun (144 vies). Définir :

```
M[p,arm] = somme_{slot=0..23, family,repeat} steps_lived(G2,p,arm) / 144
D[p] = M[p,selected] - M[p,random_parent]
mean_D = sum(D[p] for p=0..31) / 32
sample_sd = sqrt(sum((D[p]-mean_D)^2 for p=0..31)/31)
L_97_5 = mean_D - 2.0395134463964077 * sample_sd / sqrt(32)
```

`2.0395134463964077` est la **valeur critique de Student à 31 degrés de liberté pour un test unilatéral α=0,025**, une borne inférieure unilatérale à 97,5 %, choisie avant toute vie.

**Succès du critère principal**, `STAGE8A_MEAN_PERSISTENCE_ADVANTAGE_F0`, **si et seulement si** `sample_sd > 0`, `mean_D > 0` et `L_97_5 > 0`. Sinon `STAGE8A_MEAN_ADVANTAGE_NOT_DEMONSTRATED_F0`. Aucune exigence d'un nombre minimal de populations positives : toutes les lignées comptent dans la moyenne, y compris celles avec résultats négatifs ou nuls. Les 32 populations sont les **seules** unités statistiques. Le test n'est interprétable qu'avec l'hypothèse de populations suffisamment indépendantes et la justification de l'approximation de Student ; ces conditions ne sont pas prouvées par la seule séparation des racines. Une variance nulle ne déclenche jamais un GO automatique.

Les résultats négatifs, manquants, écologiques, censurés et les erreurs techniques restent publiés. Un échec de journal d'archive, de source, de phase, de SHA, de mutation ou de parenté rend le résultat **TECHNICAL_NO_VERDICT**, non négatif biologique, sans rerun de l'allocation.

## Effectif et puissance, documentés AVANT la première vie

Le choix **n=32** part du signal historique Stage7 (écart-type ≈20,68), mais ne garantit pas sa reproductibilité. **Approximation NORMALE de la puissance** d'un test t unilatéral α=0,025 (pas une simulation empirique ni une garantie) :

| Effet réel hypothétique | SD entre populations | Puissance normale approximative |
|---:|---:|---:|
| +12 pas | 20,68 pas | 89 % |
| +8 pas | 20,68 pas | 56 % |
| +6 pas | 20,68 pas | 35 % |
| +12 pas | 30 pas | 59 % |
| +8 pas | 30 pas | 30 % |
| +6 pas | 30 pas | 18 % |

Pour n=32, une bande t bilatérale à 95 % aurait une demi-largeur indicative ≈7,46 pas à SD=20,68. Cette précision est **conditionnelle** : si la dispersion réelle est plus grande ou les populations corrélées, l'étude est moins puissante. Un résultat nul/négatif ne prouve pas l'absence d'un petit effet. **Aucune adaptation de n en fonction de vies nouvelles n'est autorisée.**

## Secondaires EXPLORATOIRES seulement

Rapporter les **32 différences individuelles** sans supprimer de négatifs, la médiane, l'écart-type, les comptes +/−/0, les durées G0/G1/G2 par branche, les parts censurées à 400, l'avantage G1, les effets par famille F0 et le nombre de parents distincts dans chaque branche, notamment les possibles goulets génétiques. Aucun secondaire ne peut remplacer `L_97_5`. Pas de sélection post hoc d'un groupe de mondes, d'un gène ou d'une génération alternative. Les questions distinctes Stage8-B (interaction écologie) et Stage8-C (diversité génétique) ne sont **pas** validées par Stage8-A.

## Transport, custody et admission

Une exécution native complète = 2 panneaux × (2 304 G0 + 4 608 G1 + 4 608 G2) = **23 040 vies réelles**, 576 occasions World, **3 072 tirages parentaux + 3 072 mutations**, et 18 phases (9 par panneau). Le workflow one-shot de Stage8-A :
1. CI logiciel Python 3.11 et 3.12, vérification source Git clean, régime P1.3, congélation du présent protocole, des contrôles, de la racine et de la règle `L_97_5`.
2. Deux répétitions **complètes** d'ingénierie, Python 3.11 et 3.12, chacune **23 040 vies** sur une racine distincte, plan archivé pré-exposition, archives gzip et 18 phases scellées, reçus source-exacts avant science. Les sorties de tendance et d'effet des répétitions techniques ne sont pas publiées ; seul le transport est audité.
3. Seulement si **les deux** répétitions sont complètes, une **nouvelle** troisième allocation de 23 040 vies scientifiques, avec son plan distinct et ses deux reçus publiés avant naissance, puis réduction moyenne finale, publication des 32 contrastes même négatifs et des originaux.

**Total maximum : 69 120 vies natives réparties sur 3 campagnes, 32 unités d'inférence en science.** Une interruption, timeout ou archive incomplète est un défaut technique irréversible pour l'allocation, jamais une raison de changer de répertoire ou de relancer les mêmes graines. Les archives GitHub sont soumises aux limites de stockage et à une rétention provisoire (90 jours) ; conserver leur empreinte, les états des jobs, le manifeste et les fichiers bruts.

## Autorisation, limites et confidentialité

Le propriétaire autorise la recherche prospective de laboratoire sous ADR-0022 sans témoin externe obligatoire. Le protocole ne prétend ni attestation externe indépendante, ni preuve de toutes les propriétés physiques d'un être vivant, ni valeur adaptative universelle hors F0. I1 reste actif, I3 référence non enregistrée ; Stage2.1 global `NOT_ISSUED/HOLD_NO_VERDICT`.

**État avant première naissance Stage8-A : `NEW_PROTOCOL_FROZEN_NO_LIVES`.** Ne déduire aucune réussite de l'existence du code, de tests synthétiques ou des chiffres historiques Stage7.
