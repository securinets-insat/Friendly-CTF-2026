FROM ubuntu:24.04

RUN apt-get update \
    && apt-get install -y --no-install-recommends socat coreutils \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --no-create-home --shell /usr/sbin/nologin ctf

# The binary opens "flag.txt" relative to its working directory.
WORKDIR /app
COPY buvette flag.txt ./
RUN chown root:root buvette flag.txt \
    && chmod 555 buvette \
    && chmod 444 flag.txt

USER ctf
EXPOSE 1338

# stdbuf disables printf buffering so menus/prompts reach the player before scanf.
CMD ["socat", "-T300", "TCP-LISTEN:1338,reuseaddr,fork", "EXEC:'timeout 300 stdbuf -i0 -o0 -e0 ./buvette'"]
