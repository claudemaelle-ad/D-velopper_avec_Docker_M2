# Image de base : Node.js 20 en variante Alpine
# Choix : la plus légère (environ 190 Mo), moins de failles de sécurité
FROM node:20-alpine

# Métadonnées de l'image
LABEL description="Front du projet Citation du jour - Node.js"

# Dossier de travail dans le conteneur
WORKDIR /app

# Donne le dossier à l'utilisateur "node" (fourni par l'image)
# Doit être fait avant USER, car seul root peut changer le propriétaire
RUN chown -R node:node /app

# Sécurité : la suite s'exécute avec un utilisateur sans droits admin
USER node

# Copie des fichiers de dépendances seuls, avant le code
COPY --chown=node:node package*.json ./

RUN npm ci

# Copie du code (server.js, index.html), sauf ce qui est dans .dockerignore
COPY --chown=node:node . .

ENV NODE_ENV=production \
    PORT=3000

EXPOSE 3000

# Vérifie toutes les 30 s que l'application répond sur /health
# Le conteneur est marqué "unhealthy" après 3 échecs
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:' + (process.env.PORT || 3000) + '/health', (r) => process.exit(r.statusCode === 200 ? 0 : 1)).on('error', () => process.exit(1))"
  
CMD ["node", "server.js"]