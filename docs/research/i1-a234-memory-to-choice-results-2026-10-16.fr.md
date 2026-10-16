# I1 A2.34 — Résultats de l'audit mémoire → décision (2026-10-16)

**Statut scientifique : apprentissage décisionnel NON DÉMONTRÉ.** La chaîne mémorielle initiale fonctionne ; la consommation effective par l'évaluation des options factorisées reste absente.

Protocole préenregistré : `docs/research/i1-a234-memory-to-choice-prereg-2026-10-16.en.md`, commit `7d75b044577840caddfe356fa03df53d81e65ae8`, avant développement du runner. Correction purement technique du nom du runner dans le workflow au commit `bbbb9869638653dd6193174348773d2dcfb9bcb3` (premier job en échec avant toute vie). Une mise à jour du scoreur a ensuite ajouté des décomptes de rappel et d'exploitation sans modification des cohortes ni des paramètres cognitifs, commit `2274fce41b0086397540ff1a7ee92db0673fa1ce`.

**Preuve :** [workflow scientifique A2.34](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38863631535), Python 3.11 et 3.12 : succès sur le même HEAD, avec artefacts et WALs par vie. Deux relectures déterministes ne sont pas deux réplications indépendantes.

## Population et effets

24 paires, 48 vies mortelles I1 distinctes ; 8 paires chacune pour FAILURE, INJURY et NOMINAL. Maximum neuf transitions physiques par vie : **432 transitions réellement exécutées** ; zéro mort, zéro exception, zéro journal invalide, zéro affirmation de sûreté/cause cachée non autorisée détectée. Empreinte du corpus physique externe d'entraînement `3ca910ef4a333d2c88c725650406c81c3a89ff391bc8cc7c9cd50b129f0a2784`. Ce corpus ne devient pas un vécu de I1.

### Entonnoir cognitif

| Étape | FAILURE | INJURY | NOMINAL | Interprétation |
|---|---:|---:|---:|---|
| Vies avec épisodes clôturés | 16/16 | 16/16 | 16/16 | Mémoire épisodique existante |
| Vies avec rappel spontané | 16/16 | 16/16 | 16/16 | Rappel de mémoire actif |
| Vies où le rappel figure dans `S_t` | 16/16 | 16/16 | 16/16 | Publication et passage dans la sélection Gatekeeper vérifiés |
| Événements de rappel spontanés | 64 | 64 | 64 | 192 rappels pour 48 vies |
| Évaluations d'options factorisées | 220 | 214 | 236 | 670 évaluations |
| Évaluations utilisant un `learned_value` | **0** | **0** | **0** | **Aucune exploitation d'une valeur apprise** |

Résultats physiques complémentaires : FAILURE exposé a huit premières collectes avec inventaire inchangé au suivi, contre zéro chez le contrôle ; INJURY exposé présente huit diminutions d'intégrité visibles au suivi, zéro chez le contrôle ; NOMINAL a les mêmes premières commandes dans les deux bras. Les expériences réellement vécues ne suffisent pas à établir une causalité précise ni une politique de danger acquise.

## Localisation architecturale du verrou

La projection autobiographique autorisée (Stage 7/11) alimente des épisodes qui sont effectivement clos puis rappelés. Le rappel est publié comme `Contribution` avec `signal_family=memory_recall`, `risk=0`, `value=0`, `urgency=0`. L'évaluateur expérimental `I1PartialEvidenceAdapter`, pour ses propres options factorisées, produit systématiquement `learned_value_status=unlearned`, `learned_value=None`, `simulated_value_status=unavailable` et une évidence instrumentale fixe `I1_SCORE=0.35`. Le fonctionnement des autres options et des contrôles Stage9/Action Control demeure distinct. **Un rappel enregistré n'est pas consommé comme preuve modifiant la valeur de cette option**.

La constatation est limitée à l'évaluateur expérimental d'I1 dans cette campagne. Elle ne démontre pas l'impossibilité pour les autres mécanismes Stage8, TD ou Stage9 d'apprendre, et n'établit pas que toute mémoire est causale ou discriminante. Il n'existe ici aucune preuve qu'I1 ait correctement inféré « cette case est dangereuse » ni qu'il ait appris à éviter un échec de collecte.

## Prochaine hypothèse, sans déploiement prématuré

Préenregistrer séparément A2.35 : une **liaison de preuve vécue ciblée** entre résultat proximal observé, épisode autobiographique accessible, action/contexte réellement comparables, évaluation d'option et Competition. Exiger une preuve de source et d'antériorité vérifiable, refuser toute causalité distale ou danger caché non discriminé, facturer UC, conserver la possibilité d'abstention et empêcher toute altération silencieuse des souvenirs historiques. Tester en parallèle une I1 sans nouveau mécanisme, sans modifier I0 ni Action Control, avec vraies vies et mesures des coûts/survie/biais.

**Disposition : I1 expérimental, activation générale NO-GO ; Stage 9 NO-GO et Stage 12 PARTIAL inchangés. La PR #219 demeure Draft ; aucun merge vers main.**
