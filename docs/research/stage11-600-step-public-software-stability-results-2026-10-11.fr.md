# Stage 11 : stabilité logicielle et relecture exacte sur 600 pas physiques

**11 octobre 2026 · DIAGNOSTIC PUBLIC DE DÉVELOPPEMENT · NON HELD-OUT · NON GOLDEN · NON SCIENTIFIQUE.** Stage 9 reste **NO-GO scientifique**. Stage 11 conserve sa distinction entre porte logicielle et validation finale par l'opérateur.

## Chaîne d'antériorité et SHA exacts

- [Protocole figé avant toute implémentation](stage11-600-step-public-software-stability-protocol.en.md) : commit **`81d231adcd4950a55ee63657e80b22486d61294d`**.
- Logiciel du diagnostic : `src/lab/stage11_600_step_software_probe.py`, commit **`f930f7673c73fe0e2f5a8083e060f6338544fe88`**.
- Déclenchement *à la demande* dans la CI complète, sans nouveau déclencheur permanent, avec 40 minutes de plafond de job et 25 minutes pour le diagnostic : commit **`fda5d2444f7cf2038fa0d910af7139b397284ca5`**. **C'est le SHA exact du code, du test, des configurations et du workflow validés.** Le durcissement complémentaire de l'audit des `signal_ids` est inclus.
- [GitHub Actions #38147281654](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38147281654) : **SUCCESS**. Python **3.11.17 : 924/924 tests PASS** et Python **3.12.15 : 924/924 tests PASS** ; les deux jobs complets SUCCESS, zéro échec ; **16 artefacts**, dont `stage11-600-step-software-diagnostic`. Le job rapide du même workflow a été `skipped` et n'est pas compté comme validation.
- Le diagnostic de **600 pas** a été exécuté **en plus** de la suite des 924 tests, sur Python 3.12.15. Ce ne sont pas 600 tests unitaires supplémentaires.

## Conditions effectivement exécutées

Le programme a créé **deux exemplaires indépendants** de `build_stage11_reference_runtime(enable_geography=True)`, sans modifier les règles, les budgets, le tempérament, le matériel ou la physique préexistante de la fixture. Exactement **600 pas physiques** ont été complétés dans chaque exemplaire. Des snapshots périodiques complets ont été pris et vérifiés **après les pas 1, 300 et 600**, dans le même ordre. Aucun replay différant par son calendrier de snapshots ni aucune restauration artificielle du corps n'a été utilisé.

**Attention au sens physique :** la fixture de référence hérite du monde Stage 4, avec déclin continu de nourriture/eau **nul** et coûts énergétiques des primitives **nuls**. C'est un environnement de vérification du code, **pas** un test de survie indépendante dans des conditions physiologiques adverses. Les conséquences de **ce monde déclaré** n'ont toutefois pas été modifiées en cours de vie.

## Mesures publiques observées sur les deux reproductions

| Mesure | Valeur observée |
| --- | ---: |
| Pas du monde réellement terminés | **600** |
| Captures physiques locales | **600** |
| Sites physiques distincts effectivement capturés | **600** |
| Commandes `se_deplacer` effectivement appliquées | **600** |
| Évaluations intrinsèques journalisées | **600** |
| Transitions du profil Global Modulation | **0** |
| UC réellement acceptées | **9 605** |
| Demandes UC refusées | **0** |
| Événements du journal causal technique | **42 041** |
| Deuxième relecture indépendante et identique | **TRUE** |

L'absence de transition du profil sur cette trajectoire signifie qu'il n'y avait pas de séquence enregistrée de changement de profil dans ce monde de référence ; **elle ne démontre pas** les entrées/sorties des profils de menace ou récupération. Celles-ci sont couvertes séparément par les tests ciblés. Aucun résultat sur le danger inconnu, les impasses avec UC contraintes ou l'apprentissage de contingence n'est inféré de cette trajectoire favorable à l'exploration.

### Empreintes et captures

| Élément | SHA-256 |
| --- | --- |
| Configuration et entrées | `b067b8027ac950444854a3848ab36084573842439291bab92a66972e490f3840` |
| Journal canonique complet | `988a8467e71e1db507c81d01b2b4c8625d5138d6edb23baeab4f6869cbb1f559` |
| Dernier hash de la chaîne causale | `7ccf1c46403ae30e677b13a3b0ebece12608c398425b24cdb77aa49917cf8614` |
| Tous les propriétaires causaux, état final canonique | `d2de8e5d13b34f0d7b33f052e59c2f454caa6948cf06a02aa34e9fdac49105b0` |
| Empreinte du diagnostic complet | `88a3fe2edec8ab8d15fce5943cb40730fcc48faabc6009ef82b8436df62d4a18` |

| Capture périodique | Identifiant stable | SHA-256 du snapshot |
| --- | --- | --- |
| Pas 1 | `4e9f5dfd05f55f7fbd83ab59e6db78a4764e5a8bb5d3443e541b07166361c36c` | `3fa5009ea4a8986ce11628e4083645324dcd6cf0ff6f931955b93a6f64092054` |
| Pas 300 | `0be545389b67b5625058e6ea4ea4a0a31cbd856370b68d71917902ac8e0886ff` | `4115218e2c4bc95db6f1cbe54e7ce8efde71f802b18aa84a016fd3a06599cd04` |
| Pas 600 | `5a4002888401abae8be12be13137840328d00dd15637a6f96bd4d705da38a883` | `75f6aed0a242488fb3fb14c880ba1d5e2a1f5dac26d8dbfdde16c735efa7a83d` |

Les deux exécutions ont le **même** manifeste des actions, des 600 captures, des compteurs, des identifiants/hashes de snapshots, du journal, de ses propriétaires et de l'empreinte de diagnostic. Les événements `stage11_intrinsic_evaluation` ont été vérifiés contre une réutilisation interne du même `signal_id`. La chaîne du journal a passé sa vérification intégrale.

**Limitation importante :** les trois snapshots ont été **capturés/vérifiés**, mais le test de 600 pas ne restaure pas ces snapshots et ne prouve pas une continuation après chacune de leurs restaurations. Cette propriété fait l'objet de tests de restauration distincts.

## Interprétation et suite

**Hypothèse logicielle soutenue :** dans ce monde public et ces 600 pas, l'implémentation Stage 11 peut produire des actions physiques exploratoires sur une longue trajectoire sans divergence entre deux exécutions indépendantes ni dépassement rapporté des UC. **Aucune conclusion** sur une exploration optimale, une survie autonome adversariale, l'apprentissage de nouveaux dangers ou une validation scientifique absolue n'est autorisée.

La [procédure de validation humaine](stage11-validation-operateur-600-pas.fr.md) décrit la future séance en conditions réelles, avec un verdict explicite **GO/NO-GO/EN ATTENTE**. Le projet a également exprimé une nouvelle orientation vers la **mort définitive sans rollback**, non encore intégrée au runtime v1.2.1 de cette PR : l'acceptation finale doit d'abord réconcilier cette architecture et ses conséquences physiques. Stage 9 demeure scientifiquement NO-GO et la validation scientifique complète des modules relève de la fin du projet.

### Reproduction depuis le SHA exact

```sh
python -m pip install -e .
python -m unittest discover -s tests -q
python -m lab.stage11_600_step_software_probe
```

L'appel direct à la sonde imprime un JSON `stage11_600_step_software=` dont `scientific_verdict=null`. Le job `ci-full` sur [#38147281654](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38147281654) a vérifié cette sortie et publié son artefact. Les commits purement documentaires qui suivent ce SHA ne constituent pas une nouvelle version de code testée.

**Stage 11 : porte logicielle en cours de clôture ; acceptation opérateur EN ATTENTE. PR #25 Draft, non fusionnée, `main` et spécification normative anglaise inchangés.**
