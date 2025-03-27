# 1. Base Python
FROM python:3.10-slim

# 2. Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    APP_HOME=/app

WORKDIR $APP_HOME

# 3. Installation Dépendances Système + Ajout Repo CRAN + Installation R (Méthode apt-key contrôlée)
RUN apt-get update && \
    # Dépendances
    apt-get install -y --no-install-recommends \
        gnupg \
        ca-certificates \
        wget \
        build-essential \
        libcurl4-openssl-dev \
        libssl-dev \
        libxml2-dev \
        lsb-release && \
    # Ajouter la clé GPG en utilisant apt-key mais en dirigeant vers le bon keyring
    wget -qO- https://cloud.r-project.org/bin/linux/debian/marutter_pubkey.asc | apt-key --keyring /usr/share/keyrings/cran-archive-keyring.gpg add - && \
    # Ajouter le dépôt CRAN en référençant le keyring spécifique
    sh -c 'echo "deb [signed-by=/usr/share/keyrings/cran-archive-keyring.gpg] https://cloud.r-project.org/bin/linux/debian $(lsb_release -cs)-cran40/" > /etc/apt/sources.list.d/cran.list' && \
    # Update et Install R
    apt-get update && \
    apt-get install -y --no-install-recommends \
        r-base \
        r-base-dev && \
    # Nettoyage
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

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
