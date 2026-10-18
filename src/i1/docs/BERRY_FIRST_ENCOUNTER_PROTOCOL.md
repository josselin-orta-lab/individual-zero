# I1 : protocole complémentaire de première rencontre avec berry_b

## Motivation

Les neuf vies du monde garden du premier lot `a884bedd` ont consommé des `berry_a` mais **aucune berry_b**. L'absence de variation entre les toxicités ne prouve aucun apprentissage : le traitement n'a jamais été rencontré. La campagne nouvelle n'utilise pas le résultat comme oracle.

## Nouvelle écologie avant la naissance

Le mode enregistré `berry-b-first-v1`, réservé au monde `longlife-garden`, pose une ressource **berry_b inconnue** au point de naissance, rend l'eau physiquement accessible sur place et conserve les `berry_a` comme alternatives dans des cellules plus lointaines. Les ressources alimentaires à une case du point de naissance sont retirées pour isoler la première rencontre; les autres ressources, dangers et obstacles restent ceux de la variante du monde. Nourriture initiale 20, eau 75; aucune action, aucun inventaire, aucune valeur TD ou souvenir n'est préchargé. La carte d'opérateur ne devient pas un percept hors du champ visuel habituel.

Comparer `berry_b` à intégrité `-100, -10, 0` sur variantes 71/72/73, graines appariées 993071/72/73, 9 naissances irréversibles, jusqu'à 800 pas chacune. Géographie 0.3 et cognition-sommeil 0 fixées comme dans le protocole de mouvement. Code exact, digest du monde physique et configuration de naissance archivée par WAL. Le workflow `i1-berry-first-encounter.yml` est indépendant du protocole initial, et ses vies ne doivent jamais être additionnées à ses contrôles sous prétexte qu'elles partagent les mêmes valeurs de toxicité.

## Endpoints

1. Exposition réelle à berry_b : perceptions, collecte, inventaire, commande `manger` effectivement appliquée.
2. Variation d'intégrité après l'ingestion réelle, avec les autres effets continus distingués.
3. Persistance au-delà de la première ingestion, possibilité d'une seconde expérience avant décès.
4. Proposition future de l'option sous un besoin comparable, tendance TD apprise, franchissement du seuil et choix réalisé.
5. Courbe de changement de comportement uniquement lorsqu'une seconde occasion vécue existe, comparaison des morts conservée.

Si la première ingestion n'a pas lieu, verdict `INCONCLUSIVE_NO_EXPOSURE`. Si elle a lieu mais pas de seconde occasion, `INCONCLUSIVE_NO_REEXPOSURE`. Même deux rencontres ne suffisent pas à prouver causalement l'apprentissage sans distinguer connaissance acquise, observation, contexte et hasard. Aucun GO de survie ou de mémoire automatique. I0 et main inchangés.

**Actions GitHub** : [nouvelle matrice de première rencontre](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39120129262), commit `91c2a6b1d325e18b582a09b55b67b3d9efba030b`.
