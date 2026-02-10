# 1️ Image Python officielle 
FROM python:3.11-slim 

# 2️ Variables d’environnement recommandées 
ENV PYTHONDONTWRITEBYTECODE=1 
ENV PYTHONUNBUFFERED=1 
# 3️ Dossier de travail 
WORKDIR /app 
# 4️ Dépendances système nécessaires à Plotly/Kaleido 
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
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

# Install Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor > /usr/share/keyrings/chrome.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" \
    > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# 5️ Dépendances Python 
COPY requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt 

# 6️ Copier le code et les ressources 
COPY dashboard.py . 
COPY assets/ ./assets/ 
COPY data/ ./data/ 

# 7️ Dossier d’export PDF 
RUN mkdir -p exports/pdf 

# 8️ Port Dash 
EXPOSE 8050 

# 9️ Lancer l’application 
CMD ["python", "dashboard.py"]
