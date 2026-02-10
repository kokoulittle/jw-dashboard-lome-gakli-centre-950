# 1️⃣ Image Python officielle
FROM python:3.11-slim

# 2️⃣ Variables d’environnement recommandées
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8050

# 3️⃣ Dossier de travail
WORKDIR /app

# 4️⃣ Dépendances système nécessaires à Plotly/Kaleido
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

# 5️⃣ Dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6️⃣ Copier le code et les ressources
COPY dashboard.py .
COPY assets/ ./assets/
COPY data/ ./data/

# 7️⃣ Dossier d’export PDF (persistant + permissions)
RUN mkdir -p /app/exports/pdf \
    && chmod -R 777 /app/exports

# 8️⃣ Port Dash (Railway lira $PORT)
EXPOSE 8050

# 9️⃣ Lancer l’application avec un serveur production
CMD gunicorn dashboard:server \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --timeout 120
