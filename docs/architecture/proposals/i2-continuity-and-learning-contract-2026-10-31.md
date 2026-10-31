# I2 : contrat architectural de recherche (proposition G1)

**31 octobre 2026. Statut : proposition, non revue indépendamment.** Parent comparatif : I1, référence Git `1e19f02db14b64a35f8bb014d69cc061f311002c`, arbre `src/i1` `cf7968d3ee94a5792d37d76241a55d4c8406a3fb`. Aucun choix ci-dessous n'est une capacité déjà démontrée. Issues #662, #663, #664, #665.

## Objet minimal
Un individu né sans expérience empruntée doit apprendre de ses propres observations dans un monde et un corps limités, former des intentions révisables, considérer des actions réellement accessibles, payer leur traitement, puis ne produire une commande que par Competition, Action Control et la physique. Une intention ne détient **aucun droit moteur**.

## Responsabilités séparées
1. **Perception** : seule fenêtre subjective sur le corps, l'inventaire et les affordances locales. Ne reçoit ni carte globale cachée ni conséquence future.
2. **Besoins et valeur** : pression issue des états corporels vécus, des tempéraments nés et de leur historique; valeur ≠ instruction.
3. **Mémoire / apprentissage** : enregistre les séquences `observation → action admise → conséquence vécue`, les incertitudes et les retards, avec signatures/provenance. Aucun Q/mémoire d'I1 n'est copié.
4. **Intentions** : propriétaire causal unique, identifiant sémantique stable distinct de l'ID d'option. Chaque intention précise origine vécue, contexte, objectif, justification, version, échéance et invalidations. Une intention peut persister après une action ratée mais ne présume pas du résultat.
5. **Options** : reconstruites à chaque capture à partir des candidats disponibles et de l'état actuel. Chaque option possède un identifiant de réalisation et une durée vérifiable; elle ne réutilise pas automatiquement l'accumulateur Competition précédent.
6. **Competition et Action Control** : chaque option est évaluée au coût UC réel. Conservation sémantique d'intention ne signifie ni score acquis, ni admission, ni privilège de sécurité. La commande physique n'est possible qu'après décision et admission authentifiées.
7. **Monde, mort et M11** : monde propriétaire des conséquences, mort irréversible, transaction unique et reprise seulement depuis l'état complet authentifié et non terminal. Aucune restauration d'un individu mort.

## Invariants de temps
- À t0 naissance sans apprentissage injecté, identité, tempérament et configuration scellés.
- Avant chaque choix : capture authentique, calcul et facturation UC **avant** consultation de mémoire, nouveaux candidats.
- Entre pas : une intention peut être conservée si ses preuves et conditions restent admissibles. Toute option motrice expirée est invalidée; une intention ne transporte jamais `accumulator`, `winner`, `admission` ou `command`.
- Au réveil / après sommeil : les observations et budgets sont à nouveau évalués. Le sommeil ne crée pas de résultat physique inventé.
- En cas de nouveau but, disparition de ressource, contradiction vécue, corruption ou décès : dégrader/suspendre/annuler l'intention selon des règles bornées, documenter la raison. Une interruption n'autorise pas de contournement.
- Après une action admise : rapport physique + observations subjectives, puis crédit causal incertain avec provenance; ne pas apprendre à partir de la vérité cachée du Lab.

## Hypothèses et réfutations
**H1 (continuité)** : garder une intention sémantique peut permettre de compléter une séquence utile sans admission automatique. **Réfutation :** aucun gain sur contrôle indépendant, UC cachés, persistance après invalidation, passage de veto ou sur-accumulation d'un candidat expiré.

**H2 (crédit différé)** : un agent peut attribuer une conséquence à une préparation antérieure depuis sa propre histoire, y compris lorsqu'une étape coûte à court terme. **Réfutation :** crédit identique sans vécu, sur conséquence neutre/inversée ou provenance forgée; préférence maintenue malgré une conséquence adverse.

**H3 (arbitrage cohérent)** : besoins, apprentissage et exploration coexistent sans rendre systématiquement inaccessible une action utile déjà perceptible. **Réfutation :** cycles non payés, favorisation codée de `manger`, blocage récurrent au détriment du besoin corporel, suppression artificielle de concurrents ou dégradation de la survie.

## Protocole logiciel minimal avant tout individu I2
- Positifs et négatifs : naissance vide; référence individuelle de chaque observation; intention conservée / révoquée; candidate renouvelée sans score moteur transporté; UC insuffisantes; action veto; ressource disparue; conséquences retardées, neutres ou opposées; reprise M11 intacte; corruption/COMMIT incertain; mort terminale.
- Interdits : import du moteur `i1lab` comme I2, code I1 mutable partagé, rollback, téléportation, choix imposé, oracle de toxicité, suppression de protections pour réussir.
- Contrats nommés, versions déterministes, journal M11 unique, métrique physique indépendante de la récompense; tests sous Python 3.11 et 3.12 au SHA exact pour les changements moteurs.

## Portes et autorisations
G1 reste **REVIEW_REQUIRED** tant qu'une revue architecture et science n'a pas accepté les modes d'échec. G2 autorise seulement un **scaffold inerte** de fichiers. Aucun constructeur vivant, aucune inscription dans `config/engine-registry.json`, aucune naissance, aucun démarrage automatique de CI scientifique. G3 logiciels, G4 protocole statistique gelé, G5 vie comparative et G6 promotion exigent des validations séparées. L3 I1 = `NOT_ESTABLISHED`, A1-C = `NO_GO`, A2-R = `NOT_EXECUTED`.
