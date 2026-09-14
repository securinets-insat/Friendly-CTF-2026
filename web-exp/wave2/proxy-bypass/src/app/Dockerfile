FROM python:3.12-slim

WORKDIR /app

RUN pip install flask


RUN groupadd -r ctf && useradd -r ctfuser -g ctf -d /app -s /sbin/nologin
COPY --chown=root:root . .

RUN chown -R root:ctf /app \
    && find /app -type d -exec chmod 750 {} \; \
    && find /app -type f -exec chmod 640 {} \; 

USER ctfuser

CMD ["python", "app.py"]


