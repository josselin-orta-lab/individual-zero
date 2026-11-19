# i3 Stage8-D · Analyse descriptive de la diversité des génomes archivés de Stage8-C

**Observé le 19 novembre 2026. Statut : `STAGE8D_POSTHOC_ORIGINAL_BOUND_DESCRIPTIVE_COMPLETE`.** Cette étude post hoc est **descriptive uniquement**, n'est pas une expérience confirmatoire supplémentaire et n'a créé **aucune** vie, aucun World, aucune mutation ni aucun génome. L'effet primaire S−M positif de Stage8-C demeure fermé et inchangé.

## Source exacte et réception

- Étude mère Stage8-C : [Actions #44320492293](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44320492293), source expérimentale `a32b7bf50981e0bbaf688e3caf9973525888c05d`. Les mêmes vies originales, populations et descendances sont réutilisées ; jamais reproduites.
- [Auditeur brut antérieur au verdict #44406977082](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44406977082), source vérificatrice `23d0e3eabff0042123c84f4b292a2e4c72cfcc8f`, attestant les 32 256 corps gzip natifs et les 4 608 filiations mutées.
- Code de réduction Stage8-D figé au commit `62b075aaee500b9e48a3eeef7a4a7eddcbdf920a` : `src/i3/lab/stage8d_genomic_diversity_readonly.py`. La lecture des génomes suit obligatoirement la revalidation de l'audit de tous les corps originaux.
- Exécution unique [GitHub Actions #44489227157](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44489227157), source de déclenchement `6d6f55f481f3eccc90eac18a02dd432ab257cb05`, tentative initiale terminée avec succès le 19 novembre à **08:44 UTC**.
- Résultat conservé dans l'artifact GitHub `stage8d-existing-originals-genomic-diversity-44320492293`, id **14511624402** (ZIP 6 408 octets selon le relevé GitHub du 19 novembre). Il contient `STAGE8D_READONLY_GENOMIC_DIVERSITY.json`. Les valeurs ci-dessous proviennent **du journal effectif de cette unique exécution**, pas d'une nouvelle réduction locale du ZIP.

## Résultats descriptifs effectivement publiés

| Mesure | Sortie Stage8-D |
| --- | ---: |
| Statut du contrôle | `STAGE8D_POSTHOC_ORIGINAL_BOUND_DESCRIPTIVE_COMPLETE` |
| Vies natives d'origine reverifiées | **32 256** |
| Unités de population | **32** |
| Vies nouvelles | **0** |
| Diversité G2 normalisée : moyenne des différences S−M | **−0,007126119376657044** |
| Corrélation de Pearson entre différence de diversité G2 (S−M) et avantage de persistance G2 (S−M), par population | **−0,05954965008312981** |
| Populations S−M défavorables retenues | **P00, P01, P03, P11, P16, P18, P19, P24, P28, P31** |
| Nombre de populations défavorables | **10** |

La diversité est une distance euclidienne RMS entre **276 paires** constituées à partir des 24 génomes G2 de chaque population et bras, chaque gène continu étant normalisé par ses bornes déclarées. Elle n'est **pas** une hétérozygotie. Il y a **32 unités statistiques indépendantes revendiquées**, pas 276 paires ni 32 256 vies. Le coefficient de Pearson est exploratoire et aucune valeur de `p` confirmatoire n'est produite.

**Lecture scientifique bornée :** la différence de diversité moyenne S−M est légèrement négative et l'association populationnelle avec l'avantage de persistance est faible. Cela ne démontre ni absence de mécanisme génétique, ni égalité de diversité, ni effet causal de la concentration parentale. Les multiplicités parentales S/M restent exactement appariées par conception de Stage8-C, mais les **distances entre génotypes** ne le sont pas.

## Décision et limites

Le résultat préenregistré **Stage8-C** reste `STAGE8C_G2_SCORE_IDENTITY_ADVANTAGE_F0` : gain moyen +8,6759982639 pas, borne Student inférieure unilatérale 97,5 % +1,4683574706 pas, 22/32 populations positives et dix négatives. L'effet est inférieur à la grandeur de **10 pas** utilisée lors du dimensionnement ; le test préenregistré portait sur `m > 0`, et non sur `m >= 10`.

Les conclusions **Stage8-A (moyenne positive), Stage8-B (interaction non démontrée) et Stage7 (critère de signes négatif)** sont maintenues. Ni le succès Stage8-C, ni cette analyse post hoc ne nomment un gène causal ou ne démontrent une adaptation hors des trois familles F0.

**Prochaine question distincte, sans nouvel essai lancé ici :** vérifier au niveau des 32 lignées archivées quels traits génétiques et trajectoires d'ascendance pourraient être associés à la persistance en contrôlant explicitement l'identité et la concentration parentales, puis décider si une expérience prospective causalement identifiable est justifiée. Toute future étude expérimentale exigera un protocole/estimand/contrôle/seuil figés, des nouvelles allocations et les répétitions scellées propres à cette étude, sans rouvrir Stage8-C.

Provenance : `INTERNAL_PROSPECTIVE_NOT_EXTERNALLY_ATTESTED`. Les ZIP de GitHub ont une rétention limitée : préserver octets, empreintes et métadonnées de l'archive originale. I1 reste actif ; I3 reste référence de développement non enregistrée ; Stage2.1 scientifique `NOT_ISSUED/HOLD_NO_VERDICT`.
