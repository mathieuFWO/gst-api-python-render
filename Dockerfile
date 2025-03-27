# 1. Base Python
FROM python:3.10-slim

# 2. Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    APP_HOME=/app

WORKDIR $APP_HOME

# 3. Installation Dépendances Système + Installation R depuis les dépôts Debian standards
RUN apt-get update && \
    # Installer les dépendances pour R, la compilation, et V8
    apt-get install -y --no-install-recommends \
        build-essential \
        libcurl4-openssl-dev \
        libssl-dev \
        libxml2-dev \
        libv8-dev \
        r-base \
        r-base-dev && \
    # Nettoyage
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 4. Installation Packages R
#    Augmenter le timeout car l'installation de V8/dépendances peut être longue
RUN R -e "options(Ncpus = parallel::detectCores(), timeout = 600); install.packages(c('gsDesign', 'jsonlite'), repos='https://cloud.r-project.org/')"

# 5. Installation Dépendances Python
#    Assurez-vous que requirements.txt a un package par ligne
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copie du Code Applicatif
COPY . .

# 7. Exposition du Port (sera remplacé par $PORT de Render)
EXPOSE 8080

# 8. Commande de Démarrage (Utilisation de $PORT fourni par Render)
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "app:app"]
