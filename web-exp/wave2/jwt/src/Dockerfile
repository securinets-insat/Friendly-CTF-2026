FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt  .

RUN pip install -r requirements.txt


RUN groupadd -r ctf && useradd -r ctfuser -g ctf -d /app -s /sbin/nologin
COPY --chown=root:root . .

RUN chown -R root:ctf /app \
    && find /app -type d -exec chmod 750 {} \; \
    && find /app -type f -exec chmod 640 {} \; \
    && mkdir -p /app/data \
    && chown ctfuser:ctf /app/data \
    && chmod 770 /app/data

USER ctfuser

EXPOSE 5011

CMD ["gunicorn", "--bind", "0.0.0.0:5011", "--control-socket", "/tmp/gunicorn.ctl", "app:app"]