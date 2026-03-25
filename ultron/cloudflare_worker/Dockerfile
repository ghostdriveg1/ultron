# ─── Ultron Cloudflare Worker — Dockerfile ─────────────────────
FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package.json ./
RUN npm ci --ignore-scripts

# Copy source
COPY src ./src/
COPY wrangler.toml ./

CMD ["npx", "wrangler", "dev", "--local", "--port", "8787"]
