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

ENV PORT=5000

EXPOSE 5000

CMD ["python", "app.py"]