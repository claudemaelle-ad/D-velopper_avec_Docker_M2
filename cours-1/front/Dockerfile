# INSTRUCTION 1: Node.js Base Image Selection
FROM node:20-alpine

# INSTRUCTION 2: Security - Non-root User
WORKDIR /app
RUN chown -R node:node /app
USER node

# INSTRUCTION 3: Dependencies Layer
COPY --chown=node:node package*.json ./

# INSTRUCTION 4: Install Dependencies
RUN npm ci

# INSTRUCTION 5: Copy Application Source Code
COPY --chown=node:node . .

# INSTRUCTION 7: Environment Variables
ENV NODE_ENV=production \
    PORT=3000

# INSTRUCTION 9: Expose Port
EXPOSE 3000

# INSTRUCTION 10: Health Check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/health', (r) => process.exit(r.statusCode === 200 ? 0 : 1)).on('error', () => process.exit(1))"

# INSTRUCTION 11: Startup Command
CMD ["node", "server.js"]
