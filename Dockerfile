# Utiliser une image Python officielle comme base
FROM python:3.9

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier les fichiers nécessaires dans le conteneur
COPY ./requirements.txt /app/requirements.txt
COPY certs/cert.pem /etc/ssl/cert.pem

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code de l'application dans le conteneur
COPY . /app

# Exposer le port sur lequel l'API s'exécute
EXPOSE 8000

# Définir la commande pour démarrer l'application
CMD ["uvicorn", "main:api", "--host", "0.0.0.0", "--port", "8000"]
