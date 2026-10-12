# Stage12 #133 | Résultats exploratoires sommeil et consolidation (2026-10-12)

**Verdict technique ciblé : PASS. Verdict comportemental : effet substantiel de w_C observé, pertinence normative INCONCLUSIVE. Validation scientifique finale : NON EFFECTUÉE. Stage 12 et M-11 restent non certifiés.**

## Sources figées et preuve

- Préenregistrement antérieur aux mesures : `docs/research/stage12-issue133-sleep-prereg-2026-10-12.fr.md`, commit `d358510d1fcbb43dd190285b6b37630a7e5874fc`.
- Code exécuté : `36e8c8372f0c3a18ea1b228ae0c62e86027d0c08`.
- [PR #134](https://github.com/josselin-orta-lab/individual-zero/pull/134) ; [Actions campagne](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38305576307).
- [ZIP Python 3.11](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38305576307/artifacts/11772461623) ; [ZIP Python 3.12](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38305576307/artifacts/11772292057). Chaque archive contient 4 journaux, 4 WAL, 4 rapports et manifeste récapitulatif.
- Audit externe au processus de la vie : 4/4 vies par version, 50 pas physiques réellement appliqués/vie, aucun échec d'audit, SHA-256 des journaux égaux à leurs manifestes, reproductibilité exacte entre les deux versions.
- **Unité expérimentale : une vie distincte par configuration, donc N=4 configurations.** Python 3.12 réplique les mesures de 3.11 sans créer quatre traitements nouveaux. Aucun tirage aléatoire véritable.

## Résultats observés par version

| sixpass | w_C | se_deplacer | dormir | entrées/réveils | checkpoints validés | h publié | épisodes présents en fin |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| désactivé | 0,5 | 3 | 47 | 16/15 | 0 | 0 | 24 |
| désactivé | 0 | 36 | 14 | 7/7 | 0 | 0 | 24 |
| activé | 0,5 | 3 | 47 | 16/15 | 16 | 2 | 24 |
| activé | 0 | 36 | 14 | 7/7 | 7 | 1 | 24 |

Au total : **200 transitions physiques/version**, huit vies analysées sous les deux interpréteurs. L'activation de h résulte d'une transaction six passes validée, non d'une simple action dormir. La mesure `episodes=24` désigne les épisodes résidant dans Memory, **pas** le nombre nécessairement encore non consolidé : leur interprétation exige la comparaison aux `consolidated_episode_refs` de h.

## Hypothèses préenregistrées

**H133-A : SUPPORTED, sous les conditions étudiées.** Sans paire de politiques six passes, aucun checkpoint ni commit h même lorsque la pression monte. Cela indique le rôle décisif de la configuration optionnelle, pas une panne de l'algorithme.

**H133-B : SUPPORTED pour l'exécution technique, généralisation INCONCLUSIVE.** Six passes activées produisent 16 checkpoints et 2 publications h avec w_C=0,5 ; 7 checkpoints et 1 publication avec w_C=0. Aucun commit h n'est compté sans progression de passe : l'invariant doit aussi être confronté aux audits de six passes dédiés et aux injections d'interruption pour certifier toute condition adversariale.

**H133-C : SUPPORTED pour la sélection d'actions.** Abaisser expérimentalement le poids de consolidation de 0,5 à zéro réduit dormir de 47 à 14 actions par 50 pas, à politiques six passes égales : différence descriptive de **33 pas**, soit **66 points de pourcentage**. Cela ouvre des interactions veille/exploration qui n'étaient pas visibles dans le référentiel initial. Toutefois, w_C nul ne doit pas être promu en comportement normatif sans protocole nouveau : il supprime complètement la contribution des épisodes en attente à la pression de sommeil.

**H133-D : non démontrée.** Les publications h ont lieu dans les deux politiques six passes, mais la présence de publications seules ne prouve ni une normalisation durable de p_cons, ni que la consolidation a fini le travail utile. En configuration six passes activée, la proportion de temps dormi n'est pas réduite à w_C constant au cours de ces 50 pas.

**H133-E : PASS ciblé des quatre vies/version.** Pas physiques fermés, journaux et WAL conservés, aucun résultat ressuscité, aucune attribution Oracle injectée.

## Explication mécanistique et limites

Le fichier `src/lab/stage10_reference_fixture.py` utilise `consolidation_weight=0.5`, `unconsolidated_episode_reference=2`, `memory_saturation_reference=1`. La pression p_cons sature dès que les épisodes vécus s'accumulent. Son poids 0,5 dans P-40 maintient une motivation `dormir` fortement compétitive même après fatigue réduite à zéro. La limite maximale de durée impose un réveil mais ne désactive pas cette motivation à la délibération suivante.

Activer les politiques de six passes peut conduire à de vrais commits h, **sans que cela réduise nécessairement le temps de sommeil** : des épisodes arrivent en veille, l'occupation Memory reste élevée et le nombre de cellules est limité. L'expérience ne prouve pas qu'une réduction de w_C améliore la santé cognitive ; davantage de réveils ne constitue pas un indicateur de bien-être.

## Décision / chantiers

1. Garder l'issue **#133 ouverte** pour l'étude des seuils, du nombre d'épisodes encore non consolidés, de l'occupation Memory, de la quantité effectivement consolidée, des coûts UC et de la gestion d'urgence.
2. Étudier un calibrage non nul de w_C et/ou des dénominateurs P-40 par protocole distinct, avec plusieurs mondes et trajectoires, des métriques a priori de gain (sommeil utile, mémoire consolidée, capacité à chercher/boire, absence de risque létal).
3. Rendre explicite au niveau du banc de développement que la fixture standard n'active pas les six passes; choisir une configuration intégrée versionnée quand une campagne prétend tester la consolidation.
4. Préserver la conservation du journal, la mortalité, le coût P-42, la priorité des réveils et l'absence de duplication de motivations corporelles. Ne pas ajouter de période réfractaire artificielle ni un bonus à l'état éveillé.
5. **Proposition de clarification MVP uniquement** : distinguer disponibilité du mécanisme six passes, activation effective par configuration et amélioration cognitive scientifiquement mesurée. Ne pas modifier v1.3.1 sans accord opérateur.

Ce rapport est rédigé **après** les mesures. Il ne modifie pas le préenregistrement, ne ferme pas l'issue et ne constitue pas l'acceptation Stage 12.
