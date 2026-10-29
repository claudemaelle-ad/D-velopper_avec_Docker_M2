# Image de base : Python 3.11 en variante "slim"
# Choix : version légère (environ 150 Mo) avec Python déjà installé
FROM python:3.11-slim

# Métadonnées de l'image (n'ajoutent aucun fichier)
LABEL maintainer="dev@example.com"
LABEL description="Back du projet Citation du jour - API Flask"

# Dossier de travail dans le conteneur, créé s'il n'existe pas
WORKDIR /app

# Copie de la liste des dépendances seule, avant le code
# Choix : si seul le code change, l'installation reste en cache
COPY requirements.txt .

# Installation des dépendances (Flask) pendant le build
# --no-cache-dir : ne garde pas les téléchargements, image plus légère
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code de l'application (app.py, citations.json)
COPY . .

# Opération sur l'OS : création d'un utilisateur système sans droits admin
# --system : compte de service, sans mot de passe ni connexion possible
# --no-create-home : pas de dossier personnel, inutile ici
RUN useradd --system --no-create-home appuser

# Sécurité : l'API s'exécute avec cet utilisateur et non en root
# Placé après pip install, qui a besoin des droits root
USER appuser

# Port par défaut lu par app.py, remplacé au run par le compose
ENV PORT=5000

# Documente le port utilisé par l'API (n'ouvre rien sur la machine)
EXPOSE 5000

# Commande lancée au démarrage du conteneur
# Forme exec : Python est le processus principal et reçoit directement SIGTERM
CMD ["python", "app.py"]