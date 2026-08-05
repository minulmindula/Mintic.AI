# Multi-stage Dockerfile for Mintic.AI Next.js Frontend
FROM node:20-alpine AS deps

WORKDIR /app

# Copy root workspace and dependencies
COPY apps/web/package.json ./apps/web/
COPY packages/shared-types ./packages/shared-types/

WORKDIR /app/apps/web
RUN npm install --legacy-peer-deps

# Builder Stage
FROM node:20-alpine AS builder

WORKDIR /app

COPY --from=deps /app/apps/web/node_modules ./apps/web/node_modules
COPY packages/shared-types ./packages/shared-types
COPY apps/web ./apps/web

WORKDIR /app/apps/web

ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production

RUN npm run build

# Production Runner Stage
FROM node:20-alpine AS runner

WORKDIR /app/apps/web

ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

COPY --from=builder /app/apps/web/public ./public
COPY --from=builder /app/apps/web/.next ./.next
COPY --from=builder /app/apps/web/node_modules ./node_modules
COPY --from=builder /app/apps/web/package.json ./package.json

EXPOSE 3000

CMD ["npm", "start"]
