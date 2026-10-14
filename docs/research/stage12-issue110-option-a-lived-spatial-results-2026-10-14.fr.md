# Individual Zero #110 / Option A : première attribution spatiale personnelle vécue, rapport prospectif

**Date : 14 octobre 2026. Statut : validation exploratoire positive partielle pour `self`, attribution extérieure `world` toujours non démontrée.** PR [#155](https://github.com/josselin-orta-lab/individual-zero/pull/155) sur branche de recherche issue de #153, sans fusion `main`. Cible normative GA-SPATIAL-01 candidate, aucune réception opérateur.

## 1. Préenregistrement et provenance

La campagne a été préenregistrée **avant le code du nouveau runner** dans `docs/research/stage12-issue110-option-a-first-planning-state-prereg-2026-10-14.fr.md`, commit `63382aae8242ee9a18b3953655cba9ece2060d06`. Le protocole fixait un corpus Equipment exact constitué **hors de l'individu et avant naissance** par vraies transitions WorldBody : `north -> east -> collect -> eat` pour nourriture ou `north -> east -> boire` pour eau. La cible est (3,1), observée après un possible premier mouvement autonome `north` de (2,2) à (2,1). Il ne s'agit ni d'entraînement en vie autonome ni d'action dirigée par le laboratoire.

Source exacte de la première campagne : [GitHub Actions #38487115066](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38487115066), SHA `dc59ef37fb8eb1d332c38800716f776175ddef4e`. **SUCCESS Python 3.11 et 3.12**, quatre vies neuves par interpréteur, mêmes configurations déterministes (ne pas considérer les interpréteurs comme huit individus indépendants). Les archives originales `issue110-first-state-py3.11` et `issue110-first-state-py3.12` ont été récupérées puis leurs quatre JSONL comparés octet par octet.

| Monde | SHA256 des JSONL, identique sur 3.11/3.12 |
| --- | --- |
| near_food_blocked | `7fe27a505a5fa6d5926536367782a65f0627f8134dc4ecce4a79137b713237a4` |
| near_food_free | `b072cb92654c2c30bc848839f67556d65b3deadbdd8a15bae161a8fac0ccc86c` |
| near_water_blocked | `d1db19216346ef6d783f5a9326152e616a6732a26104d1d22bc7fa89b7bf21dd` |
| near_water_free | `79dd844f41cd9eed56fcb4d8f7d6b7cdd54ea60337adafe7c1e694d0ad660833` |

**Défaut de reporting détecté et corrigé APRÈS cette première exécution :** l'ancien résumé nommait `verified_one_step_resource_gains` l'ensemble des réussites incluant les sous-objectifs spatiaux, et le nom de dossier des vies eau indiquait `water70` malgré un état physique `water20`. Ces libellés étaient trompeurs même si les transitions et verdicts des audits d'origine étaient cohérents. Correctifs ultérieurs : sortie séparée spatial/corporel dans `Stage12GoalProgressAudit.as_dict()` (audit v2 conditionnel), et nom/metadata initial_water conformes à la vraie config. Les premières archives **ne sont jamais réécrites** ; les nouvelles CI doivent être référencées par leur propre SHA.

## 2. Mesures sur les quatre vies, pas de double comptage entre Pythons

| Mesure | Total |
| --- | ---: |
| Transitions WorldBody réellement appliquées | 200 |
| Vies auditées | 4/4 |
| Options Stage 6 ayant un `proposal_ref` | 5 |
| Préenregistrements de critère d'objectif | 5 |
| **Sous-objectifs spatiaux** préenregistrés | **2** |
| Progressions spatiales `success` | **2** |
| Progressions spatiales `failure` | 0 |
| Gains corporels stricts `success` | **2** |
| Non-gains corporels `failure` | **1** |
| Jugements originaux Action Control `self` | **3** |
| Jugements originaux Action Control `unknown` | 2 |
| Jugements originaux Action Control `world` | **0** |
| Frais d'évaluation d'agence acceptés (UC, incluant supplément spatial) | 7 |
| Jointures facturées (UC) | 3 |
| Couples `(success,self)` effectivement admis | 3 |
| Couples consommés au diagnostic du pas suivant | **2** |
| Couples expirés sans rétrodiagnostic à cause du sommeil | 1 |
| Diagnostics positifs/négatifs de biais publiés | 0 |

Le coût propre du critère spatial `stage12_spatial_goal_preregistration` vaut **1 UC par intention**, donc 2 UC de cette opération, en plus des 7 UC d'agence et 3 UC de jointure. Toutes les preuves de coût sont présentes dans les journaux canoniques. Le résultat `attribution_bias=None` reste obligatoire : dans chaque vie, le seuil configuré exige 2 références uniques `success` ET 2 `failure` admissibles, ce qui n'est obtenu nulle part.

### Séquence réelle de la vie nourriture libre

- **Pas 1** : activation du but `eat`, mouvement exploratoire `north` réellement choisi et appliqué.
- **Pas 2** : Stage 6 produit un plan de but depuis la position vécue (2,1) ; I0 choisit `east` vers la baie **directement perçue** en (3,1). L'intention spatiale est préenregistrée avant la transition et le coût UC est facturé.
- **Pas 3** : capture à (3,1) ; l'auditeur établit une diminution du critère de distance (1 -> 0), `spatial_progress=success`. Action Control interprète indépendamment le déplacement compatible avec la copie efférente et formule `self` avec sa propre UC ; première jointure `(success,self)` admise. I0 choisit et applique `collecter`.
- **Pas 4** : `food` corporel n'augmente pas ; le critère corporel précédent est `failure` et Action Control formule `unknown`. Le couple spatial positif du pas 3 est appliqué par le diagnostic publié au pas 4. I0 choisit `manger`.
- **Pas 5** : gain réel de `food` selon le critère préenregistré, jugement `self` distinct fondé sur la baisse d'inventaire perçue, jointure `(success,self)` admise.
- **Pas 6** : sommeil autorisé, aucune cognition nouvelle ni diagnostic ; le couple du pas 5 expire, reçu vérifiable au réveil suivant. Il ne peut pas entrer rétroactivement dans le détecteur.

### Vie eau libre

Le but `drink` se matérialise en plan au pas 2 ; I0 exécute le déplacement vers l'eau perçue puis `boire` dans l'environnement physique. Au pas 3, `spatial_progress=success` et jugement `self` ; le couple correspondant est appliqué au diagnostic du pas 4. Le succès corporel d'eau est indépendant ; Action Control conserve un jugement `unknown` sur cette ingestion puisque la politique d'inventaire alimentaire ne prouve rien à propos de l'eau.

### Mondes bloqués

Ni `near_food_blocked` ni `near_water_blocked` n'a donné de plan Stage6 ni de tentative autonome admise vers la cellule Est non passable. Les individus ont continué à explorer et dormir. **Aucun `world` ne peut être inventé** ; les données sont négatives et scientifiquement inconclusives sur ce mécanisme.

## 3. Limites résiduelles et attention particulière aux références

Les identifiants internes `Stage12Runtime.individual_id` sont actuellement dérivés d'une constante de runtime ; il est possible que deux vies distinctes sur des journaux/WAL séparés produisent le **même identifiant d'événement déterministe** pour une séquence exactement identique. Les références doivent donc être interprétées **dans le périmètre d'une vie/journal** et ne doivent jamais être utilisées comme identifiants globaux distincts pour agréger la validité scientifique. Dans les deux vies libres, un couple du pas 3 partage effectivement un identifiant calculé identique. Chaque vie a son archive et son hash de journal distinct, mais l'unicité **globale** de la référence doit être investiguée avant de déclarer un résultat statistique multi-vies.

La campagne prouve un mécanisme local de jugement subjectif `self`, pas la vérité causale physique objective. Les tests positifs de `world` sur commandes de fixtures sont seulement logiciels, les rejets de falsifications rechaînées sont sémantiques, pas de preuve métaphysique externe. La nouvelle intégration spatiale nécessite encore une campagne M-11 `os._exit` et reprise froide sous journal durable, une plus grande couverture de trajectoires et de jugements `world`, puis réception opérateur.

**Verdict : première preuve exploratoire favorable pour la chaîne spatiale personnelle autonome. Pas de validation de `world`, pas de calibration scientifique du détecteur, Stage12 non reçu, issue #110 ouverte, Stage9 scientifique NO-GO.**
