FROM python:3.10-slim

ARG R_VERSION=4.2.3

ENV PYTHONUNBUFFERED=1 \
    APP_HOME=/app

WORKDIR $APP_HOME

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    software-properties-common \
    # Dépendances pour R et certains packages
    build-essential \
    libcurl4-openssl-dev \
    libssl-dev \
    libxml2-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*


RUN curl -fsSL https://cloud.r-project.org/bin/linux/debian/marutter_pubkey.asc | apt-key add -
RUN echo "deb https://cloud.r-project.org/bin/linux/debian bullseye-cran40/" >> /etc/apt/sources.list
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    r-base=${R_VERSION}* \
    r-base-dev=${R_VERSION}* \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN R -e "install.packages(c('gsDesign', 'jsonlite'), repos='https://cloud.r-project.org/')"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
