# Stage8-F1G · deux contrôles indépendants, TD et tampon, sans effet moteur sur huit écologies

**21 novembre 2026 · deux verdicts primaires négatifs, avec 8/8 appariements de coût valides :**

- `NO_TD_CONTENT_EFFECT_IN_EIGHT_ECOLOGIES` : **K_TD = 0/8** commandes motrices modifiées par la substitution temporaire des valeurs TD avant/après apprentissage.
- `NO_BUFFER_CONTENT_EFFECT_IN_EIGHT_ECOLOGIES` : **K_BUFFER = 0/8** commandes modifiées par le masque non factuel du contenu de l'unique épisode du tampon, à taille de tampon égale.

L'état global du protocole est `TWO_SEPARATE_TD_BUFFER_CONTENT_COST_GATES_EVALUATED`. **Aucun résultat nul n'est réinterprété en succès causal.** Il reste possible que les valeurs TD affectent les scores calculés et que le tampon serve à l'apprentissage/rejeu ultérieur; ce protocole ne demande que le **choix moteur immédiat au tick 2**.

## Préenregistrement avant F1F et sources originales

Le [préenregistrement séparé F1G](STAGE8F1G_SEPARATE_TD_BUFFER_PREEXPOSURE_2026-11-21.md), commit `82d3dc015b5d89ce52b1abc632e7a6a1a52d01b7`, a été scellé **avant même l'exécution de Stage8-F1F**. Il fixe exactement les huit contextes `bare`, `water_here`, `water_north`, `water_east`, `water_west`, `food_here`, `food_east`, `mixed_here_water_east_food`, et les deux contrastes. **Aucun monde n'a été choisi après la divergence de F1F**.

Source individuelle F1C réellement vécue/payée : artifact #14679910820, `F1C_PAID_NATIVE_ORIGINAL.json`, **125436 octets**, SHA `e46ad5f54af49796da65f48d603595544116aa6e73632546b0935d2178c5e91d`. Source écologique F1F : [rapport et audit](STAGE8F1F_EIGHT_ECOLOGIES_NATIVE_CONTENT_RESULT_2026-11-21.md), artifact #14702338615, JSON SHA `f620d1b46ddf269dc368dcd90ba6c93f44f0b6442f8d9e6322440de32e3fbab5`, contre-audit indépendant artifact #14702267579, SHA `8013f2add1f3eb0190127bb77eac588c95f153f32ba21113302bafa0292e2ac2`. La CI F1G récupère les trois originaux par **nom d'artefact et run-id exact**, vérifie chaque SHA et le score F1F 1/8 seulement **pour verrouiller sa provenance**, jamais pour sélectionner les contextes.

[PR expérimentale F1G #1493](https://github.com/josselin-orta-lab/individual-zero/pull/1493), code source de base `f6c86019df2800e5584f1b047746e093c4d17abe` après la fusion F1F.

## Protocole mécanique, financement natif

Une même expérience `dormir` F1C librement décidée a été exécutée et reproduite dans chacun des huit `WorldSpec`, avec paiement postaction **0,1096 énergie / 0,174 vigilance**, conservation d'effets, valeurs TD et tampon après apprentissage. Les ressources de chaque écologie deviennent visibles **uniquement après le premier pas natif**. Les huit instants de choix suivants partent du même corps `[2.9096,74.63,59.6,90.2,98.776]`, même état privé F1C appris, même RNG, mêmes gènes, et de la perception autonome de chaque monde.

Pour chaque monde, **quatre copies identiques** de l'individu logiciel ont été exécutées :

| Bras | Contenu exposé au seul `Mind.decide` |
|---|---|
| `full` | Effets, valeurs TD et épisode authentiquement appris |
| `sham_state` | Copie de contenu identique, contrôle neutre |
| `mask_td` | **Valeurs TD d'avant apprentissage F1C**, matrices 3×6 exactes ; EffectsModel et tampon authentiques |
| `mask_buffer` | **Une place mémoire occupée par `None`** au lieu du contenu de l'épisode, sans créer de fausse expérience ni en modifier le nombre ; effets et valeurs TD authentiques |

Ces interventions sont **temporaires**. Avant `World.step`, la vraie mémoire acquise est restaurée et les états scellés le prouvent. L'individu prend une commande motrice de son propre contrôleur, jamais imposée par le laboratoire. **Aucun apprentissage/rejeu n'est exécuté pendant la présence de la sentinelle**, et aucune autre information du monde n'est injectée.

Le protocole exige **le même travail `CognitiveWork` entier, les mêmes coûts énergie et vigilance totalement payés, la même capture et le même corps à l'entrée du calcul, et un `sham` strictement neutre dans les 8 mondes**. Ce critère est satisfait **8/8**. Les coûts varient naturellement selon le monde (`bare` : 0,2306 E/0,344 V ; `mixed` : 0,2888 E/0,402 V), mais **sont identiques entre les quatre bras d'un même monde**, sans coût fictif d'égalisation.

## Commandes réellement enregistrées

| Écologie | Mémoire intacte | TD masquées | Buffer masqué |
|---|---|---|---|
| `bare` | déplacement Est | Est | Est |
| `water_here` | boire | boire | boire |
| `water_north` | déplacement Nord | Nord | Nord |
| `water_east` | déplacement Est | Est | Est |
| `water_west` | déplacement Ouest | Ouest | Ouest |
| `food_here` | déplacement Est | Est | Est |
| `food_east` | déplacement Est | Est | Est |
| `mixed_here_water_east_food` | déplacement Est | Est | Est |

Le bras `sham_state` coïncide exactement avec `full` dans les huit écologies. **Deux critères primaires négatifs : 0/8 pour TD, 0/8 pour buffer.**

Les valeurs TD ne sont pas inexistantes : elles ont été réellement modifiées par `learn_from_outcome` et leur substitution **modifie les évaluations**. Exemple `bare` : score meilleur des explorations affiché ≈ **−0,652133** avec TD après expérience, ≈ **−0,650694** avec les TD antérieures, sans changer l'option motrice. En contexte `mixed`, ≈ **−0,378790** contre **−0,377351**, toujours Est. Les différences de scores ne suffisent pas pour déclarer un effet sur l'action.

Le contenu du `buffer` n'est actuellement pas utilisé comme conséquence distincte dans la décision qui suit : la méthode native `Mind.decide` facture le **nombre** d'éléments `len(self.buffer)`, mais le contenu sert notamment à l'apprentissage et aux replays `learn_from_outcome`, **qui ne sont pas testés ici**. Son verdict nul n'est donc pas un verdict sur sa valeur fonctionnelle globale.

## Reproduction, audit indépendant et échecs conservés

[CI F1G corrigée #44893263579](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44893263579) : **2/2 jobs PASS**, **18/18 tests de falsification PASS**, deux processus producteurs Python 3.11 génèrent un **JSON octet-identique** de **40 `World.step`** natifs synthétiques par processus (8 sources F1C, 8×4 décisions secondes). Un réducteur Python 3.12 **stdlib seulement, sans importer le moteur `Mind`, `World` ni le producteur**, vérifie les huit WorldSpecs, la physique, les **32 reçus natifs de décision**, les comptes, la conservation des mémoires et les factures des deux monnaies.

La **première CI #44893210594 est explicitement FAIL** : le test malveillant `test_falsify_private_genetics_or_rng_override_rejected` a tenté d'indexer comme une liste le champ `w` scellé sous forme de tuple. Seul le test a été corrigé au commit `333d1e8d89dcce57eb48f35fcb68dc4fa0021361`. **Aucun reçu de preuve F1G scientifique n'a été généré par cette CI en échec**, et aucune politique/native World n'a été retouchée pour l'expérience suivante.

Original F1G [artifact #14702437957](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44893263579), `F1G_TD_BUFFER_ORIGINAL.json` **2 143 612 octets**, reproduction identique, SHA256 `a7f0782886b3d2b97cd91ea11803934f31736b91e6d659c700a3d1dd886a8376`, ZIP `6ca75a54271c85d9d41b95bd34ba2a7cbb7470680c0a81e9f6724fa0dff8129f`. Audit indépendant [artifact #14702663751](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44893263579), `F1G_INDEPENDENT_COLD_TD_BUFFER_AUDIT.json` **3 384 octets**, SHA `ec3b1c953c69d87dc042ab81da55809984e7b78c175a2697a6b3d0a24fa21310`, ZIP `d482d54a8ad3333796f780255edc788904a26c8edef3ff4f6be6a92358f5147e`. Les originaux F1C, F1F, F1G et leurs audits sont réunis dans une **archive portable vérifiée** `F1G_separate_TD_buffer_and_F1F_evidence_20261121.tar.gz`, SHA256 `4717ff7e426bde1bce012fdd2e77fc13e6c8d37556cb921b3bd0543c1b242d2a`, et [manifest JSON](STAGE8F1G_NATIVE_TD_BUFFER_PROVENANCE_MANIFEST_2026-11-21.json). Les ZIP CI expirent après **90 jours**, les octets de la copie portable sont fournis à l'utilisateur et ne sont pas dans Git.

## Interprétation et règle d'arrêt

**Bilan causal conditionnel à huit contextes synthétiques** : F1F a montré **1/8 divergence de décision produite par les moyennes d'EffectsModel**, tandis que F1G montre **0/8 pour le masque des valeurs TD et 0/8 pour le contenu d'un tampon d'un épisode**. Ces résultats sont compatibles avec un accès direct aux effets appris pendant la simulation et l'évaluation des actions. Ce mécanisme **n'est pas une preuve de mémoire générale utile, d'amélioration de santé corporelle, de survie ou d'héritabilité**. Les huit contextes partagent tous **une seule racine d'expérience F1C** et ne constituent pas huit vies indépendantes. La parité financière est celle des unités `CognitiveWork`, non des instructions CPU chronométrées.

Aucun `run_life`, aucune naissance ni cohorte scientifique; pas de vraie mémoire historique des descendants G2, aucun saut de stade ou politique de vie F1 admise. F1D et F1E restent négatifs dans leur monde initial; Stage8-E2 reste strictement `STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0 / CLOSED_NO_RETRY`. Le projet reste sur son stade scientifique précédent; les preuves mécanistiques de laboratoire **ne promeuvent pas** une adaptation générale.
