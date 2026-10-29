# Docker Cloud : Citation du jour

## Contexte

Ce projet simule la mise en place d'un **mini-cloud basé sur Docker** : une infrastructure où chaque service tourne dans son propre conteneur, avec ses ressources, son réseau et son stockage définis.

Pour démontrer cette infrastructure, elle héberge une application simple : **Citation du jour**, un site en français qui affiche une citation tirée au hasard. Le sujet autorise un "Hello World" ; nous avons choisi une application à peine plus riche pour montrer de vrais échanges entre services (le front demande une citation au back, en passant par le serveur web).

L'intérêt du projet n'est donc pas l'application elle-même, mais l'architecture qui l'héberge : images personnalisées, orchestration, isolation réseau, persistance des données, allocation des ressources et outils de CI/CD.

## Démarrage rapide

Prérequis : Docker Desktop (ou Docker Engine avec le plugin Compose).

```bash
cd projet-final
cp .env.example .env
docker compose up -d --build
```

Puis ouvrir **http://localhost:8081**.

Lancer les conteneurs de CI/CD (à la demande) :

```bash
docker compose --profile ci run --rm lint
docker compose --profile ci run --rm tests
```

Pour tout arrêter :

```bash
docker compose down
```

## Vue d'ensemble

| Service | Rôle | Technologie | Lancement | Accessible depuis la machine |
|---|---|---|---|---|
| nginx | Serveur web, point d'entrée unique (reverse proxy) | nginx (Alpine) | `docker compose up` | Oui, port 8081 |
| front | Sert la page affichée à l'utilisateur | Node.js 20 (Alpine) | `docker compose up` | Non, uniquement via nginx |
| back | API qui fournit les citations | Python 3.11 / Flask | `docker compose up` | Non, uniquement via nginx |
| lint | CI/CD : analyse la qualité du code du back | Python 3.11 / flake8 | À la demande (`--profile ci`) | Non, aucun réseau |
| tests | CI/CD : teste l'application de bout en bout | Python 3.11 / pytest | À la demande (`--profile ci`) | Non |

![Schéma de l'architecture](schema.png)

## Pourquoi Docker plutôt qu'une virtualisation classique

Une machine virtuelle (VMware, VirtualBox...) virtualise un ordinateur complet : chaque VM embarque son propre système d'exploitation. Un conteneur Docker, lui, partage le noyau de la machine hôte et n'embarque que l'application et ses dépendances.

| Critère | Machine virtuelle | Conteneur Docker |
|---|---|---|
| Contenu | Un OS complet par VM | L'application et ses dépendances |
| Taille | Plusieurs Go | Quelques dizaines à centaines de Mo (nos images : ~50 à 200 Mo) |
| Démarrage | Plusieurs minutes | Moins d'une seconde |
| Densité | Quelques VM par machine | Des dizaines de conteneurs par machine |
| Reproductibilité | Configuration souvent manuelle | Décrite dans un Dockerfile, identique partout |
| Ressources | Allouées par VM, souvent surdimensionnées | Limites fines par conteneur (ici : 0,25 CPU, 64 Mo) |

Dans ce projet, cinq services tournent sur une seule machine, démarrent en quelques secondes et consomment ensemble moins de 100 Mo de mémoire au repos. Avec des VM, il en aurait fallu plusieurs, avec chacune son système à installer et à maintenir.

Nuance : sur macOS et Windows, Docker Desktop fait tourner les conteneurs dans une petite VM Linux unique, partagée par tous les conteneurs. Sur un serveur Linux, il n'y a aucune VM.

## Images de base et personnalisation

Aucune image n'est utilisée telle quelle. Chaque image part d'une **image de base officielle** (`python:3.11-slim`, `node:20-alpine`, `nginx:alpine`) qui ne fournit que le système et l'environnement d'exécution, et nous la personnalisons : notre code, nos dépendances, nos utilisateurs, notre configuration et nos réglages. Toutes les personnalisations sont détaillées dans les sections suivantes.

Une fois construites, nos images n'ont plus besoin de Docker Hub : elles peuvent être exportées en fichier et rechargées sur une autre machine, sans aucun registre.

```bash
docker save citation-du-jour-back -o back.tar
docker load -i back.tar
```

## Images : choix au build

Les cinq images sont construites à partir de nos propres Dockerfiles (`build:` dans le compose).

### Image back (`back/Dockerfile`)

| Élément | Choix | Justification |
|---|---|---|
| Image de base | `python:3.11-slim` | Python préinstallé, variante Debian allégée (~150 Mo). Plus compatible qu'Alpine pour les bibliothèques Python. |
| Dépendance | Flask (`requirements.txt`) | Micro-framework web : une API en quelques lignes. Seule dépendance du projet. |
| Installation | `pip install --no-cache-dir -r requirements.txt` | `--no-cache-dir` ne conserve pas les fichiers téléchargés : image plus légère. |
| Ordre des couches | `requirements.txt` copié et installé **avant** le code | Si seul le code change, la couche d'installation reste en cache : rebuilds beaucoup plus rapides. |
| Fichiers copiés | `app.py`, `citations.json` | Le code de l'API et une version par défaut des citations. |
| Opération sur l'OS | `RUN useradd --system --no-create-home appuser` | Crée un compte de service sans mot de passe ni dossier personnel. |
| Utilisateur | `USER appuser` | Sécurité : l'API ne tourne pas en root. Placé après `pip install`, qui a besoin des droits root pour installer Flask. |
| Variable | `ENV PORT=5000` | Port par défaut lu par `app.py`, surchargé au run par le compose. |
| Port | `EXPOSE 5000` | Documente le port d'écoute. N'ouvre rien sur la machine. |

### Image front (`front/Dockerfile`)

| Élément | Choix | Justification |
|---|---|---|
| Image de base | `node:20-alpine` | Node.js préinstallé sur Alpine Linux : la variante la plus légère (~190 Mo contre ~1 Go pour l'image complète) et la plus petite surface d'attaque. Le front n'utilise aucun module natif, donc la libc d'Alpine (musl) ne pose pas de problème. |
| Opération sur l'OS | `RUN chown -R node:node /app` | Donne le dossier de l'application à l'utilisateur `node` (fourni par l'image). Fait avant `USER`, car seul root peut changer un propriétaire. |
| Utilisateur | `USER node` | Sécurité : l'application ne tourne pas en root. |
| Dépendances | `package.json` et `package-lock.json` copiés avant le code | Même logique de cache que pour le back. |
| Installation | `npm ci` | Installe exactement les versions du `package-lock.json` : builds reproductibles. Aucune dépendance externe pour l'instant (serveur basé sur le module `http` intégré à Node). |
| Copie | `COPY --chown=node:node` | Sans `--chown`, les fichiers copiés appartiendraient à root malgré `USER node`. |
| Exclusions | `.dockerignore` (`node_modules`, `.git`, logs) | Ces fichiers ne sont pas envoyés au build : build plus rapide, image plus propre. |
| Variables | `NODE_ENV=production`, `PORT=3000` | Mode production pour Node, port par défaut surchargé au run. |
| Port | `EXPOSE 3000` | Documente le port d'écoute. |
| Santé | `HEALTHCHECK` toutes les 30 s sur `/health` | Docker vérifie que l'application répond ; le conteneur passe `unhealthy` après 3 échecs. Le port est lu dans `PORT`, il suit donc la configuration. |

### Image serveur web (`nginx/Dockerfile`)

| Élément | Choix | Justification |
|---|---|---|
| Image de base | `nginx:alpine` | Serveur web léger et performant, très utilisé en production. |
| Configuration | `default.conf.template` copié dans `/etc/nginx/templates/` | Au démarrage, nginx remplace `${FRONT_PORT}` et `${BACK_PORT}` par leurs valeurs et génère sa configuration. Les ports ne sont donc écrits qu'à un seul endroit : le `.env`. |
| Routage | `/` vers le front, `/api/` vers le back | nginx est le seul point d'entrée. Le `/` final de `proxy_pass` retire le préfixe `/api` avant de transmettre au back. |
| Logs | `citation-access.log` et `citation-error.log` | L'image officielle redirige ses logs par défaut vers la console. Nous écrivons dans de vrais fichiers pour les conserver dans un volume. |
| Port | `EXPOSE 80` | Port d'écoute de nginx dans le conteneur. |

### Image lint (`lint/Dockerfile`)

| Élément | Choix | Justification |
|---|---|---|
| Image de base | `python:3.11-slim` | Même version de Python que le back : le code est analysé avec la version qui l'exécute. |
| Dépendance | flake8 (`requirements.txt`) | Outil de référence pour vérifier le style (PEP 8) et les erreurs probables du code Python. |
| Installation | `pip install --no-cache-dir` | Image plus légère. |
| Opération sur l'OS | `RUN useradd --system --no-create-home linter` | Le linter ne fait que lire le code : il n'a besoin d'aucun droit. |
| Dossier de travail | `WORKDIR /code` | Le code du back y est monté au run, en lecture seule. |

### Image tests (`tests/Dockerfile`)

| Élément | Choix | Justification |
|---|---|---|
| Image de base | `python:3.11-slim` | Même base que le back et le lint : une seule base Python à maintenir. |
| Dépendances | pytest, requests (`requirements.txt`) | pytest lance les tests et produit un rapport ; requests envoie les requêtes HTTP vers l'application. |
| Installation | `pip install --no-cache-dir` | Image plus légère. |
| Opération sur l'OS | `RUN useradd --system --no-create-home tester` | Les tests n'ont besoin d'aucun droit d'administration. |
| Fichiers copiés | `test_app.py` | Trois tests : page d'accueil, API, route de santé du front. |
| Variable | `ENV BASE_URL=http://nginx` | Adresse de l'application testée, remplaçable au run. |

## Entrypoints choisis

| Image | Entrypoint / commande | Forme | Justification |
|---|---|---|---|
| back | `CMD ["python", "app.py"]` | exec | Python est le processus principal (PID 1) et reçoit directement les signaux d'arrêt. `CMD` plutôt qu'`ENTRYPOINT` : on peut remplacer la commande pour diagnostiquer (`docker compose run back sh`). |
| front | `CMD ["node", "server.js"]` | exec | Même raison : Node est PID 1. Avec la forme shell (`CMD node server.js`), un shell serait PID 1 et ne transmettrait pas le signal à Node. |
| nginx | Entrypoint de l'image officielle (`/docker-entrypoint.sh`), conservé volontairement | exec | Ce script exécute les scripts de `/docker-entrypoint.d/`, dont celui qui transforme nos templates en configuration (remplacement de `${FRONT_PORT}` et `${BACK_PORT}`), puis lance nginx au premier plan. C'est ce mécanisme qui permet de passer les ports en arguments au run. |
| lint | `ENTRYPOINT ["flake8"]` + `CMD ["--max-line-length=100", "."]` | exec | Conteneur à mission unique : `ENTRYPOINT` fixe l'outil, `CMD` fournit les options par défaut, remplaçables au lancement sans rebuild. |
| tests | `ENTRYPOINT ["pytest"]` + `CMD ["-v", "-p", "no:cacheprovider"]` | exec | Même logique. `-v` détaille chaque test ; `-p no:cacheprovider` désactive le cache de pytest, inutile dans un conteneur jetable et impossible à écrire sans droits root. |

Exemple de remplacement des options sans rebuild :

```bash
docker compose --profile ci run --rm lint --max-line-length=79 .
```

## Gestion des signaux d'arrêt (SIGTERM)

À l'arrêt (`docker stop`, `docker compose down`), Docker envoie `SIGTERM` au processus principal, attend 10 secondes, puis force l'arrêt avec `SIGKILL` (code de sortie 137).

Avant correction, Python et Node, lancés comme PID 1, ignoraient `SIGTERM` : chaque arrêt prenait 10 secondes et se terminait par un code 137. Nous avons donc ajouté une gestion explicite :

| Service | Gestion | Résultat |
|---|---|---|
| back | `signal.signal(signal.SIGTERM, ...)` dans `app.py` : quitte avec `sys.exit(0)` | Code de sortie 0, arrêt immédiat |
| front | `process.on("SIGTERM", ...)` dans `server.js` : ferme le serveur puis quitte avec le code 0 | Code de sortie 0, arrêt immédiat |
| nginx | Gestion native par nginx | Code de sortie 0 |
| lint, tests | Conteneurs éphémères : ils terminent leur tâche et s'arrêtent seuls | Code 0 si succès, 1 si échec |

Les formes exec des `CMD` sont indispensables : elles garantissent que le signal arrive bien à l'application et non à un shell intermédiaire.

## Arguments du run (docker-compose.yml et .env)

Tous les réglages du run sont centralisés dans le fichier `.env`, lu automatiquement par Docker Compose. Pour modifier un port ou les ressources d'un service, on change une ligne du `.env` puis on relance `docker compose up -d` : aucun rebuild n'est nécessaire. Test réalisé : passer `BACK_MEMORY` de `128M` à `256M` ne recrée que le conteneur du back, dont la limite passe à 256 Mo.

Le fichier `.env` n'est pas versionné (il est dans le `.gitignore`, car dans un vrai projet il contiendrait des secrets). Le fichier `.env.example`, versionné, sert de modèle.

### Variables du `.env`

| Variable | Valeur | Rôle |
|---|---|---|
| `COMPOSE_PROJECT_NAME` | `citation-du-jour` | Préfixe des conteneurs, réseaux et volumes |
| `NGINX_PORT` | `8081` | Port d'accès depuis la machine (seul port ouvert) |
| `FRONT_PORT` | `3000` | Port d'écoute du front dans le réseau Docker |
| `BACK_PORT` | `5000` | Port d'écoute du back dans le réseau Docker |
| `BACK_CPUS` / `BACK_MEMORY` | `0.5` / `128M` | Ressources du back |
| `FRONT_CPUS` / `FRONT_MEMORY` | `0.25` / `64M` | Ressources du front |
| `NGINX_CPUS` / `NGINX_MEMORY` | `0.25` / `64M` | Ressources de nginx |
| `LINT_CPUS` / `LINT_MEMORY` | `0.5` / `128M` | Ressources du lint |
| `TESTS_CPUS` / `TESTS_MEMORY` | `0.5` / `128M` | Ressources des tests |

### Arguments par service : application

| Argument | back | front | nginx |
|---|---|---|---|
| `build` | `./back` | `./front` | `./nginx` |
| `environment` | `PORT=${BACK_PORT}` | `PORT=${FRONT_PORT}` | `FRONT_PORT`, `BACK_PORT` |
| `ports` | aucun | aucun | `${NGINX_PORT}:80` |
| `networks` | `back-net` | `front-net` | `front-net` et `back-net` |
| `volumes` | `./back/citations.json:/app/citations.json:ro` | aucun | `nginx-logs:/var/log/nginx` |
| `deploy.resources.limits` | `${BACK_CPUS}`, `${BACK_MEMORY}` | `${FRONT_CPUS}`, `${FRONT_MEMORY}` | `${NGINX_CPUS}`, `${NGINX_MEMORY}` |
| `depends_on` | aucun | aucun | `front`, `back` |

### Arguments par service : CI/CD

| Argument | lint | tests |
|---|---|---|
| `build` | `./lint` | `./tests` |
| `profiles` | `ci` | `ci` |
| `environment` | aucun | `BASE_URL=http://nginx:80` |
| `networks` | aucun (`network_mode: none`) | `front-net` |
| `volumes` | `./back:/code:ro` | aucun |
| `deploy.resources.limits` | `${LINT_CPUS}`, `${LINT_MEMORY}` | `${TESTS_CPUS}`, `${TESTS_MEMORY}` |
| `depends_on` | aucun | `nginx` |

**`environment`** transmet des variables **à l'intérieur** du conteneur. Elles remplacent les valeurs par défaut des `ENV` des Dockerfiles.

**`ports`** : seul nginx publie un port sur la machine. Le front et le back ne sont joignables qu'à travers lui.

**`profiles: ["ci"]`** : le lint et les tests ne démarrent pas avec `docker compose up`, uniquement quand on les demande, comme dans un pipeline CI.

### Équivalent avec `docker run`

Chaque argument du compose correspond à une option de `docker run`. Exemple pour le back :

```bash
docker build -t citation-back ./back
docker network create --internal back-net
docker run -d --name back \
  --network back-net \
  -e PORT=5000 \
  -v "$(pwd)/back/citations.json:/app/citations.json:ro" \
  --cpus 0.5 --memory 128m \
  citation-back
```

| `docker run` | `docker-compose.yml` |
|---|---|
| `-e PORT=5000` | `environment` |
| `-p 8081:80` | `ports` |
| `--network back-net` | `networks` |
| `-v ...:ro` | `volumes` |
| `--cpus 0.5` | `deploy.resources.limits.cpus` |
| `--memory 128m` | `deploy.resources.limits.memory` |

Le compose évite de retaper ces commandes pour chaque conteneur et garantit qu'elles sont toujours les mêmes.

## Ordre de démarrage (dépendances)

| Service | Dépend de | Raison |
|---|---|---|
| nginx | front, back | nginx redirige vers eux : ils doivent exister quand il démarre. |
| tests | nginx | Les tests interrogent l'application via nginx. Lancer les tests démarre automatiquement nginx, donc aussi le front et le back. |

Ordre obtenu : back et front, puis nginx, puis les tests.

`depends_on` garantit l'ordre de **démarrage** des conteneurs, mais pas que l'application soit déjà **prête** à répondre. C'est pourquoi le conteneur de tests attend lui-même que l'application réponde (jusqu'à 30 secondes) avant de lancer les tests.

## Réseaux

| Réseau | Membres | Particularité |
|---|---|---|
| `front-net` | nginx, front, tests | Réseau standard |
| `back-net` | nginx, back | `internal: true` : aucun accès à Internet |
| aucun | lint | `network_mode: none` : totalement isolé |

nginx est le seul conteneur présent dans les deux réseaux : c'est l'unique pont entre le front et le back. Les tests sont dans `front-net` : ils passent par nginx, comme un utilisateur, et ne peuvent pas joindre le back directement. Vérifications effectuées :

- nginx joint le back : `docker compose exec nginx wget -qO- http://back:5000/quote` renvoie une citation.
- Le front ne peut pas joindre le back : la même commande depuis le front renvoie `bad address 'back:5000'`.
- Le back n'a pas accès à Internet : une requête vers google.com échoue (`Temporary failure in name resolution`).

## Volumes

| Volume | Type | Rôle |
|---|---|---|
| `./back/citations.json` → back | Bind mount (fichier de la machine), lecture seule `:ro` | Les citations se modifient sans rebuild ni redémarrage. Le conteneur peut les lire mais pas les modifier. |
| `nginx-logs` → nginx | Volume nommé (géré par Docker) | Les logs de nginx survivent à la suppression du conteneur (`docker compose down`). Seul `docker compose down -v` les supprime. |
| `./back` → lint | Bind mount, lecture seule `:ro` | Le linter analyse le code du back sans pouvoir le modifier. |

## CI/CD : lint et tests

Les deux conteneurs CI/CD reproduisent les étapes d'un pipeline d'intégration continue : avant de déployer, on vérifie la qualité du code (lint), puis le bon fonctionnement de l'application (tests). Chacun renvoie un **code de sortie** : `0` si tout est bon, `1` sinon. C'est ce code qu'un outil de CI (GitHub Actions, GitLab CI...) utilise pour autoriser ou bloquer une mise en production.

### Lint

```bash
docker compose --profile ci run --rm lint
echo "Code de sortie : $?"
```

Résultat lors de sa première exécution :

```
./app.py:29:39: W292 no newline at end of file
Code de sortie : 1
```

flake8 a détecté un fichier sans retour à la ligne final (convention PEP 8). Après correction : aucune remarque, code de sortie `0`.

### Tests

```bash
docker compose --profile ci run --rm tests
echo "Code de sortie : $?"
```

| Test | Vérifie |
|---|---|
| `test_page_accueil` | La page d'accueil répond (code 200) et contient « Citation du jour » |
| `test_api_renvoie_une_citation` | L'API renvoie une citation avec un texte et un auteur |
| `test_healthcheck_front` | La route de santé du front répond `OK` |

Résultat : `3 passed`, code de sortie `0`.

## Allocation des ressources et benchmarks

### Méthode

1. Mesure de la consommation au repos avec `docker stats --no-stream`.
2. Test de charge **sans limites** avec ApacheBench : 20 000 requêtes sur l'API, 50 simultanées.
3. Choix des limites à partir des mesures.
4. Même test de charge **avec limites**, pour comparer.

Commande de test :

```bash
ab -l -n 20000 -c 50 http://127.0.0.1:8081/api/quote
```

L'option `-l` accepte des réponses de longueurs différentes : sans elle, ApacheBench compte à tort comme « échecs » les citations dont la taille diffère de la première.

### Mesures de consommation

| Service | Mémoire au repos | Mémoire sous charge |
|---|---|---|
| back | 22 Mo | 57 Mo |
| front | 9 Mo | 9 Mo |
| nginx | 8 Mo | 9 Mo |

### Limites choisies

Environ deux fois le pic de mémoire mesuré, pour garder une marge :

| Service | CPU | Mémoire | Raison |
|---|---|---|---|
| back | 0,5 | 128 Mo | Service le plus sollicité : chaque requête API est traitée par Python. |
| front | 0,25 | 64 Mo | Sert une seule page statique, très peu sollicité. |
| nginx | 0,25 | 64 Mo | Ne fait que transmettre les requêtes, très léger. |
| lint | 0,5 | 128 Mo | Tâche courte (quelques secondes) ; Python et flake8 chargés en mémoire. |
| tests | 0,5 | 128 Mo | Tâche courte ; Python, pytest et requests chargés en mémoire. |

### Résultats

| Mesure | Sans limites | Avec limites |
|---|---|---|
| Requêtes par seconde | 1497 | 400 |
| Temps moyen par requête | 33 ms | 125 ms |
| Requêtes en échec | 0 | 0 |

### Analyse

- **Aucune erreur avec les limites** : la mémoire allouée est suffisante, aucun conteneur n'a été arrêté pour dépassement de mémoire.
- **Débit divisé par environ 3,7** : le CPU est le facteur limitant de l'application, pas la mémoire. Une limite CPU ralentit un conteneur sans le tuer, alors qu'un dépassement de mémoire l'arrête (code 137).
- **Conclusion** : 400 requêtes par seconde suffisent largement pour ce service, et les limites protègent la machine si un conteneur s'emballe. Si le besoin augmentait, c'est le CPU du back qu'il faudrait augmenter en priorité (`BACK_CPUS` dans le `.env`).

## Vérifier le fonctionnement

Après `docker compose up -d --build`, depuis le dossier `projet-final` :

| Vérification | Commande | Résultat attendu |
|---|---|---|
| Conteneurs démarrés | `docker compose ps` | 3 services `running`, le front `(healthy)` après ~30 s |
| Application | ouvrir http://localhost:8081 | Une citation s'affiche, elle change à chaque rechargement |
| API via nginx | `curl http://localhost:8081/api/quote` | Une citation au format JSON |
| Front et back non exposés | `curl http://localhost:3000` | Connexion refusée |
| Back sans root | `docker compose exec back whoami` | `appuser` |
| Limites de ressources | `docker stats --no-stream` | Colonne LIMIT : 128MiB (back), 64MiB (front, nginx) |
| Isolation réseau | `docker compose exec front wget -qO- http://back:5000/quote` | `bad address 'back:5000'` |
| Back sans Internet | `docker compose exec back python -c "import urllib.request; urllib.request.urlopen('https://www.google.com', timeout=3)"` | Erreur de résolution de nom |
| Logs persistants | `docker compose exec nginx tail -n 3 /var/log/nginx/citation-access.log` | Les dernières visites, conservées après `down` puis `up` |
| Lint | `docker compose --profile ci run --rm lint` | Aucune remarque, code de sortie 0 |
| Tests | `docker compose --profile ci run --rm tests` | `3 passed`, code de sortie 0 |
| Arrêt propre | `docker compose down` | Arrêt en moins d'une seconde, sans attente de 10 s |

## Limites et pistes d'amélioration

- **Serveur de développement Flask** : suffisant pour ce projet, mais en production on utiliserait un serveur WSGI comme Gunicorn, capable de traiter plusieurs requêtes en parallèle.
- **Disponibilité réelle des services** : ajouter un healthcheck au back et à nginx permettrait d'utiliser `depends_on` avec `condition: service_healthy`, pour qu'un service ne démarre qu'une fois ses dépendances réellement prêtes.
- **Passage à l'échelle** : avec Docker Swarm, on pourrait lancer plusieurs répliques du back derrière nginx, les répartir sur plusieurs machines et ajuster leur nombre selon la charge.
- **Pipeline automatisé** : les conteneurs de lint et de tests pourraient être lancés automatiquement à chaque push, par exemple avec GitHub Actions.