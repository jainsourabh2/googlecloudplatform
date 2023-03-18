# syntax=docker/dockerfile:1

FROM node:12.18.1

ENV NODE_ENV=production

ENV PORT 3000
EXPOSE 3000

WORKDIR /app

COPY package*.json ./
COPY index.js ./

RUN npm install

COPY . ./

CMD [ "node", "app.js" ]
