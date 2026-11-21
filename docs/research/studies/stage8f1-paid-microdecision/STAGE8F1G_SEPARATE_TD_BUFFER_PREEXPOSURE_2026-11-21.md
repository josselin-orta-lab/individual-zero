# Stage8-F1G · contrôles SEPARES des valeurs TD et du tampon de souvenirs

**Préenregistrement distinct effectué avant toute exposition F1F ou F1G. 21 novembre 2026.** Base `77c3e3395dfa379851d6192a7ec09968727c9ed9`. Source originale `F1C_PAID_NATIVE_ORIGINAL.json` SHA256 `e46ad5f54af49796da65f48d603595544116aa6e73632546b0935d2178c5e91d`, jamais réinterprétée ou remplacée. Les huit contextes `bare`, `water_here`, `water_north`, `water_east`, `water_west`, `food_here`, `food_east`, `mixed_here_water_east_food` sont exactement ceux de F1F, y compris tick 0 initial invisible, événements natifs à tick 1 et même génome/graine/corps. **Ne sélectionner aucun contexte à partir des résultats F1F.**

## Hypothèses et contrastes séparés

Chaque contexte exige **quatre copies** du **même état individuel F1C `retain` après vraie acquisition et vrai paiement**. Les moyennes d'EffectsModel restent pleinement accessibles et identiques dans tous les bras.

- **`full`** : toutes valeurs TD et tous épisodes de `buffer` réellement acquis restent lisibles.
- **`sham`** : copier puis restaurer les mêmes valeurs TD et le même buffer sans altérer les scores.
- **`mask_td`** : sur un clone pendant *la seule décision*, lire les `values` d'avant l'apprentissage F1C original en gardant exactement les **mêmes dimensions (3×6)**, le buffer authentique et EffectsModel inchangés. Remettre les valeurs originales immédiatement après décision, sans empêcher le débit corporel.
- **`mask_buffer`** : conserver **exactement le même nombre de places mémoire (1)** et les mêmes autres champs privés, mais remplacer le contenu accessible du tampon par **un seul `None` sentinelle explicitement non factuel** pendant *la seule décision*, puis restaurer l'épisode réel. La sentinelle n'est **jamais** une expérience inventée ni une mise à jour; sa présence dans un plan, une prédiction ou un apprentissage inattendu invalide le test. Cette intervention teste l'accès au **contenu épisodique**, pas le stockage ni son compte. Si `Mind.decide` ne lit que `len(buffer)`, le résultat nul est attendu et ne prouve PAS l'inutilité du buffer pour l'apprentissage/replay ultérieur.

## Principaux critères et budgets

**Deux estimands préalables, non combinables** : pour `mask_td` et `mask_buffer`, nombres respectifs (K_{TD}/8) et (K_{BUFFER}/8) de modifications de la **commande motrice native `(action,param)`** vs `full`. Pour chacun, le protocole exige **8/8 comparaisons appariées**; au moindre échec de financement, facture énergie/vigilance différente, `CognitiveWork` différent, état corporel, perception, source G2 hypothétique ou changement de champs non autorisé : verdict global **`INCONCLUSIVE_TD_OR_BUFFER_COST_GATE`**, avec toutes les conditions et leurs reçus conservés, sans dénominateur redéfini. Ne pas ajouter de cycles « gratuits » pour équilibrer; la parité doit sortir naturellement du contrôleur.

Si 8/8 valides et K=0, `NO_TD_CONTENT_EFFECT_IN_EIGHT_ECOLOGIES` / `NO_BUFFER_CONTENT_EFFECT_IN_EIGHT_ECOLOGIES`; si K>0, `TD_CONTENT_MOTOR_EFFECT_IN_K_OF_EIGHT_ECOLOGIES` / `BUFFER_CONTENT_MOTOR_EFFECT_IN_K_OF_EIGHT_ECOLOGIES`, ces constats restant **logiciels synthétiques** sans valeur adaptative prouvée. Le contrôle sham doit être neutre. Les scores sont secondaires.

**Aucune action prescrite, aucune modification de `Mind.decide`, du `World` original, de la politique de référence, de l'énergie/vigilance, du RNG ou de l'inné.** `World.step` natif finance réellement la décision sous les mêmes lois, tous les épisodes restent sous le même compte de mémoire. Test séparé F1G, source F1C octet-verrouillée, deux productions reproductibles et audit stdlib Python 3.12 sans moteur. Ne pas importer les résultats F1F pour choisir les ecologies.

**Limites** : huit contextes synthétiques déterministes, même racine d'apprentissage F1C, pas huit lignées indépendantes, pas d'inférence statistique généralisable. Le tampon n'a qu'**un seul** épisode; son contenu éventuellement non consulté lors d'une décision ne préjuge pas de son rôle futur. Aucun `run_life`, aucune naissance/cohorte nouvelle, aucune mémoire privée des vrais G2, aucun gain de survie ni héritabilité, Stage8-E2 `STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0 / CLOSED_NO_RETRY` inchangé.
