# A2.30-ZN : préenregistrement d'une relecture indépendante des boucles physiques ZM

**15 octobre 2026. APRÈS connaissance des résultats ZM et AVANT code, tests et CI ZN.** Audit secondaire **rétrospectif en lecture seule**, pas une nouvelle étude physique, pas une nouvelle naissance ni un vrai apprentissage I0.

## Archives source entièrement identifiées

**Run original ZM :** [GitHub Actions #38788052317](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38788052317), code `daf800007330b420b92578270e0ec4f2ae37e410`, archives `a230zm-py3.11` et `a230zm-py3.12`, chacune contenant `a230zm-physical-loop-worlds.json` et `a230zm-summary.json`. Les deux résumés du journal CI ont publié les **mêmes** comptes, mais **l'égalité byte-à-byte de leurs deux fichiers complets n'est pas encore vérifiée indépendamment** à l'instant du préenregistrement. L'empreinte canonique des 64 mondes ZM est publiquement figée dans les deux journaux :
`b253fca92417b7b00f277b958cdf7c37f7ca9dd07b0749ec80c105280a65d6ff`.

Résultat déjà connu AVANT ZN : 64 mondes, 256 déplacements de boucles et quatre déplacements de validation t5, 64 requêtes du vrai Stage6 ; 4/64 états complets égaux après retour, 60/64 états modifiés malgré positions égales, 4/64 `plan_found` spatial à un pas et 60/64 `incomplete_model`, quatre vérifications physiques exactes, 0 décès et 0 ingestion.

## Vérificateur strictement distinct du runner, sans exécution

Le reviewer ne doit importer **ni `run_stage12_issue110_b_a230zm_exact_reentry`, ni `WorldBody`, ni `Equipment`, ni `SimulatorPlanner`, ni `Stage12Runtime`, ni Oracle** ; seul l'utilitaire de sérialisation causale déterministe peut être partagé. Il doit :
1. Télécharger depuis le **run originel** les deux archives, contrôler l'unicité des noms, **l'égalité octet par octet** pour chaque fichier (si elle s'avère fausse : FAIL explicite, pas suppression de divergence), l'empreinte canonique du contenu `worlds` et la SHA déclarée originale du code ZM.
2. Réimplémenter indépendamment les critères de première perception admissible (`SimulationState` complet) et la clé `sha256(canonical({"state": ..., "command": ...}))`, puis les commandes candidates Stage6 depuis les voisins, ressources, inventaire et les primitives disponibles. Ne jamais masquer `energy`, `food`, `water` ou `is_night`.
3. Vérifier **tous les 64 mondes /260 reçus physiques** : quatre mouvements consécutifs east/south/west/north, hash de chaque `EquipmentCorpusExample`, absence de terminal, les coordonnées, ressources locales et inventaire aux t1/t5, la variation des quatre composantes corporelles, les drapeaux jour/nuit, l'identité du monde et des six facteurs ; le cinquième mouvement n'existe **que pour les quatre cellules pré-enregistrées** à coût/décroissance nuls et jour maintenu.
4. Reconstruire les **4 paires state×command de chaque monde** en mémoire de laboratoire, vérifier qu'aucun exemple d'un autre monde n'est présent, refuser toute collision incompatible, et compter les candidats à la racine t5 possédant un exemple exact. Confronter le compte au diagnostic Stage6 réel archivé, vérifier **4 `plan_found` spatiaux en un pas vers l'est** et **60 `incomplete_model`**. Comparer la prédiction enregistrée et le **reçu physique du cinquième pas** pour les quatre témoins positifs, octet par octet pour `next_state`.
5. Refuser l'interprétation « 64 retours géographiques = 64 racines de modèle connues », toute prétention de sécurité globale, toute ingestion B, toute commande envoyée depuis le shadow, toute UC vécue ou naissance I0.

## Falsifications exigées

Tester le rejet d'au moins : SHA canonique ZM inventé, octets de fichier altérés, monde factoriel doublonné, énergie de marche falsifiée, perte de faim/eau ignorée, `is_night` effacé, ressource fantôme, transition importée d'un autre monde, résultat physique falsifié mais compteur inchangé, exemple de mouvement terminal, fifth-step anticipé dans la table, `plan_found` forgé sur une racine corporelle nouvelle, fausse commande de nourriture B, prétendu certificat `safe`, UC vécues ou observation postmortem. Les cas doivent produire un échec explicite.

**PASS ZN** seulement après exécution sous Python 3.11/3.12 avec contrôles négatifs effectivement refusés et reconstitution complète des dénominateurs de ZM. ZN **ne** peut prouver à lui seul que les actions ont été exécutées dans la physique : la provenance repose sur le runner original ZM et sa CI. Il ne démontre pas qu'un véritable I0 vivant possède ce corpus idéal de laboratoire.

**A2.30 PARTIELLE, Stage12 PARTIAL, issue #110 OPEN ; déploiement cognitif NO-GO.** Aucun changement normatif ni fusion ; les deux Pythons sont des répétitions déterministes de mêmes facteurs, pas deux cohortes statistiques.
