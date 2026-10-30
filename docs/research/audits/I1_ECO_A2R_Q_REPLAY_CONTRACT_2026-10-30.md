# A2-R : reconstruction Q/TD intégrale, contrat numérique hors moteur (L1)

**30 octobre 2026.** Suite du préenregistrement #625, de la variante de naissance #626 et du précontrôle M11 #627. Historique A1-C NO_GO ; général L3 NOT_ESTABLISHED.

Le module `tools/research/i1_a2r_q_replay.py` reconstruit indépendamment les 12 caractéristiques P-32, les valeurs apprises Q, les traces d'éligibilité TD, les signatures mises à jour, les compteurs, les retours `return_g`, la différence `delta` et les valeurs `q_previous/q_next`. Il atteste les preuves Stage8→Competition→admission de commande→commande physique vécue et compare les vecteurs avec le propriétaire courant Value/Needs/TD de l'image M11 authentifiée.

Le calcul est limité à la vraie durée de vie, au plus H192. Le pas mortel est compté dans la trajectoire physique mais aucune mise à jour terminale de TD n'est inventée. La reprise à froid contrôle le segment pending et ses récompenses effectivement accumulées. Les caractéristiques jour/nuit utilisent le calendrier du monde préenregistré, et non l'hypothèse artificielle « tous les pas sont de jour » de A1-C H48.

**Qualification des preuves :** `full_q_replay_verified` vaut vrai uniquement si l'image M11 finale est fournie et les comparaisons numériques passent. Cela ne veut pas dire que la provenance des paramètres de naissance est indépendamment prouvée. `birth_source_provenance_verified`, `mechanism_exposed` et `adaptive_learning_go` restent explicitement faux/non établi. Aucune preuve de différence causale entre politiques appariées n'est produite par le seul rejeu d'une vie.

**Travaux encore requis avant toute naissance A2-R confirmatoire :** sceller le SHA source et les paramètres P-32/TD réellement nés (incluant setpoints/poids individuels), tester les chemins moteur/TD sommeil et mort, établir la correspondance de deux vies et l'exposition Q distincte, fournir le lecteur 96 originaux/manifestes SHA-256, enregistrer un one-shot inviolable. Ne pas substituer une validation L1 au seuil d'exposition 18/24 par rôle.

Tests : `tools/research/tests/test_i1_a2r_q_replay.py`. CI ciblée Python 3.11 et 3.12, aucune CI naturelle lourde. Aucune modification de `src/i1`, `src/i0` ou du moteur canonique. Aucune vie confirmatoire n'est lancée.
