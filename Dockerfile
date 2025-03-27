# 1. Base Python
FROM python:3.10-slim

# 2. Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    APP_HOME=/app

WORKDIR $APP_HOME

# 3. Installation Dépendances Système + R
#    Utilisation de && et rm pour garder l'image petite
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    r-base \
    r-base-dev \
    build-essential \
    libcurl4-openssl-dev \
    libssl-dev \
    libxml2-dev \
    # Nettoyage
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 4. Installation Packages R
RUN R -e "options(Ncpus = parallel::detectCores()); install.packages(c('gsDesign', 'jsonlite'), repos='https://cloud.r-project.org/')"

# 5. Installation Dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copie du Code Applicatif
COPY . .

# 7. Exposition du Port (sera remplacé par $PORT de Render)
EXPOSE 8080

# 8. Commande de Démarrage (Utilisation de $PORT fourni par Render)
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "app:app"]
```