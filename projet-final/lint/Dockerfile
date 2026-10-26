# Image de base : Python 3.11 slim, même base que le back
# Choix : flake8 est un outil Python, et analyser le code avec
# la même version de Python que celle qui l'exécute évite les écarts
FROM python:3.11-slim

LABEL description="Lint du code Python du back - flake8"

# Installation de flake8 (seule dépendance)
# --no-cache-dir : ne garde pas les fichiers téléchargés, image plus légère
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Opération sur l'OS : utilisateur sans droits admin
# Le linter ne fait que lire le code, il n'a besoin d'aucun droit
RUN useradd --system --no-create-home linter
USER linter

# Dossier où le code à analyser sera monté au run (volume)
WORKDIR /code

# ENTRYPOINT : l'exécutable fixe du conteneur, toujours flake8
# CMD : ses arguments par défaut, remplaçables au lancement
# Ici : lignes de 100 caractères max, analyse du dossier courant
ENTRYPOINT ["flake8"]
CMD ["--max-line-length=100", "."]
