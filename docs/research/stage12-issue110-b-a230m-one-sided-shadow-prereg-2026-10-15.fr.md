# A2.30-M : préenregistrement d'un témoin logiciel dérivé, apprentissage unilatéral

**15 octobre 2026, avant le code M.** Cette analyse est une **conséquence testable des contre-exemples déjà connus d'A2.30-L**, pas un jeu de données indépendant, une découverte prospective ni de nouveaux pas physiques. L1/L2 ont démontré : même `SimulationState × PrimitiveCommand` accessible, deux issues différentes dues à une cause cachée. Le trainer rejette correctement un corpus comportant les **deux** issues. L'expérience M examine le cas asymétrique où il ne dispose que d'une issue bénigne.

## Hypothèse et contrôle

Pour chacun des deux conflits préexistants (déplacement est caché létal / ingestion `berry_a` à effet d'intégrité variable), entraîner `FrozenTableEquipment` sur **une seule transition physique bénigne**, puis interroger exactement le même état accessible/commande issu du monde contrasté **non fourni au modèle**. Vérifier :

1. la clé `input_digest` est identique à celle de l'exemple physiquement observé en entraînement;
2. `predict` renvoie la prédiction bénigne effectivement enregistrée, avec son niveau de confiance affiché ;
3. l'issue physique contrastée déjà enregistrée est différente, en terminalité ou en intégrité ;
4. la vérité externe de ce contrôle reste exclusivement au laboratoire, non dans I0, non dans une correction Stage9 ;
5. le test ne doit pas être utilisé pour prétendre quantifier une fréquence d'erreurs, un taux de toxicité ou la sûreté d'un modèle probabiliste.

Une absence de contre-exemple dans l'exemple d'entraînement peut produire une prédiction nominalement certaine à la table, mais **pas une certitude causale du monde** lorsque les causes cachées rendent les entrées accessibles observationnellement identiques. Ce test ne modifie pas l'Equipment de production, Stage6, Stage9, Stage12 ou le MVP v1.3.1, ne crée aucune naissance ni transition physique supplémentaire au-delà des huit de L.

**A2.30 PARTIELLE, Stage12 PARTIAL, issue #110 OPEN** jusqu'à réception opérateur et recherche d'un modèle explicite de l'incertitude, si autorisée.
