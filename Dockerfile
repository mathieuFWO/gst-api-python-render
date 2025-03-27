# 1. Choisir une image de base Python
FROM python:3.10-slim # Ou une version appropriée

# Arguments pour version R, etc. (optionnel)
ARG R_VERSION=4.2.3

# Variables d'environnement (utile pour les chemins)
ENV PYTHONUNBUFFERED=1 \
    APP_HOME=/app

WORKDIR $APP_HOME

# 2. Installer les dépendances système (dont R)
#    Exemple pour Debian/Ubuntu based images (comme python:*-slim)
#    Ceci peut être long et nécessiter des ajustements
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

# Installation de R (Exemple, peut varier)
# Ajouter le repo CRAN
RUN curl -fsSL https://cloud.r-project.org/bin/linux/debian/marutter_pubkey.asc | apt-key add -
RUN echo "deb https://cloud.r-project.org/bin/linux/debian bullseye-cran40/" >> /etc/apt/sources.list
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    r-base=${R_VERSION}* \
    r-base-dev=${R_VERSION}* \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 3. Installer les packages R nécessaires
RUN R -e "install.packages(c('gsDesign', 'jsonlite'), repos='https://cloud.r-project.org/')"

# 4. Installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copier le code de l'application
COPY . .

# 6. Exposer le port (doit correspondre à ce que Gunicorn écoutera)
EXPOSE 8080

# 7. Commande de démarrage (Utiliser Gunicorn pour la production)
#    'app:app' -> nom_fichier:nom_variable_flask
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
