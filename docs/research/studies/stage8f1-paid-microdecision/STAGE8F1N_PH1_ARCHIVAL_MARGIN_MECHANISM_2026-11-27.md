# Stage8-F1N-PH1 | Pourquoi la marge personnelle payée échoue presque toujours à modifier la décision suivante

**27 novembre 2026. Étude descriptive POST-HOC, exclusivement sur les originaux F1N déjà consommés.** Aucun nouveau monde, aucune nouvelle naissance, aucun `World.step`, aucun seuil exploré par une nouvelle exécution. Aucun changement des verdicts préenregistrés M/A/B, de F1L, F1M ou de Stage2.

## 1. Provenance et méthode

L'unique [tir F1N #45824249204](https://github.com/josselin-orta-lab/individual-zero/actions/runs/45824249204), première tentative, a utilisé le code `89f58723789ad0c88336b6e5b0eb7ff3227348a1`. Réservation consommée `38d1c94a146d32bd89151fca906a26a775052560`. Les [RAW](https://github.com/josselin-orta-lab/individual-zero/releases/tag/i3-stage8f1n-t60-raw-heldout-once) et [COLD](https://github.com/josselin-orta-lab/individual-zero/releases/tag/i3-stage8f1n-t60-cold-heldout-once) sont les sources immuables, sans escrow externe indépendant. Le [verdict prospectif consolidé](STAGE8F1N_SCIENTIFIC_COLD_VERDICT_AND_NATIVE_CUSTODY_2026-11-27.md) reste négatif M/A/B.

Le nouvel auditeur `tools/stage8f1n_ph1_archival_margin_diagnostic.py` (stdlib uniquement) vérifie les SHA-256 littéraux du tar RAW `8995e25ced26dceb85737da6b8e01fd94c3877421238f1fccc0c7dd0e3d01ea6`, du manifeste `72c3d13da7a3266e0b71e670cfb930ce08470778d227bc1d7728c447a4dbea50`, de l'index `817b21bf5d1a5e2f19b1a07ab03fbb581d79327851a4054d09fc4288147ecb74` et du rapport froid `650aee67b3d356bc4dd359721b0f279e8af6a5648d35bc4de9350aa128ac681b`. Il contrôle les 336 parties compressées/décompressées (2 293 778 312 octets JSON), les 48 checkpoints, l'identité des 48 racines, et extrait trois témoins utiles par racine : T5 et les deux continuations T6..T60 réelles. Les sept parties avaient déjà fait l'objet du froid physique indépendant d'origine ; PH1 n'est pas un nouveau calcul de la physique ou un nouveau verdict scientifique.

Comparaison des **deux branches réellement exécutées** : témoin privé T5 déjà admis, clé et q conservés, mêmes options scorées, scores, évidences normalisées, accumulateurs initiaux, instantanés de tous les tours payés, activateurs terminaux avant résidu, factures T6 et état corporel de départ. Seul le seuil de la clé retenue change dans le bras `margin`, comme prévu. Les 48 paires satisfont ces égalités. Une valeur `q>0` ne prouve pas que la trace concerne une option utile ou même disponible.

L'observateur ne contient qu'un **nombre** d'options offertes, et non leur liste complète. On ne conclut à la non-offre d'une clé absente du `scored_order` que si toutes les options offertes ont été scorées. C'est vérifié dans **48/48** paires. Dans un autre jeu de données avec des options non scorées, l'auditeur classerait la cause précise de l'absence comme indéterminée.

## 2. Décomposition exhaustive, descriptive, des 48 paires

| Classe observée (exclusives) | Origines | Description |
|---|---:|---|
| Clé T5 non offerte à T6 | 31 | Aucun seuil de cette clé ne peut être modifié. |
| Clé offerte/scorée, ne franchit jamais le seuil même avec marge | 10 | Évidence T6 négative et activation finale exactement nulle dans les deux bras. |
| Clé offerte/scorée, déjà gagnante sans marge | 6 | Toutes ces clés sont `explorer:*`; l'abaissement du seuil est redondant pour le gagnant. |
| Gagnant puis moteur changés | 1 | N26, `boire` vs `dormir`. |
| **Total** | **48** | Aucune sélection de sous-cohorte. |

Les 48 q sont positifs, dont 15 saturés à 1. Médiane globale 0,356617 ; médiane des 31 clés non scorées 0,399874 ; médiane des 17 clés scorées 0,354447. Ces résumés ne sont ni un test d'association ni une mesure d'utilité. La trace T5 est `boire` dans 25 cas ; 24 de ces clés ne sont pas offertes à T6. Les dix clés avec activation finale nulle se répartissent en neuf `attendre` et un `dormir`. Les 17 seuils modifiés ne changent donc le gagnant qu'une fois. Les ensembles des options franchissant le seuil diffèrent lors d'au moins un tour uniquement pour N26 ; au **dernier tour, 0/48** ensembles diffèrent. Le franchissement de la clé est avancé uniquement pour N26. Un simple comptage des options franchissant le seuil final aurait manqué l'effet de leur **surplus relatif**, utilisé pour choisir le gagnant.

Les identités T6 où la clé T5 est encore scorée sont N06, N09, N11, N12, N15, N18, N21, N22, N23, N24, N26, N27, N31, N37, N43, N44 et N45. Le dénominateur scientifique reste 48 ; aucune nouvelle règle de succès n'est appliquée à ces 17 cas.

## 3. N26 : le seuil modifie le classement, pas l'évidence présente

N26, seed `202611259826`, écologie `n_water_diagonal_finite_food_safe`. T5 : `boire` réellement choisi, eau corporelle 35,4 avant l'action puis 57,0 après l'action, apprentissage et écriture payés ; stock d'eau fini passe de 2 à 1. Le souvenir personnel T5 est `boire`, `q=0.9688204415037732`.

À T6, les deux bras ont **les mêmes scores et évidences**. `attendre` et `dormir` partagent le score le plus élevé (-0,04112845238413741), tandis que `boire` est classé troisième (-0,047777216399089106). Le témoin natif montre cinq tours substantifs dans les deux bras ; facturation T6 égale (8 cycles totaux, 70 items mémoire, 63 pas simulés, 0 replays ; énergie 0,30, vigilance 0,526 payées, impayé nul). `boire` a une évidence positive mais inférieure à celle de `dormir` (0,6019839274 contre 0,7747413617), activation finale 2,0236291704 contre 2,6043705613. Aucun score T6 ni activateur n'est amélioré par le souvenir de confiance.

| Option | Seuil masqué | Seuil marge | Activateur final | Surplus relatif masqué | Surplus relatif marge |
|---|---:|---:|---:|---:|---:|
| `boire` | 1,5 | 0,773384669 | 2,023629170 | 0,349086114 | 1,616588163 |
| `dormir` | 1,5 | 1,5 | 2,604370561 | 0,736247041 | 0,736247041 |

`boire` franchit son seuil au tour 2 dans `margin`, au tour 4 dans `masked`. Les ensembles de franchissement divergent aux tours 2 et 3 seulement ; au tour 5 les trois options `boire`, `dormir`, `attendre` franchissent dans les deux bras. Le changement causal de gagnant provient donc du surplus **normalisé par le seuil** plus élevé de `boire` dans `margin`, et non d'un nouveau signal pertinent dans son score T6. Le bras masqué résout la concurrence entre `attendre` et `dormir` selon sa propre décision native, et exécute `dormir`. Le bras marge exécute `boire`. Pas d'action imposée, pas de nouvel essai contrefactuel.

## 4. N26 : le désavantage terminal n'est pas une simple perte immédiate d'eau ou une mort

Après T6, le dernier stock d'eau est consommé dans `margin`, pas encore dans `masked`. Les deux branches choisissent ensuite leurs actions sans réapplication directe de la marge. À T8, les deux ont consommé ce stock. Les différences de réserves (marge - masqué), dans l'ordre énergie, nourriture, eau, intégrité, vigilance, montrent que l'effet initial **s'atténue presque entièrement à T8**, avant une nouvelle divergence des trajectoires :

| Tick | Moteur marge | Moteur masqué | Différences corporelles après apprentissage payé |
|---|---|---|---|
| 6 | boire | dormir | -3,278 ; +0,17 ; +22 ; -0,20 ; -3,748 |
| 7 | dormir | attendre | -0,1686 ; +0,02 ; +22 ; -0,20 ; -0,024 |
| 8 | attendre | boire | ≈0 ; 0 ; ≈0 ; 0 ; -0,006 |
| 19 | se_deplacer W | se_deplacer N | +0,0382 ; 0 ; ≈0 ; 0 ; +0,032 |
| 60 | se_deplacer N | dormir | -2,7698 ; -0,62 ; ≈0 ; 0 ; -1,208 |

On compte 33 commandes différentes sur les 55 ticks T6..T60, dont 32 après T6, dans cette **unique paire**, pas 33 réplications indépendantes. Ce résultat montre une divergence de trajectoire consécutive au contraste initial, pas une démonstration d'une cause unique de chaque divergence tardive. Le gain d'eau transitoire ne se transforme pas en gain terminal : aucune perte ou gain de vie, et dominance corporelle du contrôle masqué à T60. Ne pas transformer le cas N26 en règle imposée contre `boire`, ni conclure que dormir aurait toujours été préférable.

## 5. Orientation de recherche proposée (pas un préenregistrement, pas une autorisation)

Les observations distinguent **accessibilité de l'expérience, pertinence dans le contexte présent et qualité de ses conséquences**. La marge q de F1N décrit une compétition gagnée à T5, pas la calibration de ses prévisions ni sa valeur corporelle future. Notre hypothèse prospective de travail, à soumettre dans un protocole distinct F1O, est qu'une trace personnelle de **l'erreur de prévision corporelle réellement observée** pourrait avoir un rôle plus informatif qu'une réduction de seuil fondée sur la seule confiance passée.

Cette piste devrait d'abord tester si des erreurs précédemment observées et réellement mémorisées (prévisions propres avant l'action, écarts aux cinq réserves réellement constatées après action et cognition payées, contexte sensoriel et corporel dont le sujet dispose) améliorent la **calibration prospective de projections** à un coût cognitif réellement apparié. Les deux bras paieraient les mêmes accès et opérations substantives ; le contrôle masquerait seulement le contenu de correction, pas son prix. Aucun accès gratuit au `WorldSpec`, à la quantité cachée des ressources, à une valeur exogène du laboratoire, à une vie future ou au bras jumeau. L'action resterait celle choisie par l'individu à partir de ses propres enjeux ; aucun veto ni consigne du type « ne pas boire ». Une correction de prévision doit pouvoir être nulle ou défavorable. La calibration et l'effet moteur, puis la valeur adaptative, sont des questions distinctes. Il faudra fixer avant toute exposition les conditions, les sources, les critères falsifiables et les limites de financement, en tenant compte des résultats déjà obtenus en F1L/F1M, sans sélectionner N26 ni rechercher un coefficient sur F1N.

Cette hypothèse n'est **pas** démontrée par PH1. Elle n'autorise aucune nouvelle naissance ; F1O nécessitera un préenregistrement et des identités nouvelles. La prochaine tâche est de définir un estimand de calibration et un contrôle d'information à coût réel, sans créer de nouveau moteur de recherche de seuils sur les 48 vies F1N.

## 6. Reproduction logicielle archive-only

Avec les trois fichiers RAW et le rapport COLD extraits des Releases ci-dessus, sous Python 3.11+ :

```sh
python -m tools.stage8f1n_ph1_archival_margin_diagnostic \
  --raw-dir /path/to/raw --cold-report /path/to/F1N_INDEPENDENT_COLD_T60.json \
  --output /path/to/F1N_PH1_ARCHIVAL_MARGIN_DIAGNOSTIC.json
```

Les miroirs ZIP originaux Actions peuvent aussi être passés avec `--native-zip` et `--cold-zip`, dont les SHA sont figés dans le programme. La lecture des octets originaux a été réalisée localement depuis le miroir Actions ; les quatre assets vérifiés sont octet-identiques à ceux des Releases. Le JSON dérivé complet reproduit chaque contraste et la trajectoire N26 ; son SHA-256 local (mode assets, Python stdlib) est `7f668fc868901ad5db9d2f2614623f39a1b36533604db621fb0764be51491a34`. Le workflow PR-only `i3-stage8f1n-ph1-archive-only.yml` est proposé pour refaire cette lecture à partir des Releases, sans moteur ni claim. Cinq tests unitaires (dont rejet du mauvais rapport et du mauvais tar avant analyse, et contrôle d'import) passent localement. Ces tests sont logiciels, pas de nouvelles expériences scientifiques.

**Statut : `F1N_PH1_ARCHIVE_ONLY_MECHANISM_DIAGNOSIS_NO_NEW_LIFE`.** F1N reste `F1N_COLD_AUDITED_COMPLETE_NEGATIVE_M_A_B_CONSUMED_ONCE_NO_RETRY`, Stage2 `NOT_ISSUED/HOLD_NO_VERDICT`. Aucun changement des originaux ou seuils préenregistrés, aucune promotion scientifique.
