# I1 A2-R : preregistration prospective de la recompense physiologique

**30 octobre 2026. AVANT toute naissance A2-R.** Issues #304, #305, #306; politique #348. Ce contrat ne modifie pas I1 et n'autorise pas une cohorte immediate.

## Hypothese et historique non reinterpretable

A1-C, 48 vies M11 originales (source 26f7929b6db43f68e78b0cc0d9c67e7444f924c6; run #40944104333), demeure **NO_GO** sur le benefice adaptatif L3. Les analyses post hoc #622-#624 reconstituent les 12 poids TD, Stage8 et Competition. Le ruban fixe de #624 donne 195 collectes a recompense native positive, aucune sous deficit seul, et 102 signes Q d'attente non positifs sur 154 observations Q-only, concentrees dans deux temperament blocks. Ceci ne montre ni 102 actions evitees ni un benefice; des reserves excedentaires peuvent avoir une valeur future.

Hypothese falsifiable H-R : sur de **nouvelles vies**, une recompense TD fondee sur la reduction des seuls deficits physiologiques produit-elle une baisse de la charge cumulee des deficits, sans surmortalite et dans deux roles nutritifs inverses, par rapport a I1 canonique ? H-C (credit instrumental collecter vers manger) et H-D (arbitrage face a attendre/dormir) sont des mediations a observer, pas des leviers autorises a modifier en parallele.

## Bras et unique difference autorisee

**CANONICAL_ABS** : recompense native de ValueAndNeeds.reward_between, somme w_i fois reduction de distance absolue |body_i - setpoint_i| pour les quatre besoins.

**RESEARCH_DEFICIT** : seulement dans une branche de recherche, somme w_i fois reduction de max(setpoint_i - body_i, 0), avec les memes consignes/poids innees. Ne pas retoucher la physiologie, le monde, la consommation, les signatures/features, TD eta/beta/lambda, competition, Q lecture, Stage8, sommeil, buts, Action Control, UC ni les baies.

Les deux bras gardent les Q **lisibles**; aucune priorite codee pour manger, collecter, boire ou attendre. Aucun oracle ni action imposee. La difference de reward doit etre appliquee sur les consequences physiques reelles y compris sommeil et reveil, de facon coherent pour tous les chemins de retour TD, avant naissance via mode versionne et atteste par M11. Une simple injection mutable ou un shadow offline ne constituent pas l'intervention prospective. La naissance canonique doit conserver sa parite.

## Cohorte et critere primaire geles

**Graines nouvelles 2001..2024**, 24 blocs de temperament; 2 roles (native, reversed), 2 bras reward independamment nes : **96 vies, 48 paires**, horizon **192 pas** ou mort irreversible plus precoce. Deux roles d'un meme seed ne sont pas independants. Identites individuelles M11 uniques, ordonnance de naissance et affectation deterministic SHA-256 domaine i1-a2r-reward-identity-v1, definies avant les resultats. Une seule execution one-shot sur SHA source final, sans relances de vies ou remplacement de mort.

Score S par vie = aire des quatre deficits ECO-v1 normalises / (4 x 192), **penalite maximale de 1 par canal sur chaque pas post-mortem**; plus faible = meilleur. Calculer le score depuis le corps vecu, independamment du reward TD. Le survivant a H est censure pour sa survie future, mais conserve son score H.

Pour chaque role/seed : D = S(canonical) - S(candidate), positif favorable a candidate. Pour chaque seed : B = (D_native + D_reversed) / 2. Toute inference est sur les **24 B**, jamais 48 paires ou 96 pseudo-replicats. Statistiques/version figees dans tools/research/i1_a2r_statistics.py.

Conditions cumulatives pour **CONFIRMATORY_TARGETED_SIGNAL_PENDING_REVIEW** :

1. 96/96 vies et 48/48 paires integres, identite/mode et SHA d'origine M11, debut de vie sans connaissance privilegiee, WAL/chaines et corps froidement verifies. Prefixe physique de chaque paire identique **avant la premiere recompense modifiee**. Donnee perdue/incoherente, difference pre-intervention ou mode non atteste : MEASUREMENT_BLOCKED, sans remplacement.
2. Dans chaque role, au moins **18/24 paires** exposent une vraie difference de reward TD puis une Q modifiee lue dans Stage8, en concurrence Competition et suivie d'une commande differente admise par Action Control. Le lien et la temporalite doivent etre attestes par les evenements M11. Sans cette exposition : NOT_EXPOSED; toutes les paires restent comptabilisees.
3. Moyenne des 24 B au moins **+0.0150**; borne inferieure IC t bilaterale 95 % sur 24 blocs strictement >0 (t23=2.068657610419041); sensibilite du **test de signes exact** unilaterale <=0.025. Les B nuls sont comptes non positifs, l'hypothese de signes symetriques/independants est explicite, et ce p ne vaut pas randomisation des 96 vies.
4. Dans chaque role, D moyen >0, au moins **16/24 paires** avec D>0, et **aucun deces supplementaire** du candidat avant H par rapport au bras canonique. Cette derniere condition est une garde de securite, pas une preuve de non-inferiorite de survie.

Si exposition suffisante mais un seuil manque : **NO_GO**, sans modification de N, H, des seuils ou rejet de cas. Si tous passent : **PENDING_REVIEW** et revue humaine de provenance et des explications alternatives, **jamais GO automatique**. L3 general reste NOT_ESTABLISHED, A1-C reste NO_GO, quels que soient les resultats A2-R.

## Portes de mise en oeuvre (non franchies par cette PR)

Un second lot devra coder et tester la variante **seulement sur une branche scientifique**, faire attester le mode dans l'image causale et l'ensemble des chemins de reward; faire un audit froid indépendant M11, un test de parite canonique et des tests adversariaux sur avant/apres, mortalite et UC. Separer source de generation des versions de lecteurs, et sauvegarder 96 WAL natifs, manifestes SHA-256 et erreurs. Ne lancer aucune naissance avant outils, tests, garde one-shot et revue scientifique du protocole. Les outils actuels sont exclusivement statistiques purs, sans I1 ni birth; CI python 3.11/3.12 **ciblee uniquement**, pas de CI naturelle lourde.

**Regle d'arret** : aucun rattrapage de A1-C ou de A2-R. Une conclusion negative constitue un resultat scientifique, pas une raison de retoucher le comportement d'I1 pour passer le test.
