# Individual Zero #110 : A2.15, attrition vérifiée des preuves d'agence vécue

**14 octobre 2026. Verdict global scientifique Stage12 : PARTIAL.** Protocole préenregistré **avant code** au SHA `b9d6c114f30a405245b0e7771c5c526b04e9dc63`. Référence au démarrage `main 86bff3a8a8ccb4a146a71dc7153a47fea65b5557`. MVP normatif v1.3.1 inchangé. Le logiciel d'I0, ses UC, ActionControl et le détecteur Stage12 n'ont pas été modifiés.

## Sources, provenance et reproduction

**Corpus de découverte fixé à l'avance** : les **16 vies mortelles A2.10b déjà scellées**, **672 pas physiques**, via [Actions #38607070724](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38607070724), identifiants de journaux et SHA-256 enregistrés individuellement. Le script indépendant `scripts/audit_stage12_issue110_a215_funnel.py` utilise à chaque vie `audit_export_bytes`, `audit_stage12_goal_progress`, `audit_stage12_first_person_agency`, et `audit_stage12_attribution_pairs`, puis reconstitue **chaque** fenêtre glissante réelle de **12 diagnostics payés**, sans condenser les pas vides. Le compte de toutes les fenêtres doit correspondre à chaque `verified_successes`, `verified_failures` et `attribution_bias` publié. Les archives ne sont jamais réécrites et aucune vérité Oracle n'entre dans I0.

[CI A2.15 #38628122946](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38628122946) : **SUCCESS sous Python 3.11 et 3.12**, reproduction **identique de tous les agrégats**. Les deux premiers CI rouges sont conservés : l'auditeur initial cherchait `event_id` au mauvais niveau du JSONL, puis une correction introduisit un retour-ligne littéral invalide ; la correction finale rétablit l'identifiant du wrapper original. Ces défauts d'**instrumentation externe** n'ont modifié ni les vies ni les sources physiques. Les deux Python répètent le même corpus de 16 vies, pas 32 seeds indépendants.

## Décomposition exhaustive, résultats bruts A2.10b

| Étape de la preuve dans la vraie vie | Observations |
| --- | ---: |
| Objectifs suivis et prérégistrés | **22** |
| Followups corporels/spatiaux réellement vérifiés, résultat success/failure | **22** |
| Followups au résultat `unknown` | **0** |
| Jugements subjectifs `self/world` appariables | **14** |
| Jugements d'agence `unknown` | **8** |
| Jugements `unavailable` | **0** |
| Paires GA-06 effectivement admises | **14** |
| Charges UC de jointure refusées | **0** |
| Jointures différées | **0** |
| Paires réellement consommées au prochain diagnostic | **10** |
| Paires indisponibles après admission | **4** |
| Cause des quatre indisponibilités | **4 × `no_waking_diagnostic_at_due_step`** |
| Paires restantes au terme de la vie | **0** |
| Sur les paires consommées, succès | **6** |
| Sur les paires consommées, échecs | **4** |
| Maximum de succès dans une fenêtre de douze *au sein d'une même vie* | **2** |
| Maximum d'échecs dans une fenêtre de douze *au sein d'une même vie* | **1** |
| Fenêtres atteignant 2 succès + 2 échecs | **0** |
| Vies dont le biais d'attribution devient évaluable | **0/16** |
| Ingestions physiques réelles dans la cohorte | **6** |

Les quatre paires indisponibles ne sont **ni effacées silencieusement ni des échecs d'UC** : l'auditeur constate des échéances de diagnostic sans éveil, à partir de la chaîne des vrais reçus `stage10_reduced_capture` et des pas physiques fermés. La conservation est exacte : **14 = 10 consommées + 4 indisponibles + 0 terminalement en attente**. Les 8 jugements `unknown` **ne sont pas des échecs physiques ou des échecs d'agence** ; ne jamais les transformer en `self`, `world` ou contre-exemples artificiels.

## Contrôle longitudinal A2.6, distinct du corpus de découverte

Le [run A2.6 #38624426580](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38624426580), achevé après préenregistrement A2.15, a réellement atteint **6 vies mortelles ×600 pas = 3 600 transitions physiques**, **0 erreur WAL/runtime ou audit**, **0 mort**, **0 vie avec calibration évaluée**, mêmes résultats sous Python 3.11 et 3.12. Il teste trois conditions physiques × traitement géographique OFF/ON : restored libre, restored A2 bloqué/libéré, sustained libre. Les deux bras restituent 80 % ou plus de sites explorés au jalon 600 ; le bras instrumental n'augmente pas le nombre d'ingestions sur ces scénarios. Au jalon 600, les paires consommées sont respectivement **2/2**, **1/1**, **0/1** (OFF/ON) sur ces trois conditions. Une unique ingestion est constatée en restored libre dans chaque bras ; les quatre autres vies ne mangent pas. **Allonger la durée à 600 pas ne rend pas le détecteur calibrable** dans ce corpus.

Ce contrôle long est indépendant du calcul détaillé de 16 vies A2.10b ; **ne pas sommer les fenêtres des deux cohortes**, ni confondre 6 vies cognitives et 16 vies historiques avec les mondes purement physiques de A2.13/14. L'exécution sur deux Python n'ajoute pas de seeds de développement supplémentaires.

## Hypothèses départagées

- **H_goal : insuffisant comme cause immédiate** : les 22 objectifs suivis reçoivent 22 résultats physiquement/subjectivement vérifiés. Il faut encore mesurer la fréquence de choix d'objectif sur l'ensemble de la vie, mais aucun résultat de cette cohorte n'est `unknown` au niveau followup.
- **H_agency : principal goulet documenté en amont** : **8/22** résultats restent sans jugement admissible parce que le jugement subjectif demeure `unknown`; la prudence est nécessaire lorsque l'individu ne dispose pas d'un indice pertinent.
- **H_join : pas de refus UC**, 14 jointures admises sur 14 jugements self/world. En revanche **4/14** paires admissibles expirent au pas requis sans diagnostic éveillé ; conserver cette absence plutôt que créer un jugement pendant le sommeil.
- **H_window : verrou déterminant** : les 10 paires consommées réparties entre 16 vies ne produisent jamais deux échecs admis dans une fenêtre de 12. Le maximum de succès est 2, celui des échecs est 1, jamais simultanément 2+2. Des durées autonomes plus longues, sans événements admissibles supplémentaires, ne corrigent pas ce manque.
- **Alimentation et agency indépendantes** : les **6 vrais repas** ne doivent être imputés à une intention ou classés `self` qu'après les contrôles indépendants de résultats et de perception. Ni la réussite alimentaire seule ni une prédiction correcte ne démontrent la responsabilité causale.

## C1–C8 et décision

| Critère | Verdict A2.15 |
| --- | --- |
| C1 Jugement subjectif | **PARTIAL** : 14 jugements self/world crédibles au sens des reçus, 8 inconnus, calibration non atteinte |
| C2 Distinction causale | **PARTIAL** : provenance et indécidabilité respectées ; causalité externe non prouvée |
| C3 Diversité | **PARTIAL** hérité : A2.6 conserve la diversité relative ; pas d'amélioration de compétence |
| C4 Compétence alimentaire vécue | **PARTIAL** : 6 ingestions A2.10b, résultat négatif en longues vies perturbées |
| C5 Discrimination P-48 | **INCONCLUSIVE** pour cet audit d'attrition |
| C6 Stabilité | **PARTIAL** technique sur 600 pas, calibration toujours absente |
| C7 Reproductibilité | **PASS borné** : 16 journaux scellés et deux Python, A2.6 6×600 sur deux Python, pas davantage de seeds scientifiques |
| C8 Conformité | **PASS borné** : aucun changement runtime, norme ou frontières épistémiques |

**VERDICT GLOBAL Stage12 PARTIAL, issue #110 OPEN, réception opérateur NON EFFECTUÉE.**

## Décision posthoc, pour une campagne séparément préenregistrée

Ne pas abaisser arbitrairement le seuil de 2 succès +2 échecs/12, ne pas ignorer des diagnostics vides, ne pas créer une preuve causale depuis une comparaison prédictive, ne pas supprimer la suspension `unknown`, ne pas redéclarer de vrai sommeil comme éveil. La prochaine campagne A2.16 devra confronter les **8 jugements `unknown`** aux indices effectivement perçus et aux résultats connus, pour distinguer des abstentions légitimes (contre-factuels irréductiblement inconnus) de lacunes d'observation accessibles dans les frontières existantes, **sans** inventer un critère spécifique aux baies. Elle devra aussi mesurer la fréquence des **échecs admissibles** et l'effet de leur concentration temporelle sans chercher à faire passer artificiellement la fenêtre. Toute correction cognitive exige une ablation ON/OFF sur vies réellement autonomes et des contre-exemples nocifs/retardés. Le modèle de prédiction relationnelle A2.14 reste un résultat de laboratoire NO-GO pour le runtime par défaut.
