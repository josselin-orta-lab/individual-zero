# I1 : réaudit intégral de Q et de la chaîne décisionnelle A1-C (post hoc)

**Données** : 48 vies de la cohorte A1-C confirmatoire unique, GitHub Actions [#40944104333](https://github.com/josselin-orta-lab/individual-zero/actions/runs/40944104333), SHA de génération `26f7929b6db43f68e78b0cc0d9c67e7444f924c6`. Les 48 ZIP originaux et le manifeste SHA-256 sont requis. L'issue scientifique principale est [#305](https://github.com/josselin-orta-lab/individual-zero/issues/305).

**Cette analyse est post hoc. L'expérience préenregistrée A1-C reste NO-GO ; L3 reste NOT_ESTABLISHED. Aucun nouveau-né, paramètre TD, reward, UC, Competition, I0 ou moteur I1 n'est modifié.**

## Méthode indépendante, limitée au moteur source

`tools/research/i1_a1c_td_full.py` reprend exactement les **12 caractéristiques P-32** de la source, dans leur ordre : biais, énergie, nourriture, eau, intégrité, x, y, nuit, quatre buts actifs ; positions divisées par 31, corps par 100. Le contexte de nuit est 0 sur l'horizon H48 du monde préenregistré. L'état TD lors de la décision admise provient d'une capture première-personne M11 signée, et le but des événements `active_goal_changed` M11.

Les coefficients effectivement nés sont `beta = 0.8`, `lambda_e = 0.8`, `eta = 0.05`. Pour chaque publication TD, l'auditeur reproduit `Q_previous`, `Q_next`, `delta`, la décroissance `(beta*lambda_e)**segment_length`, les **12 coefficients d'éligibilité**, l'incrément de chacun des poids et les compteurs de lecture apprise. Il compare ensuite toutes les valeurs Q natives des évaluations Stage8, les statuts **masqués** du témoin et les preuves transmises à Competition. Les commandes sélectionnées sont contrôlées contre le seuil franchi ou le repli licite `permanent:attendre` ; il contrôle également la correspondance avec la physique et les 48 pas.

`tools/research/i1_a1c_td_full_audit.py` vérifie auparavant les **48 ZIP originaux**, leurs empreintes SHA-256, le SHA source, les individus attendus, les chaînes d'occurrences M11, les têtes finales SQLite et la correspondance avec les reçus. Il ne simule aucune physique ni ne relance de vie.

## Résultat vérifié à froid sur les 48 ZIP originaux

| Assertion indépendante | Total |
|---|---:|
| Archives / journaux M11 audités | **48/48** |
| Valeurs Q native Stage8 recalculées | **5 261** |
| Évaluations Stage8 dans le bras masqué conformes | **2 267** |
| Champs `q_previous`, `q_next`, `delta` vérifiés | **3 201** |
| Mises à jour TD dont tous les poids ont été reproduits | **1 067** |
| Liaisons numériques Stage8 → Competition | **13 853** |
| Admissions avec seuil franchi | **1 002** |
| Admissions `attendre` de repli | **113** |
| Résidu numérique maximal absolu | **2,665×10⁻¹⁵** |

**Aucune discordance** n'a été identifiée dans les journaux audités entre les poids TD reconstitués, les valeurs Q publiées par Stage8, les mises à jour signées et le transfert numérique à Competition. Cela ne signifie pas qu'une option disposant d'une bonne valeur Q doit nécessairement gagner Competition.

### Crédit instrumental quantifié sur les 12 dimensions

La projection de la **contribution d'une seule mise à jour des poids de collecte** sur le vecteur d'état de la décision TD suivante est `eta * delta * dot(trace_collect, next_features)`. Ce n'est ni le changement Q *total* incluant les autres mises à jour, ni un bénéfice physiologique contre-factuel.

| Rôle / bras | Ingestions avec mise à jour TD | Projection moyenne de cette contribution sur Q collecte |
|---|---:|---:|
| Native / canonique | 23 | +0,061533 |
| Native / TD masqué | 28 | +0,101828 |
| Inversé / canonique | 35 | +0,042771 |
| Inversé / TD masqué | 26 | +0,196258 |

Sur les **112** ingestions suivies de TD, cette contribution est positive **64** fois et négative **48** fois. La comparaison par groupe n'est pas une inférence confirmatoire; les différences de sommeil, ingestions et états physiques participent à ces trajectoires.

## Ce qui est maintenant établi et ce qui ne l'est pas

- **Vérifié** : continuité numérique intégrale du modèle linéaire Q, des 12 dimensions de trace d'éligibilité et des lectures Q Stage8 natives. Le masquage n'empêche pas les mises à jour TD du témoin. Les évaluations arrivées dans Competition correspondent à Stage8.
- **Non établi** : que ce crédit améliore la politique sur des vies nouvelles ; que sa récompense positive reflète un bénéfice corporel ; que `lambda_e` soit inadapté ; que le sommeil soit l'unique médiateur ; que la projection de contribution locale soit une vraie différence d'utilité écologique.
- **À examiner avant toute nouvelle naissance** : distinguer les contributions numériques de Q des contributions *effectivement sélectionnées* par Competition, établir le coût d'opportunité du sommeil à besoins égaux, et **préenregistrer une intervention mécanistique isolée** avec un véritable comparateur physique. Pas de retuning sur les 48 vies A1-C.

## Reproduction et falsification

Exécuter `python tools/research/i1_a1c_td_full_audit.py --root /dossier/archives_originales --out /dossier/result.json --workers 1`. La variante `--workers 4` conserve l'ordre des résultats et n'affecte aucune donnée. Les tests adversariaux ciblés contrôlent une Q inventée, une fuite dans le bras masqué, des preuves Competition fausses, un seuil incohérent, un état P-32 falsifié, des signatures et coefficients TD incorrects et une archive SHA erronée.

L'observation d'une contribution à Q, même prouvée dans M11, ne constitue **jamais** à elle seule une certification L3.
