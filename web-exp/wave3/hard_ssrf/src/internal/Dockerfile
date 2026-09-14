FROM python:3.12-slim

RUN pip install flask uwsgi

WORKDIR /test
COPY . ./

EXPOSE 3001

CMD ["uwsgi", "--http", ":3001", "--wsgi-file", "app.py", "--callable", "app"]
