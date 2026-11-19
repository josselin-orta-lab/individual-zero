# Stage8-D : plan analytique post hoc de diversité génomique, sans naissance

**Établi le 19 novembre 2026 avant la relecture génotypique Stage8-D. Statut : SOFTWARE_READY_NO_ORIGINAL_STAGE8D_AUDIT_YET.**
L'analyse est explicitement **post hoc** : les résultats G2 Stage8-C sont déjà connus. Cette note ne préenregistre pas de découverte confirmatoire ni de mécanisme causal. Aucun World, aucune mutation ni vie nouvelle.

## Sources déjà figées

- Étude Stage8-C : [science unique #44320492293](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44320492293), source a32b7bf50981e0bbaf688e3caf9973525888c05d, 32 populations F0, **32 256 vies scientifiques**, trois bras S/M/U, verdict G2 sélectionné moins multiplicité appariée positif, 22 populations favorables / 10 défavorables.
- Plan antérieur à la première naissance : artifact 14455899574, allocation bee65ba13a75eca1b283f1558aba2fc5418748aa84c35d8525fe6646b8dd22b6.
- Archive originale G0/G1/G2 : artifact 14476010510, 32 256 gzip, tous les SELECT_G1.json, SELECT_G2.json et manifestes.
- Audit complet distinct, écrit avant le verdict : [Actions #44406977082](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44406977082), artifact 14476915655, code audit Git 23d0e3eabff0042123c84f4b292a2e4c72cfcc8f, blob e24d0a96af183453256966c9f371b5aba17f5d03.
- Analyseur descriptif source-figé : [PR #1450](https://github.com/josselin-orta-lab/individual-zero/pull/1450), merge 62b075aaee500b9e48a3eeef7a4a7eddcbdf920a. L'ancien audit des vies est inchangé.

## Calculs fixés avant la présente analyse

**Unité d'analyse : population (n=32)**, pas la vie, le génome ni la paire de génomes. Lire 24 génomes v4 par population/bras S/M/U en G1 et G2. Pour chaque paire de génomes, calculer une distance RMS normalisant chaque différence de gène par son intervalle déclaré dans genome.BOUNDS. La moyenne des **276 distances** de chaque groupe de 24 génomes produit une seule mesure de diversité par population et bras. Les bornes sont fixées par le génome v4, non apprises des résultats. Ce calcul ne mesure pas l'hétérozygotie ni la diversité fonctionnelle.

Les 24 tirages parentaux par population/bras et génération G1/G2 produisent une multiplicité, un nombre de parents distincts et une entropie Shannon. Exiger **l'égalité exacte des multiensembles de reproduction et de l'entropie entre S et M** : sinon ne publier aucune association. Rapporter les 32 diversités par bras/génération, leurs moyennes/écarts-types entre populations, les 32 différences descriptives de diversité S−M en G2, et leur Pearson descriptif **avec les 32 effets connus de persistance S−M**, sans p-value ni seuil confirmatoire. Ne pas attribuer une cause génétique à une association.

Inclure les dix populations Stage8-C dont la sélection a perdu face à M : P00, P01, P03, P11, P16, P18, P19, P24, P28 et P31. La comparaison des « perdantes » aux gagnantes est une sélection par l'issue, donc descriptive exclusivement.

## Séquence scellée et falsificateurs

1. Sur la source exacte 62b075aaee500b9e48a3eeef7a4a7eddcbdf920a, exécuter les tests synthétiques sans vie. Téléchargement uniquement des archives Stage8-C déjà terminées et du rapport de premier audit. La création de World, les mutations et les naissances ne sont pas appelées.
2. Réexecuter le **même auditeur indépendant** sur les 32 256 gzip, vérifier SHA compressés/décompressés, 4 608 mutations et lignées, identités d'archives, plan antérieur à la naissance, résultats de chaque population, et comparer les résultats au rapport indépendant préverdict. Toute divergence ou archive manquante arrête la procédure.
3. Lire les événements de sélection G1/G2 **déjà vérifiés** et rejeter les omissions de populations/bras/slots, les faux SHA génomiques, l'inégalité des occupations S/M. Ne jamais transformer les 276 paires en 276 unités d'inférence.
4. Produire un petit JSON contenant les 32 lignes, les 10 perdantes, les métriques descriptives et un statut exploratoire. Zéro nouvelle vie et zéro World. En cas d'échec : AUDIT_MISMATCH/NO_NEW_VERDICT, aucune révision rétroactive de Stage8-C, aucune relance de cohorte.
5. Exécution à usage unique : nouveau workflow déclenché uniquement par son fichier YAML ajouté sur main, run_attempt=1, checkout figé au commit de l'analyseur, sans option pour générer une nouvelle étude.

**Limites :** résultats post hoc non confirmatoires, génomes à paramètres continus sans phénotype causal isolé, indépendance statistique des populations non prouvée, trois mondes F0 seulement. Provenance interne GitHub, non attestée hors hébergeur. Sauvegarder octets ZIP et SHA-256 avant expiration des artifacts autour de février 2027.

Stage7 et Stage8-B restent négatifs selon leurs critères ; Stage8-A et Stage8-C restent positifs selon les leurs. I1 actif, i3 non promu, Stage2.1 scientifique NOT_ISSUED/HOLD_NO_VERDICT.
