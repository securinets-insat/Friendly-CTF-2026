FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

RUN useradd --no-create-home --shell /usr/sbin/nologin ctf

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY Bankai.py .
RUN chmod 444 Bankai.py

USER ctf
EXPOSE 31337

CMD ["python3", "Bankai.py"]
