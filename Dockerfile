FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    APP_HOME=/app

WORKDIR $APP_HOME

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gnupg \
    ca-certificates \
    wget \
    build-essential \
    libcurl4-openssl-dev \
    libssl-dev \
    libxml2-dev \
    lsb-release \ # Pour détecter la version de Debian (ex: bullseye)
    && \
    wget -qO- https://cloud.r-project.org/bin/linux/debian/marutter_pubkey.asc | gpg --dearmor > /usr/share/keyrings/cran.gpg && \
    sh -c 'echo "deb [signed-by=/usr/share/keyrings/cran.gpg] https://cloud.r-project.org/bin/linux/debian $(lsb_release -cs)-cran40/" > /etc/apt/sources.list.d/cran.list' && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    r-base \
    r-base-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN R -e "options(Ncpus = parallel::detectCores()); install.packages(c('gsDesign', 'jsonlite'), repos='https://cloud.r-project.org/')"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "app:app"]
