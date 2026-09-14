FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt  .

RUN pip install -r requirements.txt

COPY . .

RUN groupadd -r ctf && useradd -r ctfuser -g ctf -d /app -s /sbin/nologin

RUN chmod +x /app/entrypoint.sh && chown -R ctfuser:ctf /app

USER ctfuser

EXPOSE 5000

ENTRYPOINT [ "/app/entrypoint.sh" ]