FROM python:3.12-slim-bookworm

RUN apt-get update \
    && apt-get install -y --no-install-recommends socat \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /usr/sbin/nologin ctf

WORKDIR /app

COPY chall.py flag.txt ./
COPY attachments ./attachments

RUN chmod 0555 chall.py \
    && chmod 0444 flag.txt attachments/detector.py \
        attachments/detector_weights.json attachments/Submission.java

USER ctf

EXPOSE 10001

CMD ["socat", "TCP-LISTEN:10001,reuseaddr,fork", "EXEC:timeout 45 python3 -u /app/chall.py,stderr"]
