# Image de base : Python 3.11 en variante "slim"
FROM python:3.11-slim

# Métadonnées de l'image
LABEL maintainer="dev@example.com"
LABEL description="Back du projet Citation du jour - API Flask"

WORKDIR /app

# Copie de la liste des dépendances seule, avant le code
COPY requirements.txt .

# Installation des dépendances (Flask) pendant le build
# --no-cache-dir : ne garde pas les téléchargements, image plus légère
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code de l'application (app.py)
COPY . .

# Opération sur l'OS : création d'un utilisateur système sans droits admin
# --system : compte de service, sans mot de passe ni connexion possible
# --no-create-home : pas de dossier personnel, inutile ici
RUN useradd --system --no-create-home appuser

# Sécurité : l'API s'exécute avec cet utilisateur et non en root
USER appuser

ENV PORT=5000

EXPOSE 5000

CMD ["python", "app.py"]