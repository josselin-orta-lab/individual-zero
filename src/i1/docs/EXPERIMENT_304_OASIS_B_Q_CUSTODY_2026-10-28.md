# I1 #304: attribution rétrospective bornée de la première divergence Oasis B

Date : 28 octobre 2026. Base : `71bd39ffca92338675a7d75e4e08267181ca8f6b` (PR #595 fusionnée). Cette étape ajoute uniquement des champs au rapport **du même test M11 déjà préenregistré**, sans naissance supplémentaire ni changement cognitif.

## Question

Dans la paire `oasis/b` de #595, qu'a exactement lu Stage8, avant l'admission physique de `manger berry_a` contre `dormir` au pas 11 ? Quelles signatures TD effectivement mises à jour, quels Q appris et quelles preuves Competition payées participent à ce pas ?

Cette question est une **analyse mécanistique de découverte**, choisie après observation de la divergence. Elle ne constitue pas une nouvelle expérience confirmatoire et n'autorise ni reclassification de #305 en crédit instrumental démontré, ni hausse du niveau de preuve global.

## Lecture instrumentée sans nouvelle intervention

Dans le seul pas 11 de `oasis/b`, publier comme rapport opérateur :

- Les lignes authentiques `stage8_option_evaluation` des deux bras, indexées `(pas, cycle, option_ref)`, contenant `learning_signature`, statut appris, valeur Q, résultat et preuve.
- Les preuves `competition_cycle` correspondant aux mêmes candidats et cycles, seuils et franchissements réellement calculés.
- Les publications `td_update_published` déjà inscrites dans le journal causal canonique jusqu'à ce premier embranchement, y compris signature antérieure/suivante, delta, retour et signatures modifiées.
- Les admissions Action Control authentifiées des deux bras et les lectures Q réellement masquées au même pas.
- Les bornes M11, les égalités de corps/TD/objectif/P-40/Competition préaction et l'absence de rollback déjà exigées par le témoin existant.

Ne pas convertir l'apparition de la signature `collecter` en une preuve que sa valeur a déterminé `manger` : l'ablation #595 masque **toutes** les lectures Q de Stage8, pas une signature unique. Un mécanisme d'attribution sélective demanderait une nouvelle expérience spécifiée avant naissance, et seulement si les traces existantes sont insuffisantes pour départager les hypothèses.

## Verdicts autorisés

- `MECHANISM_EXPOSED` si le TD et les évaluations Stage8/Competition sont authentifiés.
- `SIGNATURE_CAUSALITY_NOT_ISOLATED` tant que plusieurs Q peuvent contribuer.
- `INSTRUMENTAL_REUSE_NOT_ESTABLISHED` en l'absence d'une deuxième occasion naturelle `collecter` réellement proposée, admise et bénéfique.
- Aucun GO adaptatif ou robuste, aucun réglage du moteur sur cette base.

Cette instrumentation descriptive ne change pas les mondes `oasis`/`foraging`, les deux identités, les 18 pas maximum ni la politique du moteur, et conserve les résultats négatifs. Gates : les quatre contrôles exact-head Python 3.11/3.12, audit des rapports et du diff, conformément à #348.
