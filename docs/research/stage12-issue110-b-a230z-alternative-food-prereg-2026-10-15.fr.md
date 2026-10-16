# A2.30-Z : préenregistrement prospectif, alternatives alimentaires accessibles et coût d'une décision prudente

**Date : 2026-10-15.** Base figée : PR #194, commit `267fe2b5a744827146e972c14e6edab9fd3a3d96`. **Préenregistrement AVANT code, données, tests et résultats Z**. Les résultats W/X/Y sont déjà connus : quatre sondes de `berry_a` sans ingestion ne distinguent pas cinq effets latents, malgré des témoins perceptifs positifs. Ne pas les compter comme observations nouvelles Z.

## Hypothèse falsifiable et question

**H-Z1** : une politique bornée qui reconnaît une **ressource alimentaire alternative réellement visible et physiquement accessible** peut, dans au moins une cellule contrôlée, atteindre un gain alimentaire avec survie en évitant le préfixe toxique `berry_a`. Cela n'implique pas que l'autre ressource soit sûre par nature. **H-Z0** : aucun cas testé n'établit simultanément l'accessibilité, l'exécution physique, la survie et le gain alimentaire. Une ressource qui n'est visible que dans la configuration du laboratoire, mais absente du `SimulationState` de décision, ne compte pas comme alternative disponible.

**H-Z2 (distincte)** : le vrai Stage6 peut-il former une première arête de plan prévisible pour cette alternative, avec **uniquement** l'historique causal effectivement vécu par l'individu considéré ? Le succès d'un laboratoire précommandant `collecter → manger` ne vaut jamais validation de H-Z2. Le manque d'arête `incomplete_model` reste un résultat admissible et doit être publié, non contourné par un modèle idéal injecté.

## Cohorte, témoins et mesures préengagées

Préparer une cohorte déterministe **indépendante des 92 mondes W**, avec au moins ces bras factoriels, en fixant les nombres définitifs et les graines dans le code AVANT de lancer la première physique Z :
- `berry_a` seul, cinq effets latents de référence ; témoin d'aliasing dangereux.
- `berry_a` et `berry_b` tous deux visibles, avec `berry_b` accessible et un effet physique explicitement configuré ; témoin d'alternative réelle, mais **sans donner au décideur le paramètre caché de sécurité**.
- Même paire visible, mais `berry_b` bloquée par un obstacle visible ; témoin de fausse accessibilité.
- `berry_b` visible après déplacement seulement ; témoin de coût et de nécessité d'exploration physique.
- Même espèce `berry_b` avec au moins deux effets cachés différents et même observation initiale ; témoin contre la fausse inférence « autre espèce = sûr ».

Pour chaque cellule, conserver `pre_action_stage3_state` complet, provenance des observations, chemin des commandes, capture `SymbolicPerception`, coût corporel, coût UC **uniquement si une vraie cognition I0 est exécutée**, transitions `WorldBody.apply`, mortalité et résultat alimentaire. Conserver la trace de décès seulement dans le journal externe : **aucune perception postmortem vécue**. Les informations `latent_external_only`, la configuration physique, les reçus Oracle et les résultats futurs ne doivent jamais entrer dans le choix de politique.

Distinguer strictement trois niveaux de résultat : **(1) existence physique d'un chemin alimentaire** précommandé par le banc ; **(2) possibilité de sélectionner le chemin à partir de perceptions réellement disponibles** sans certitude de sécurité indue ; **(3) capacité de Stage6/I0 à sélectionner et exécuter lui-même ce chemin avec mémoire et UC vécues**. Ne jamais faire passer (1) pour (2) ou (3).

## Contrôles de falsification obligatoires

- Un changement du seul effet caché de `berry_b` ne doit **pas** modifier les observations avant exposition ni la décision d'une politique first-person déterministe.
- Retirer `berry_b` des ressources visibles ou ajouter un obstacle visible doit être détecté ; un banc qui exécute malgré tout un plan physiquement impossible doit être refusé.
- Détruire la provenance des connaissances antérieures, injecter une étiquette `safe` non vécue ou une donnée Oracle dans Stage6 doit faire échouer les contrôles.
- Une politique qui échoue, meurt ou renonce à agir doit rester comptée dans le dénominateur, sans filtrage a posteriori des seules vies survivantes.
- Mesurer et déclarer séparément coûts physiques, UC réelles, durée en pas et actions refusées. Si I0 ne s'exécute pas, **UC = non mesuré**.
- Rejouer les archives sous Python 3.11/3.12, puis produire un audit de lecture **indépendant** du runner ; la répétition déterministe n'est pas une nouvelle cohorte statistique.
- Comparer explicitement les branches `berry_a` et `berry_b` à historique subjectif équivalent, et rapporter les cas où aucune garantie universelle n'est possible.

## Critères de décision

**Z physique PASS** seulement si les scénarios prédéclarés, leurs témoins, la provenance first-person, les captures de décès et les coûts sont intégralement vérifiables avec les deux interpréteurs. **Z décision PASS** seulement si au moins une alternative est choisie sur un signal préexposition réellement accessible et si le protocole distingue correctement le cas de même signal mais d'effet dangereux caché. **Z Stage6 PASS** uniquement avec exécution du véritable planificateur sur une mémoire causalement admissible, première arête réelle, action non imposée par le banc et reçus UC observés ; autrement `NOT ESTABLISHED`.

L'absence d'alternative démontrée ne justifie ni une fuite Oracle ni une garantie de sécurité fabriquée. Ne modifier ni la norme `docs/architecture/reference/en/mvp-specification-v1.3.1.md`, ni `src/i0`, ni les contrats Stage6/Stage9/Stage12, ni la mortalité WAL sans autorisation opérateur explicite.

**Statut initial : protocole Z uniquement, aucune donnée Z acquise, aucun PASS revendiqué. A2.30 PARTIELLE ; Stage12 PARTIAL ; issue #110 OPEN ; déploiement cognitif NO-GO.**
