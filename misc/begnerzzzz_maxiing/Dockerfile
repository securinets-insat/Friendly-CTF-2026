FROM ubuntu:26.04

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        openjdk-21-jdk-headless python3 socat \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /usr/sbin/nologin ctf

WORKDIR /app

COPY chall.py detector.py detector_weights.json Main.java flag.txt ./

RUN javac --add-exports java.base/jdk.internal.reflect=ALL-UNNAMED Main.java \
    && chmod 0555 chall.py \
    && chmod 0444 detector.py detector_weights.json Main.java Main.class Main\$*.class \
    && chown root:root flag.txt \
    && chmod 0400 flag.txt

EXPOSE 10001

CMD ["socat", "TCP-LISTEN:10001,reuseaddr,fork", "EXEC:timeout 32 python3 -u /app/chall.py,stderr"]
