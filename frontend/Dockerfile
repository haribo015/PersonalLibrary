FROM node:20-bookworm-slim

WORKDIR /usr/src/app

COPY package.json package-lock.json* ./
RUN npm install --legacy-peer-deps --no-audit --no-fund

COPY . .
RUN chown -R node:node /usr/src/app

USER node

EXPOSE 4200
