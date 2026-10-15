# A2.28 : résultats de l'entonnoir d'occasions d'agence B

**15 octobre 2026.** Préenregistrement antérieur au code `25d989de`. Réplication expérimentale sur `8e97b587a1277b2853febfe3856b687e67c033d9`, [CI #38690724743](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38690724743) **SUCCESS Python 3.11 et 3.12**. Ce rapport ne transforme pas le diagnostic rétrospectif B-L600 en preuve prospective.

## Résultats physiques et subjectifs

**Huit nouvelles naissances autonomes et mortelles, quatre profils alimentaires définis avant naissance × obstacle extérieur OFF/ON, 64 vrais pas par vie : 512 transitions.** Journaux canoniques, WAL durable, attestations de première personne, préengagements et jugements B, et progrès d'objectif passent les auditeurs indépendants. **12 jugements B réellement émis**, 12 commandes explicitement motivées par objectif actif et **0 refus UC des évaluations B**.

| Profil | Sans obstacle : jugement B | Avec obstacle : jugement B | Nourriture perçue première → dernière |
|---|---:|---:|---|
| `restored` | 3 | 3 | 35 → 65 (deux vies) |
| `sustained` | 2 | 0 | 24 → 0 |
| `episodic` | 3 | 1 | 33 → 0 |
| `marginal` | 0 | 0 | 22 → 0 |

**Prudence importante :** `restored` a une hausse alimentaire observée, mais **aucun `self` distal n'est attribué** sur cette base. Les valeurs sont des sensations cohérentes avec le journal, et non une preuve de causalité indépendante.

## Analyse de l'attrition sans comptes artificiels

Les profils `marginal` comportent une activation alimentaire réelle au pas 1, et de nombreuses mises à jour de **ce même objectif**, avec progression de la faim jusqu'à une nourriture perçue égale à 0. Malgré cela : **aucune commande directement motivée par cet objectif et aucun préengagement B**. Le moteur choisit principalement `se_deplacer` pour une `cible_exploration`, ainsi que `dormir` sous pression de sommeil. `sustained/A2` ne produit également aucun jugement B bien qu'un objectif soit maintenu et réactualisé. Le profil `restored` réalise réellement `collecter` et `manger`, source des nouveaux préengagements. Le nombre `active_goal_changed` n'est **pas** un compteur de nouvelles activations : plusieurs événements peuvent mettre à jour exactement le même `goal.id`.

Ce diagnostic réduit le verrou de densité à la **sélection de l'action et au filtrage de sa motivation d'objectif**, en amont du jugement B. Il n'établit pas encore si la prédominance de l'exploration est un défaut cognitif ou une politique justifiée. Les comportements sous pression ne doivent pas être « corrigés » pour forcer artificiellement une calibration ; il faut désormais auditer les options candidates, leurs scores/contraintes, le repli et l'arbitrage du moteur de planification.

## Incident d'instrumentation et correction bornée

La [première CI #38689910298](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38689910298) était **FAIL** dans les deux Python : elle exigeait à tort une `stage12_action_motive_attested` pour chaque `command_experienced`, y compris pendant des cycles de sommeil réduit. Les huit journaux contenaient déjà les 512 pas. Le correctif du **seul observateur laboratoire** `8e97b587` admet un pas sans ce reçu uniquement si la commande est `dormir` et qu'un événement `stage10_reduced_capture` possède le même pas et `attempt_ref`. Les autres omissions restent FAIL. Il distingue également activation réelle, réaffirmation du même objectif et désactivation. Le protocole et les seuils préenregistrés restent inchangés.

## Verdict

**T1–T7 : PASS technique borné à la matrice**, aucune révision de `GoalAgencyService`, `DualScopeService`, ActionControl, Stage6, Stage10, M-11, UC, le journal, l'Oracle ou Stage9. Aucune vérité du laboratoire n'est fournie à I0. **12 jugements sur 512 pas ne démontrent pas une responsabilité causale fiable, ni une capacité de calibration GA-06** ; le couplage hérité reste désactivé sous B, sans paires synthétiques ni abaissement de `2+2/12`. Les deux Python rejouent la même cohorte déterministe.

**Stage12 PARTIAL, issue #110 OPEN, PR #184 non fusionnée, MVP v1.3.1 inchangé.** La réception opérateur et la révision normative du contrat B sont distinctes. La suite recommandée est un audit prospectif des choix entre exploration, besoins alimentaires et sommeil, sans imposer de commande à I0.
