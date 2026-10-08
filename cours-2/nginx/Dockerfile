# Image de base : nginx en variante Alpine
# Choix : serveur web léger et rapide, très utilisé en production
FROM nginx:alpine

# Métadonnées de l'image
LABEL description="Reverse proxy du projet Citation du jour - nginx"

# Remplace la configuration par défaut par la nôtre
# nginx lit automatiquement les fichiers du dossier conf.d
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

# Pas de CMD : l'image nginx démarre déjà le serveur automatiquement