FROM node:latest

WORKDIR /app

COPY package*.json ./ 

RUN npm install


RUN groupadd -r ctf && useradd -r ctfuser -g ctf -d /app -s /sbin/nologin
COPY --chown=root:root . .

RUN mv flag.txt /flag.txt \
    && chown root:ctf /flag.txt \
    && chmod 440 /flag.txt

RUN mkdir -p /app/data \
    && chown ctfuser:ctf /app/data \
    && chmod 770 /app/data

USER ctfuser

EXPOSE 5008

CMD ["node", "app.js"]