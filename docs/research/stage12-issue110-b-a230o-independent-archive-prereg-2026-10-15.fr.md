# A2.30-O : préenregistrement d'un audit indépendant des archives N

**15 octobre 2026, avant le code O.** L'expérience scientifique N est **déjà achevée** au code \`d62a92d7f0a773a411de2e65ce2c2467be9efb48\`, run [#38726664498](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38726664498), succès Python 3.11 et 3.12. **Les résultats N sont déjà connus avant cet audit** : 42 mondes prénataux / 54 transitions appliquées; 62 mondes de test / 82 transitions; couverture des intervalles 54/62, baseline exacte 18/62, interpolation 28/28, 20 intervalles manqués (12 toxicité cachée et 8 dérive de décroissance), 12 terminalités hors ensemble (6 mouvement létal, 6 ingestion mortelle), 18 faux positifs d'un **proxy externe naïf** assimilant \`confidence=1.0\` à une certification de sécurité. Le prototype ne délivre **aucun certificat**.

L'audit O ne compte **aucune nouvelle vie, aucun nouveau pas I0, aucun nouveau monde ni transition physique**. Il recontrôle en lecture seule les artefacts originaux A2.30-N (et non un replay de mondes) : \`a230n-py3.11\` et \`a230n-py3.12\`. Empreintes SHA-256 des trois JSON contrôlées localement avant ce protocole :

| Fichier (identique sous les deux Python) | SHA-256 de ses octets |
|---|---|
| \`a230n-training-manifest.json\` | \`948dc97de8ff6fc4\` + suffixe complet à fixer/contrôler par l'auditeur |
| \`a230n-heldout-physical-results.json\` | \`2c40322e5b4810cc\` + suffixe complet |
| \`a230n-summary.json\` | \`719978de013674e3\` + suffixe complet |

Les préfixes ci-dessus ne sont **pas** des empreintes complètes suffisantes en production; l'auditeur doit recalculer les digests sur chaque fichier et comparer intégralement les deux versions Python. Pour rendre le contrôle falsifiable, une divergence des octets ou des catégories fausse la campagne O.

## Audit à développer indépendamment du prédicteur

1. Vérifier l'identité du run source, du SHA de code N, le schéma et le compte des exemples, les 42 identifiants d'entraînement, les 62 identifiants de test, les 136 pas physiques *déclarés*, et l'absence de recouvrement d'identifiants. Recouper les empreintes causales de chaque entrée/commande, des 42 sorties enregistrées et des 62 résultats de test à partir des données archivées. Reconstituer le SHA du corpus physique d'entraînement.
2. Implémenter **une nouvelle fonction indépendante** qui calcule la clé de groupement uniquement sur les champs perceptibles préenregistrés (commande exacte, \`is_night\`, voisin directionnel passable/créature, ressource présente, outil, inventaire de nourriture, eau visible, abri visible). Ne pas importer le code du prototype ni l'utiliser comme oracle de test.
3. Reconstituer les 11 deltas physiques (2 positionnels, 4 corporels, 5 d'inventaire) et les enveloppes \`min/max\` **à partir des 42 entrées d'entraînement seulement**. Vérifier pour chacun des 62 cas de test les bornes, l'effectif, les étiquettes de risque, les abstentions, les dimensions manquées, les terminalités hors ensemble, les largeurs d'intervalles et chaque compteur de la matrice originale.
4. Reconstituer la table exacte naïve *indépendamment*, avec un dictionnaire de clés et conséquences originales. Ne pas appeler \`FrozenTableEquipment.predict\` dans l'auditeur; vérifier les occurrences où le proxy EXTERNE « \`confidence=1.0\` ⇒ sûr » se tromperait. L'auditeur ne doit **pas** attribuer ce jugement au Stage6 réel, dont le \`risk_status\` reste inconnu.
5. Contrôles négatifs : une fausse empreinte d'état, un intervalle inversé, un \`certifies_safe=true\`, une prédiction disponible hors groupe, un statut \`terminal\` falsifié ou un exemple de test ajouté à l'entraînement doivent invalider l'audit; comparer les deux versions Python *octet à octet*.

**Résultat O attendu :** preuve de consistance indépendante des métriques et des artefacts, **pas** preuve causale autonome de l'application des transitions, qui dépend encore de \`WorldBody.apply\` dans le runner N. Si le corpus n'est pas physiquement attestable indépendamment avec ces seules données, le signaler. Toute confirmation des chiffres connus de N reste un **recalcul des mêmes conditions**, pas un nouveau succès reproductif indépendant.

**A2.30 PARTIELLE**, Stage12 PARTIAL, issue #110 OPEN, PR #188 DRAFT. Aucun changement du runtime, de la spécification, du jugement subjectif ou d'un modèle cognitif.
