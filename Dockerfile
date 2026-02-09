# 1️⃣ Image Python officielle (légère et stable)
FROM python:3.11-slim

# 2️⃣ Dossier de travail dans le conteneur
WORKDIR /app

# 3️⃣ Dépendances système nécessaires pour Plotly/Kaleido (export PDF)
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libnss3 \
    libxss1 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxcomposite1 \
    libxrandr2 \
    libgbm1 \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libgtk-3-0 \
    libdrm2 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 📚 Source officielle Plotly – dépendances Kaleido
# https://plotly.com/python/static-image-export/

# 4️⃣ Copier les dépendances Python
COPY requirements.txt .

# 5️⃣ Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# 6️⃣ Copier le code et les assets
COPY dashboard.py .
COPY JW_Logo.png .
COPY Random_Attendant_Crew_Schedule.csv .

# 7️⃣ Créer le dossier d’export PDF
RUN mkdir -p "PDF EXPORTS"

# 8️⃣ Exposer le port Dash
EXPOSE 8050

# 9️⃣ Lancer l’application
CMD ["python", "dashboard.py"]
