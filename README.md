# Citation du jour, hébergée sur un mini-cloud Docker

Citation du jour est une petite application web en français. Quand on ouvre la page, elle affiche un titre « Citation du jour » suivi d'une citation d'un auteur célèbre (Socrate, Descartes, Pascal...), tirée au hasard à chaque rechargement.

Le projet a pour objectif de mettre en pratique la conteneurisation d'une application composée de plusieurs services, chacun dans son propre conteneur Docker. Le front, développé en Node.js, sert la page affichée à l'utilisateur. Le back, une petite API en Python avec Flask, fournit les citations au format JSON. Un serveur nginx joue le rôle de point d'entrée unique : il redirige les visites vers le front et les appels à l'API vers le back, si bien que seul son port est exposé sur la machine. L'ensemble est orchestré avec Docker Compose, qui construit et lance les services en une seule commande.

Pour le projet final (TP Docker Cloud), cette application sert de démonstration à une infrastructure de type cloud : l'enjeu n'est pas l'application elle-même, mais la façon dont elle est hébergée. Les images sont personnalisées, et les ressources allouées à chaque conteneur (CPU, mémoire) ainsi que les ports sont passés au lancement via un fichier `.env`. Deux réseaux isolent les services (le back n'est joignable que par nginx et n'a pas accès à Internet), un volume permet de modifier les citations sans reconstruire l'image, et un autre conserve les logs de nginx. Les applications tournent sans droits root et s'arrêtent proprement. Deux conteneurs de CI/CD complètent la stack : un linter (flake8) qui vérifie la qualité du code, et des tests de bout en bout (pytest) qui vérifient le fonctionnement de l'application. Les limites de ressources ont été choisies à partir de benchmarks.

## Organisation du dépôt

| Dossier | Contenu |
|---|---|
| **`projet-final/`** | **Rendu du TP Docker Cloud** : images, docker-compose, conteneurs CI/CD, documentation complète et schéma d'architecture |
| `cours-1/` | Séance 1 : premiers Dockerfiles "Hello World" (back, front, nginx) et premier docker-compose |
| `cours-2/` | Séance 2 : projet Citation du jour, réseaux, volumes, `.env`, limites de ressources et benchmarks |

## Lancer le projet final

```bash
cd projet-final
cp .env.example .env
docker compose up -d --build
```

Puis ouvrir **http://localhost:8081**.

Lancer les conteneurs de CI/CD :

```bash
docker compose --profile ci run --rm lint
docker compose --profile ci run --rm tests
```

La documentation détaillée (choix au build, entrypoints, gestion des signaux, arguments du run, réseaux, volumes, CI/CD, benchmarks, guide de vérification) se trouve dans [`projet-final/README.md`](projet-final/README.md).