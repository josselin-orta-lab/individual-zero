# Individual Zero I1 : preuve locale d'apprentissage de l'attente dans Competition

**Statut** : audit post hoc, descriptif et statique, execute le 29 octobre 2026 sur les 48 archives originales A1-C. **A1-C reste NO-GO ; L3 reste NOT_ESTABLISHED.** Aucune naissance, nouvelle simulation physique, modification de reward, Q, Competition ou UC. L'issue de suivi est #305, et l'issue de validation L3 est #304.

## Sources, unite d'analyse et provenance

Run original [GitHub Actions #40944104333](https://github.com/josselin-orta-lab/individual-zero/actions/runs/40944104333), source reproductrice `26f7929b6db43f68e78b0cc0d9c67e7444f924c6`, 48 journaux M11 SQLite, 24 paires, 12 blocs de temperaments (seeds 101..112). Les ZIP originaux et le manifeste `I1_ECO_A1C_EVIDENCE_MANIFEST.json` sont requis pour reproduire l'analyse. L'auditeur `i1_a1c_wait_gate_audit.py` reprend la verification integrale des SHA-256, des chaines M11 et des 12 caracteristiques TD/Q avant de mesurer le dernier cycle Competition de chaque decision. Une **opportunite** est un pas de decision avec une capture first-person, reserve `food` sous le setpoint de naissance et baie disponible en inventaire. Les prolongations non decisionnelles de sommeil ne sont jamais incluses.

**Attention aux pseudo-replicats** : 391 opportunites canoniques et 275 temoins sont des pas repetes dans 24 vies par bras, et **non** des experiences independantes. Les deux roles nutritifs d'un meme temperament constituent un bloc, pas deux sources innnees independantes.

## Entonnoir general, deja reaudite

| Chemin de `manger` sous faim avec baie | Canonique (24 vies) | TD masque (24 vies) |
|---|---:|---:|
| Absent des evaluations Stage8 | 72 | 59 |
| Evalue, ne franchit jamais le seuil | 258 | 115 |
| Franchit le seuil, autre action admise | 17 | 47 |
| `manger` admis physiquement | 44 | 54 |
| Total | **391** | **275** |

Parmi les 258 occasions canoniques ou `manger` est evalue mais reste sous le seuil, 249 ne possedent **aucune evaluation de `manger` avec une valeur Q apprise**. Une aversion Q apprise pour `manger` ne peut pas expliquer a elle seule ce blocage frequent. L'absence de Stage8 ne certifie pas l'absence de proposition en amont, a cause des limites UC et de la duree des propositions.

## Analyse plus stricte du dernier cycle reel

Sur 391 occasions canoniques, **256** commandes `attendre` sont physiquement admises : 95 attentes de repli sans franchissement de seuil, 161 attentes ayant franchi leur seuil. **155/161** de ces attentes concurrentielles ont une Q native apprise strictement positive et pas de simulation disponible dans Stage8.

**Separation necessaire des sources de preuve** :

- **154** gagnants sont `permanent:attendre`, signature `primitive:attendre` : pour leur evaluation Stage8 dans le cycle effectivement admis, la valeur Q apprise est la **seule preuve extrinseque disponible**. Le simulateur n'a pas fourni de valeur. Les 154 gagnants passent tous d'un accumulateur *sous* le seuil a un accumulateur *au-dessus* ou egal au seuil dans ce dernier cycle.
- Parmi ces **154 cycles**, **107** ne comportent **aucune autre option franchissant le seuil**; **47** comportent une autre option qui franchit aussi, mais perd selon le classement Competition.
- **Un** gagnant local additionnel (natif, seed 105, pas 14) possede une Q positive sans simulation, mais sa preuve passe par l'adaptateur d'affordances avec un **prior local possible**. Il n'est **pas** comptabilise comme dependant uniquement de Q.
- Les 107 cas sans autre franchissement sont enregistres dans **6 vies canoniques**, appartenant a seulement **3 des 12 temperaments independants** : **101, 102, 111**. Ces seeds se repetent dans les deux roles nutritifs. Les 155 observations ne prouvent donc pas un comportement universel chez I1.

Sur les memes 256 attentes sous faim et inventaire, l'aire des deficits ECO se degrade immediatement **256/256**. Parmi les **250** suivies d'une mise a jour TD d'un pas, la recompense publiee est positive **250/250**. Les 6 autres cas ne sont pas assimiles a zero. Il existe une discordance entre le signal de reward et le changement ECO **au pas observe**, pas une preuve que l'attente serait toujours inutile a long terme.

## Interpretations causales autorisees et interdites

**Etabli** : 48/48 originaux M11 authentifies; progression numerique Stage8/Competition deja verifiee par #622; une valeur Q native positive suffit a rendre `permanent:attendre` evaluee dans 154 cycles observes ou Stage6 ne fournit aucune valeur; les accumulateurs et seuils signes donnent 107 cycles dans lesquels aucune autre option ne passe son seuil.

**Non etabli** : une vie sans lecture Q aurait mange a la place, ni que 154 attentes auraient disparu, ni que le NO-GO de A1-C vient uniquement de l'inaction. Enlever un signal dans **un cycle archive** n'est pas regenerer la trajectoire sans ce signal : UC, affectation d'options, accumulateurs, perceptions et besoins auraient pu diverger depuis des pas anterieurs. Le score L3 ne peut jamais etre recalcule a partir d'un tel shadow local.

## Hypothese prospective H-D / H-R, sans lancer de nouvelle vie

**H-D** : dans des conditions de faim avec nourriture disponible, la preuve de `manger` est insuffisante pour franchir Competition alors que `permanent:attendre` acquiert un signal Q suffisant. **H-R** : la recompense TD de distance symetrique aux setpoints peut favoriser cette attente dans des etats ou les deficits alimentaires empirent. Les deux hypotheses sont distinctes et peuvent etre vraies, fausses ou mediatrices l'une de l'autre.

Prochaine porte : controler les **premieres divergences appariees** avant d'envisager une variante prospective. Si une intervention est necessaire, tester une modification physiologique generalisable de **reward**, et non une priorite `manger` forcee, sans connaissance des baies ni retouche opportuniste de lambda. Le futur protocole devra conserver les sources physiques appariees, des graines nouvelles et une metrique de benefice preregistree, avec un controle de generalisation hors du monde ECO.

## Reproduction

`python tools/research/i1_a1c_wait_gate_audit.py --root /chemin/48-zip-et-manifeste --out /chemin/resultat.json --workers 4`

Les tests `tools/research/tests/test_i1_a1c_wait_gate.py` falsifient notamment les seuils et preuves Competition, la source de la Q (permanente versus option locale avec prior), le masque TD, l'absence d'inventaire, les doublons d'options, les cohortes incomplètes et les faux ensembles de graines. **Pas de CI naturelle lourde ni de naissance** pour ce diagnostic.
