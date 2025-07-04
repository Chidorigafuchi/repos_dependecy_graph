FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    rpm \
    ca-certificates \
    curl \
    libglib2.0-0 \
    openssl \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /etc/pki/tls/certs && \
    curl -o /etc/pki/tls/certs/ca-bundle.crt https://curl.se/ca/cacert.pem

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV REQUESTS_CA_BUNDLE=/etc/pki/tls/certs/ca-bundle.crt
ENV SSL_CERT_FILE=/etc/pki/tls/certs/ca-bundle.crt

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]