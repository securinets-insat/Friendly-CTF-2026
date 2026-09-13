FROM ubuntu:latest

RUN apt-get update && apt-get install -y python3 socat cpulimit

WORKDIR /app

RUN useradd -m ctf

COPY chall.py flag.txt ./

RUN chmod +x chall.py

USER ctf

EXPOSE 10001

CMD socat TCP-LISTEN:10001,reuseaddr,fork EXEC:'timeout 30 python3 -u ./chall.py'
