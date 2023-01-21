FROM python:3.11.1-slim
MAINTAINER advillalba


HEALTHCHECK --interval=5m --timeout=3s CMD curl --silent -o /dev/null https://www.google.es || exit 1

RUN  mkdir -p /app/shared &&  apt-get update && apt-get install curl -y

VOLUME /app/shared
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt  --no-warn-script-location

COPY web_scraper web_scraper
COPY app.py .



CMD ["python", "./app.py"]
