# A2.30-ZS : preenregistrement de predictions scellees AVANT chaque action physique heldout

**Date : 15 octobre 2026, AVANT runner ZS, avant toute physique ZS et avant la CI ZS.** Branche scientifique empilee sur #210 (ZP audit independant) et #208 (ZO laboratoire), au SHA de base `1ab0812e7ff09e81a4e5c8cdf32d15504b1e7273`. La faiblesse ZO est **connue avant ZS** : le modele partiel et sa formation sont bien gelés avant le heldout, mais le calcul de `compare_forecast` a lieu APRES `apply_one` pour les 104 mondes. ZP a etabli ce defaut de preuve de chronologie et n'a PAS pretendu que ZO possedait un recu individuel de prediction preaction. ZS teste exactement cette lacune, et ne transforme pas retroactivement ZO en etude prospective stricte.

## Population scientifique figée

**120 nouveaux mondes externes independants / 120 pas physiques non ingestifs** : reprendre EXACTEMENT les recettes, dimensions, seuils et distributions fixes de ZO en tant que **replication independante**, mais utiliser un espace d'identites `a230zs:` strictement distinct du run original ZO :

- TRAIN 16 mondes, positions `(5,5),(7,7)`, food `35,45`, phases `1,201`, actions `MOVE_E`, `COLLECT_B`. 16 actions physiques uniquement en formation, exactement huit demonstrations par commande.
- NOMINAL 64 mondes inedits, positions `(9,9),(11,11),(13,13),(15,15)`, corps `(35,25,30)`, `(70,55,65)` pour energie/nourriture/eau, phases `1,201`, deux commandes et deux effets B caches `benign`, `toxic_lethal`.
- HIDDEN 24 mondes, quatre positions × deux commandes × `hidden_lethal_east`, `hidden_danger_here`, `hidden_forced_action_failure`.
- BOUNDARY 16 mondes, quatre positions × deux commandes × deux phases avec corps `(0.5,0.25,0.1)`.

Resultats **attendus avant les nouvelles mesures** : 64 predictions nominales correspondant aux six composantes autorisees, quatre deces moteurs caches, huit blessures d'integrite invisibles, huit échecs forces d'action et 16 abstentions de clamp. Ces effectifs ne doivent pas etre forces si les observations different. Ni le modele ni les sujets ne recoivent les causes cachees. Aucun `manger(B)` n'est execute.

## Ordre temporel a sceller, pour chacun des 104 HELDOUT

1. Executer les 16 mondes TRAIN, enregistrer leurs 16 exemples de physique reelle, figer le `FrozenTableEquipment` temoin et le modele partiel appris de leur seule projection accessible. Ecrire le modele et ses SHA sur disque **avant de creer** le moindre monde heldout.
2. Pour chacun des **104 mondes jamais utilises au training**, construire la physique dans son bras; capter le `SimulationState` accessible `before` sans exécuter de commande, verifier visibilite et eligibilite de la primitive fixee.
3. Appeler `partial_forecast` sur ce `before`, avec seulement le modele deja fige, la commande visible et aucune variable `hidden_*`, resultats de `WorldBody`, `Oracle`, ou valeur postaction. Ajouter un evenement **`prediction_committed`** dans un journal JSONL hash-chainé. Son contenu doit fixer `world_id`, index unique, empreinte complete de `before`, commande, hash de modele immuable, status, prediction numerique ou abstention, et les quatre champs de securite **toujours `None`**. Ecrire, `flush`, `os.fsync`. Controle de poison : aucune entree `outcome_sealed` de ce monde avant cette etape.
4. Appliquer **exactement une** primitive de laboratoire `WorldBody.apply` via `EquipmentCorpusRecorder.record_transition`, aucune action I0. Apposer ensuite **`outcome_sealed`** au journal durable avec avant/apres externe, terminalite reelle, empreinte de l'exemple physique, et un lien `prediction_event_sha256` vers le **recu deja fsyné**. Ecrire, flush, fsync, ne pas reecrire le recu precedent. Si la physique tue, geler le monde, ne pas produire de capture subjective posterieure.
5. Un auditeur doit lire ce flux de **208 evenements ordonnes**, recalculer le hash canonique de chaque recu et chaque lien prev, imposer une alternance `prediction_committed → outcome_sealed` pour chaque monde, et rejeter les coutumes post-hoc : prediction manquante, apres ecrit avant prediction, modele/source change apres la prediction, recu terminal declare non terminal, predictions `safe=True`, faux droit de cognition ou UC. La chronologie est garantie dans le processus du runner par ordre d'appels plus fsync; un fichier hors de ce processus ne peut apporter une preuve cryptographique absolue de l'heure reelle. Ne pas formuler d'attestation exageree.

**Aucune mutation du modele gelé**, aucun `partial_forecast` recalcule apres le resultat pour rediger un recu individuel preaction. Le recalcul independant a posteriori est autorise comme **verification distincte**, jamais substitut a `prediction_committed`.

## Mesures et interpretation

Recalculer par bras : nombre de predictions prefixees durables, non-abstentions/abstentions, six deltas corrects, predictions erronees, blessures/deces/echecs physiques reels. Le `FrozenTableEquipment` exact sur les 104 racines inedites reste un temoin `UNKNOWN`, pas une alternative sure. Les predicteurs partiels doivent toujours produire `integrity=None`, `terminal=None`, `next_adjacency=None`, `safe=None`, meme lorsque leur estimation du mouvement est juste. Les effets de la baie B ingeree ne sont jamais testes ni certifies.

**Pas de nouveau I0, pas d'action autonome ni de jugement d'agence subjectif**, pas de depense UC reelle, pas de postmortem cognitif. Deux jobs Python 3.11/3.12 peuvent verifier la determinisation numerique mais ne constituent pas 240 mondes statistiques.

## Controle scientifique et falsifications

Tests negatifs avant PASS : retirer, inverser, dupliquer ou reordonner un recu `prediction_committed` ; casser la chaine de SHA/prev ; forger un model_hash different ou une prediction apres observation; injecter `hidden_intervention` ou `safe` dans une prediction; inverser le bras nominal/hidden ; inventer la reussite d'une action physiquement echouee; compter une action terminale comme experience vecue; modifier un identifiant mondial; introduire `manger(B)`; faire fuir un exemple heldout dans le TRAIN; fabriquer un nombre d'UC ou une action I0. Refuser toute ligne dont le SHA ne correspond pas a la projection canonique, et ne pas combler silencieusement un recu manquant.

**ZS PASS uniquement si** protocole de 120 mondes applique, 104 predictions durables fsync AVANT leurs 104 actes, 104 consequences archivees APRES, 16 exemples train incorpores au modele immuable avant les 104 actes, 208 lignes hash-chain exactes, controles adversariaux, rapport scientifique et CI sur 3.11/3.12. Si le flux ne permet pas d'etablir le temps avant/apres, resultats `CHRONOLOGY_NOT_CERTIFIED`. Aucun modele dans `src/i0`, aucune modification normative, aucune modification Stage9/DC-05, M11, UC, Oracle. **Stage12 PARTIAL, A2.30 PARTIELLE, #110 CLOSED administrativement, deploiement cognitif NO-GO.**
