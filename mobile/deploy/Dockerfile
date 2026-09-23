# Mobile-track backend: app.py (:8000 HTTP, :8443 HTTPS) and
# rogue_sdk_collector.py (:9090). One image, one container, all three
# processes.
#
# Flags are NEVER baked in. flags.json is gitignored and bind-mounted
# read-only at runtime (see docker-compose.yml and DEPLOY.md); CTF_FLAGS
# points app.py and rogue_sdk_collector.py at it.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

RUN useradd --system --no-create-home --shell /usr/sbin/nologin backend

WORKDIR /srv/backend

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py rogue_sdk_collector.py debriefs.json docker-entrypoint.sh ./
COPY --chown=backend:backend certs/ ./certs/

RUN chmod +x docker-entrypoint.sh

USER backend

EXPOSE 8000 8443 9090

ENTRYPOINT ["./docker-entrypoint.sh"]
