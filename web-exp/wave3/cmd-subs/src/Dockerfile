FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends iputils-ping \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt  .

RUN pip install -r requirements.txt


RUN groupadd -r ctf && useradd -r ctfuser -g ctf -d /app -s /sbin/nologin
COPY --chown=root:root . .

RUN chown -R root:ctf /app \
    && find /app -type d -exec chmod 750 {} \; \
    && find /app -type f -exec chmod 640 {} \; 

USER ctfuser

EXPOSE 5013

CMD ["gunicorn", "--bind", "0.0.0.0:5013", "--control-socket", "/tmp/gunicorn.ctl", "app:app"]