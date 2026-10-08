# Citation du jour

Application web qui affiche une citation au hasard, composée de trois conteneurs Docker orchestrés avec Docker Compose.

## Schéma

```mermaid
flowchart LR
    U[Navigateur] -->|localhost:8081| N
    subgraph Réseau Docker Compose
        N[nginx<br/>reverse proxy<br/>port 80]
        F[front<br/>Node.js<br/>port 3000]
        B[back<br/>Python Flask<br/>port 5000]
        N -->|/| F
        N -->|/api/| B
    end
```

1. Le navigateur demande `localhost:8081` : nginx renvoie la page du front.
2. La page demande `/api/quote` : nginx transmet au back, qui renvoie une citation en JSON.
3. La page affiche la citation.

## Choix techniques

| Service | Techno | Justification |
|---|---|---|
| back | Python / Flask | Crée une petite API en quelques lignes. Image `slim` légère avec Python préinstallé. |
| front | Node.js | Très répandu pour le web. Image `alpine` légère, exécution avec un utilisateur non-root. |
| nginx | nginx | Porte d'entrée unique : redirige `/` vers le front et `/api/` vers le back. Léger et rapide. |
| orchestration | Docker Compose | Lance les trois services en une commande et les relie dans un même réseau. |

Bonnes pratiques appliquées :
- Dépendances copiées avant le code pour profiter du cache Docker.
- Seul nginx est exposé sur la machine : front et back ne sont joignables qu'à travers lui.
- Arrêt propre des applications (code de sortie 0) à la réception du signal `SIGTERM`.
- `HEALTHCHECK` sur le front pour vérifier qu'il répond.

## Lancer le projet

```bash
docker compose up --build
```

Puis ouvrir http://localhost:8081

Pour tout arrêter :

```bash
docker compose down
```

## Benchmarks et limites de ressources

Test : 20 000 requêtes sur `/api/quote`, 50 simultanées (`ab -l -n 20000 -c 50`).

| Mesure | Sans limites | Avec limites |
|---|---|---|
| Requêtes par seconde | 1497 | 400 |
| Temps moyen par requête | 33 ms | 125 ms |
| Requêtes en échec | 0 | 0 |

Consommation mémoire mesurée (`docker stats`) : back 22 Mo au repos et 57 Mo sous charge, nginx et front environ 9 Mo.

Limites choisies (environ deux fois le maximum mesuré) :
- back : 0,5 CPU, 128 Mo
- front : 0,25 CPU, 64 Mo
- nginx : 0,25 CPU, 64 Mo

Aucune erreur avec les limites : la mémoire est suffisante. Le débit baisse car le CPU devient le facteur limitant, mais 400 requêtes par seconde suffisent largement pour ce projet, et les limites protègent la machine.