# Utilise une image Python officielle
FROM python:3.10-slim

# Définit le dossier de travail
WORKDIR /app

# Copie les fichiers du projet
COPY . .

# Installe les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Expose le port 8000
EXPOSE 8000

# Commande pour démarrer Flask
CMD ["python", "app.py"]
