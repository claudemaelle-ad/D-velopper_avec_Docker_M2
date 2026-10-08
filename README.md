# Projet Docker : Citation du jour

Dépôt des travaux pratiques Docker, organisé par séance.

## cours-1 : premiers Dockerfiles

Trois services "Hello World" construits instruction par instruction :
- back : Python / Flask
- front : Node.js
- nginx : page statique

Orchestrés avec un premier docker-compose.

## cours-2 : projet Citation du jour

Application web qui affiche une citation au hasard :
- front (Node.js) : affiche la page
- back (Python / Flask) : fournit les citations
- nginx : point d'entrée unique, redirige vers le front ou le back

Dockerfiles et docker-compose commentés, schéma et justification des choix dans `cours-2/README.md`.

## Lancer une séance

```bash
cd cours-1   # ou cours-2
docker compose up --build
```
