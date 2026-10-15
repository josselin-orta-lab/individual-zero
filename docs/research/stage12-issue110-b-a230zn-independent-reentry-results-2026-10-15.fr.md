# A2.30-ZN : confirmation indépendante des 64 boucles exactes ZM

**15 octobre 2026.** **Préenregistrement APRÈS résultats ZM connus mais AVANT code ZN**, au commit `dda3bef49b3d09514a63f626de5c6eea0b95c01c`. Audit **strictement rétrospectif** sur les fichiers originaux du [run ZM #38788052317](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38788052317). Vérificateur indépendant : `scripts/audit_stage12_issue110_b_a230zn_independent_reentry.py`. CI de réception [#38789049839](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38789049839) : **24 tests PASS sous Python 3.11 et 3.12**, mêmes résultats.

## Preuve immuable des fichiers d'origine

Pour chacun des deux fichiers de sortie physiques du run **ZM original** (et non ceux d'une réexécution postérieure), l'auditeur compare les archives téléchargées `a230zm-py3.11` et `a230zm-py3.12` **octet par octet**, puis leurs SHA-256 complets :

| Fichier original | SHA-256 brut du fichier |
|---|---|
| `a230zm-physical-loop-worlds.json` | `1938e2e673f59f831855210d9c9f9cb0e10b275bdc6013a798332869c64848b4` |
| `a230zm-summary.json` | `39d6becd46b2b8966c609d24ba2921b836caf223542cd4900734a172f54760cc` |

Empreinte du contenu canonique des 64 mondes, déjà connue **avant la construction de ZN** et retrouvée indépendamment :
`b253fca92417b7b00f277b958cdf7c37f7ca9dd07b0749ec80c105280a65d6ff`.

Le code source original ZM est précisément `daf800007330b420b92578270e0ec4f2ae37e410`. Le reviewer **n'importe pas** le runner, `WorldBody`, `Equipment`, `SimulatorPlanner` ou le runtime cognitif. Il ne crée donc **aucun** monde physique, aucun nouvel acte ni individu I0.

## Reconstitution indépendante du problème de clé

L'auditeur reconstruit depuis les seuls JSON les 64 mondes et leur factorisation, les **260 empreintes d'exemples physiques**, l'intégralité des chaînes `état → commande → observation suivante`, les coûts du corps et les changements de `is_night`, puis réimplémente les commandes candidates et les **64 clés de racine `SimulationState×PrimitiveCommand`**.

**Toutes les comparaisons ZM sont retrouvées :** 64 retours géographiques, **4 retours à perception complète identique**, **60 retours à perception modifiée**, **4 racines exactes connues** et **4 plans spatiaux d'un pas attestés**, **60 racines sans premier pas connues** et **60 `incomplete_model`**, quatre effets physiques à t5 égaux aux conséquences initialement prédites. **4** des échecs de réentrée surviennent avec **uniquement le passage à la nuit**, et les **56** autres avec dérive d'au moins une variable corporelle.

Les sorties du planificateur ont été **enregistrées par 64 véritables recherches Stage6 lors de ZM**, mais le reviewer ZN ne relance pas lui-même le planificateur. Il recalcule seul les compteurs de racine et recoupe les commandes et sorties archivées. Il n'établit donc pas une seconde preuve indépendante de l'exécution de Stage6 ou de la physique.

## Contrôles adversariaux et erreurs d'audit exposées

**24 tests PASS dans les deux versions**, dont altération de l'archive, falsification des empreintes, duplication de bras, utilisation abusive des seules coordonnées, omission de la dérive énergétique ou alimentaire, suppression de `is_night`, ressource fantôme, exemple d'un autre monde, décès fictif, fuite du cinquième pas dans l'apprentissage antérieur, faux `plan_found`, allégation d'ingestion, sécurité garantie, commande dispatchée et UC vécues inventées.

Deux tentatives de l'auditeur ont été **rouges avant stabilisation** : [#38788910902](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38788910902) à cause du décalage entre `night_start_step` (indice de jour à base zéro) et `t_monde` (pas à base un), et [#38789030402](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38789030402) à cause d'un libellé d'erreur trop spécifique dans un test négatif (la falsification était bien refusée). Corrigés **sans modifier les données originales, les critères pré-enregistrés, les métriques de ZM ou ses témoins physiques**. Ne pas masquer les CI initiales échouées.

## Limite scientifique

Un audit cryptographique et sémantique de reçus archivés ne démontre **pas à lui seul** que `WorldBody.apply` a eu lieu : l'exécution physique est attestée par la CI originale ZM. Les deux Pythons rejouent **les mêmes 64 facteurs**, ils ne sont pas deux nouvelles cohortes. Les boucles ZM et ZN sont **hors de la cognition autonome I0**. Les quatre prédictions confirmées prouvent une exactitude physique locale en monde contrôlé, **aucune garantie extrapolée de sûreté**.

**Verdict ZN : PASS technique sur intégrité et recalcul indépendant du résultat ZM; A2.30 PARTIELLE, Stage12 PARTIAL, issue #110 OPEN, déploiement cognitif NO-GO.**
