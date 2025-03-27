# 1. Base Python
FROM python:3.10-slim

# 2. Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    APP_HOME=/app

WORKDIR $APP_HOME

# 3. Installation Dépendances Système + Ajout Repo CRAN + Installation R
RUN apt-get update && \
    # Installation des dépendances système nécessaires pour https, gestion clés, compilation et R
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
    # Ajout de la clé GPG du dépôt CRAN (méthode actuelle)
    wget -qO- https://cloud.r-project.org/bin/linux/debian/marutter_pubkey.asc | gpg --dearmor > /usr/share/keyrings/cran.gpg && \
    # Ajout du dépôt CRAN à sources.list.d en utilisant la version détectée
    # Utilise sh -c pour permettre l'évaluation de $(lsb_release -cs)
    sh -c 'echo "deb [signed-by=/usr/share/keyrings/cran.gpg] https://cloud.r-project.org/bin/linux/debian $(lsb_release -cs)-cran40/" > /etc/apt/sources.list.d/cran.list' && \
    # Mise à jour de la liste des paquets après ajout du nouveau dépôt
    apt-get update && \
    # Installation de R base et des outils de développement
    apt-get install -y --no-install-recommends \
    r-base \
    r-base-dev \
    # Nettoyage pour réduire la taille de l'image
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
