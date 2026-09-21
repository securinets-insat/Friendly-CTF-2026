FROM ubuntu:latest

RUN apt-get update && apt-get install -y socat
RUN apt-get install -y cpulimit

WORKDIR /app

RUN useradd -m ctf

COPY main main.c flag ld-linux-x86-64.so.2 libc.so.6 ./

RUN chmod +x main ld-linux-x86-64.so.2 libc.so.6

USER ctf

EXPOSE 10001

CMD socat TCP-LISTEN:10001,reuseaddr,fork EXEC:'timeout 15 ./main'
