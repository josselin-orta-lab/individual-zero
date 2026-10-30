# I1 / A2-R : contrat de naissance de la variante H-R (L1 uniquement)

**Source normative :** docs/research/I1_ECO_A2R_REWARD_PREREGISTRATION_2026-10-30.md (PR #625), gel du 30 octobre 2026. A1-C = NO_GO et L3 adaptatif = NOT_ESTABLISHED, sans reinterpretation.

## Proprietaire et intervention

Le module tools/i1_eco_a2r_birth.py est strictement experimental, sans modification de src/i1, src/i0, WorldBody, Action Control, Q/TD, seuils, UC ni moteurs canoniques. Il ne rajoute aucun parametre au point d'entree birth_i1_m11. Il selectionne uniquement au moment d'une nouvelle naissance la classe d'un seul Value/Needs owner. Le constructeur global est immediatement restaure; les choix physiques ne sont jamais imposes.

- CANONICAL_ABS : proprietaire I1ActiveValueNeeds originel et formule native de distance absolue, intacts.
- RESEARCH_DEFICIT : sous-classe de ce meme proprietaire, dont seule la methode reward_between retourne la reduction ponderee des deficits positifs, sur les memes quatre canaux energy, food, water, integrity. Les labels d'action, les noms de baies et les futurs etats physiques sont absents de la formule.
- Les trois chemins runtime identifies (Stage8 eveille, Stage10 continuation du sommeil, reflexe au reveil) appellent toujours value_needs.reward_between. La fonction reward_for Stage4, les pressions vitales et les perceptions restent natives.
- La version du contrat de ValueNeedsConfig est suffixee dans le bras RESEARCH_DEFICIT, puis l'etat causal proprietaire exporte un marqueur de mode supplementaire. Un etat altere ou venant d'une autre version est refuse par la restauration recherche. Le champ GoalProposal.rule_version contient aussi cette nouvelle version; il faudra controler qu'aucun effet de ce marqueur ne precede l'effet TD, sans quoi le protocole est bloque.

## Matrice et garanties

La matrice pure contient 24 temperament seeds neufs 2001..2024, deux roles de baies native/reversed et deux bras, soit 96 identites differentes et opaques, plus un ordre SHA-256 reproductible. Il s'agit de la configuration de futures naissances, **pas de naissances realisees**.

Le test tools/a2r_tests/test_i1_a2r_reward_birth.py couvre le calcul au-dessus des consignes, le refus de faux modes, la source temperament unique, le retour sans patch du constructeur, l'etat initial physique et perceptif avant reward, le mode causal dans M11, la restauration froide au pas suivant et le rejet d'une usine de naissance incompatible. Un nombre minimal de pas de deux I1 sert de **smoke logiciel L1** sur Python 3.11/3.12, non de cohorte confirmatoire, sans infirmer une mortalite ou un score scientifique.

CI : .github/workflows/i1-a2r-reward-birth-l1.yml, declenchee uniquement par ces outils et ce rapport, sans executer i1-current-ci.yml, natural FULL ni la matrice 96 vies. Les sources et etats de I0 sont intacts.

## Portes non franchies

Avant une cohorte : lecteur froid independant de M11 capable de verifier mode de naissance/TD effectif, hash de la source, premiers Q et Stage8, Competition, Action Control et physique, differences pre-reward, decès et ECO-v1 a horizon H192; stockage durable des 96 WAL et manifestes; garde d'une unique execution prospective en tentative 1. Les 96 vies ne doivent pas etre lancees dans cette PR. Une bonne statistique de ce test ne vaut jamais GO automatique L3; toute divergence technique = MEASUREMENT_BLOCKED jusqu'a qualification.
