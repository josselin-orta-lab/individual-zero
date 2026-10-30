# A2-R — observation réelle GitHub en lecture seule (30 octobre 2026)

Le connecteur GitHub actuellement disponible refuse la lecture directe des endpoints `/environments` (accès restreint). Une tentative externe n'a pas apporté de preuve. Il serait incorrect d'en déduire une configuration absente ou présente.

Cette tranche ajoute dans la CI de provenance **déjà existante** une sonde GET en lecture seule de l'environnement `i1-a2r-confirmatory`. Elle n'utilise aucun token privilégié, ne crée et ne modifie aucun environnement, ne configure aucune protection et n'autorise jamais de naissance. La sortie JSON ne contient ni personnes ni secrets et sépare `API_UNVERIFIABLE` d'une règle observable insuffisante ou d'une règle de revue observable. Une règle correctement observée n'atteste **ni restriction effective à main**, ni identité de l'approbateur futur, ni permanence du snapshot, ni autorisation. Même `REVIEW_RULE_OBSERVED` interdit tout lancement.

Validation pure Python 3.11/3.12 et observation en lecture seule dans la même CI. Aucun workflow confirmatoire, H192 0/96, L3 NOT_ESTABLISHED. Une lecture `API_UNVERIFIABLE` doit conduire à la demande d'une attestation indépendante disposant des accès minimaux appropriés, sans contournement et sans surpromesse.
