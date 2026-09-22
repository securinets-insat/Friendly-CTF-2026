FROM ubuntu:latest

WORKDIR /app

RUN useradd -m ctf

COPY main main.c flag.txt ./

RUN chmod +x main

USER ctf

EXPOSE 5000

CMD ["./main"]
