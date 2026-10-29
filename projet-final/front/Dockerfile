# Image de base : Node.js 20 en variante Alpine
# Choix : la plus légère (environ 190 Mo), moins de failles de sécurité
FROM node:20-alpine

# Métadonnées de l'image
LABEL description="Front du projet Citation du jour - Node.js"

# Dossier de travail dans le conteneur
WORKDIR /app

# Opération sur l'OS : donne le dossier à l'utilisateur "node" (fourni par l'image)
# Doit être fait avant USER, car seul root peut changer le propriétaire
RUN chown -R node:node /app

# Sécurité : la suite s'exécute avec un utilisateur sans droits admin
USER node

# Copie des fichiers de dépendances seuls, avant le code
# Choix : si seul le code change, l'installation reste en cache
COPY --chown=node:node package*.json ./

# Installation des dépendances à l'identique du package-lock.json
# Choix : npm ci garantit un build reproductible
RUN npm ci

# Copie du code (server.js, index.html), sauf ce qui est dans .dockerignore
COPY --chown=node:node . .

# Mode production et port par défaut, remplacé au run par le compose
ENV NODE_ENV=production \
    PORT=3000

# Documente le port utilisé par l'application (n'ouvre rien)
EXPOSE 3000

# Vérifie toutes les 30 s que l'application répond sur /health
# Le port est lu dans la variable PORT : il suit la configuration du .env
# Le conteneur est marqué "unhealthy" après 3 échecs
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:' + (process.env.PORT || 3000) + '/health', (r) => process.exit(r.statusCode === 200 ? 0 : 1)).on('error', () => process.exit(1))"

# Commande lancée au démarrage du conteneur
# Forme exec : Node est le processus principal et reçoit directement SIGTERM
CMD ["node", "server.js"]