FROM python:3.12-slim

# The flag contains a non-ASCII character, force UTF-8 on stdin/stdout.
ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

RUN apt-get update \
    && apt-get install -y --no-install-recommends socat \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --no-create-home --shell /usr/sbin/nologin ctf

WORKDIR /app
# The real chall.py (with the flag), NOT the handout one.
COPY chall.py .
RUN chmod 444 chall.py

USER ctf
EXPOSE 1337

# One process per connection, killed after 120s.
CMD ["socat", "-T120", "TCP-LISTEN:1337,reuseaddr,fork", "EXEC:'timeout 120 python3 -u chall.py'"]
