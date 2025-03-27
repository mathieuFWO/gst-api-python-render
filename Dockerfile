# 1. Base Python
FROM python:3.10-slim

# 2. Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    APP_HOME=/app

WORKDIR $APP_HOME

# 3. Installation Dépendances Système + Ajout Repo CRAN + Installation R (UNE SEULE INSTRUCTION RUN)
RUN apt-get update && \
    # Installer les dépendances initiales pour HTTPS, clés, compilation, R
    apt-get install -y --no-install-recommends \
        gnupg \
        ca-certificates \
        wget \
        build-essential \
        libcurl4-openssl-dev \
        libssl-dev \
        libxml2-dev \
        lsb-release && \
    # Ajouter la clé GPG CRAN
    wget -qO- https://cloud.r-project.org/bin/linux/debian/marutter_pubkey.asc | gpg --dearmor > /usr/share/keyrings/cran.gpg && \
    # Ajouter le dépôt CRAN (utilisation de sh -c pour évaluation de lsb_release)
    sh -c 'echo "deb [signed-by=/usr/share/keyrings/cran.gpg] https://cloud.r-project.org/bin/linux/debian $(lsb_release -cs)-cran40/" > /etc/apt/sources.list.d/cran.list' && \
    # Mettre à jour les listes de paquets *après* ajout du dépôt
    apt-get update && \
    # Installer R base et dev
    apt-get install -y --no-install-recommends \
        r-base \
        r-base-dev && \
    # Nettoyer pour réduire la taille
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
