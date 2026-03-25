# ─── Ultron Website — Dockerfile ───────────────────────────────
FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package.json ./
RUN npm ci --ignore-scripts

# Copy all source
COPY . ./

CMD ["npm", "run", "dev", "--", "--host"]
