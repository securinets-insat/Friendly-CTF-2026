FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt  .

RUN pip install -r requirements.txt


RUN groupadd -r ctf && useradd -r ctfuser -g ctf -d /app -s /sbin/nologin
COPY --chown=root:root . .

RUN chmod +x /app/entrypoint.sh \
    && chown -R root:ctf /app \
    && find /app -type d -exec chmod 750 {} \; \
    && find /app -type f -exec chmod 640 {} \; \
    && chmod +x /app/entrypoint.sh \
    && mkdir -p /app/data \
    && chown ctfuser:ctf /app/data \
    && chmod 770 /app/data

USER ctfuser

EXPOSE 5005

ENTRYPOINT [ "/app/entrypoint.sh" ]