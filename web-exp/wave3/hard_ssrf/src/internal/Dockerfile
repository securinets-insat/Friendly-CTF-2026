FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install flask uwsgi

WORKDIR /test
COPY . ./

EXPOSE 3001

CMD ["uwsgi", "--http", ":3001", "--wsgi-file", "app.py", "--callable", "app"]
