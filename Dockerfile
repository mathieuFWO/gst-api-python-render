# 1. Base Python
FROM python:3.10-slim

# 2. Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    APP_HOME=/app

WORKDIR $APP_HOME

# 3. Installation Dépendances Système + Ajout Repo CRAN + Installation R (UNE SEULE INSTRUCTION RUN, ETAPES GPG SEPAREES)
RUN apt-get update && \
    # Installer les dépendances initiales
    apt-get install -y --no-install-recommends \
        gnupg \
        ca-certificates \
        wget \
        build-essential \
        libcurl4-openssl-dev \
        libssl-dev \
        libxml2-dev \
        lsb-release && \
    # Étape 1: Télécharger la clé GPG CRAN dans un fichier temporaire
    wget -qO /tmp/cran-key.asc https://cloud.r-project.org/bin/linux/debian/marutter_pubkey.asc && \
    # Étape 2: Vérifier si le fichier de clé existe et n'est pas vide avant de continuer
    test -s /tmp/cran-key.asc && \
    # Étape 3: Importer la clé depuis le fichier en utilisant gpg --dearmor
    gpg --dearmor < /tmp/cran-key.asc > /usr/share/keyrings/cran.gpg && \
    # Étape 4: Nettoyer le fichier temporaire
    rm /tmp/cran-key.asc && \
    # Étape 5: Ajouter le dépôt CRAN en référençant la clé importée
    sh -c 'echo "deb [signed-by=/usr/share/keyrings/cran.gpg] https://cloud.r-project.org/bin/linux/debian $(lsb_release -cs)-cran40/" > /etc/apt/sources.list.d/cran.list' && \
    # Étape 6: Mettre à jour la liste des paquets après ajout du dépôt
    apt-get update && \
    # Étape 7: Installer R base et dev
    apt-get install -y --no-install-recommends \
        r-base \
        r-base-dev && \
    # Étape 8: Nettoyage final
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
