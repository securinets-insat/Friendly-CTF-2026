FROM node:latest

WORKDIR /app

COPY package*.json ./ 

RUN npm install


RUN groupadd -r ctf && useradd -r ctfuser -g ctf -d /app -s /sbin/nologin
COPY --chown=root:root . .

USER ctfuser

EXPOSE 5007

CMD ["node", "app.js"]