# Image de base : nginx en variante Alpine
# Choix : serveur web léger et rapide, très utilisé en production
FROM nginx:alpine

# Métadonnées de l'image
LABEL description="Reverse proxy du projet Citation du jour - nginx"

# Au démarrage, nginx y remplace ${FRONT_PORT} et ${BACK_PORT}
# par leurs valeurs, puis génère /etc/nginx/conf.d/default.conf
COPY default.conf.template /etc/nginx/templates/default.conf.template

EXPOSE 80

# Pas de CMD : l'image nginx démarre déjà le serveur automatiquement
