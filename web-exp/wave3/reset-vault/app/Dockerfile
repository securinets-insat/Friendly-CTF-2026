FROM node:24-alpine

RUN apk update && apk upgrade --no-cache

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --omit=dev

COPY server.js ./
COPY lib ./lib
COPY routes ./routes
COPY public ./public

USER node

EXPOSE 3000
CMD ["node", "server.js"]
