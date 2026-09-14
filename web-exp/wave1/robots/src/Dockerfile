FROM node:latest

WORKDIR /app

COPY package*.json ./ 

RUN npm install


RUN groupadd -r ctf && useradd -r ctfuser -g ctf -d /app -s /sbin/nologin
COPY --chown=root:root . .

USER ctfuser

EXPOSE 3000

CMD ["node", "server.js"]