FROM debian:12-slim

# Instal·la eines bàsiques i afegeix el repositori de Google Chrome
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update

# Instal·la dependències i Google Chrome
RUN apt-get install -y \
    python3 \
    python3-pip \
    curl \
    unzip \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    google-chrome-stable

# Instal·la Chromedriver
RUN CHROMEDRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE) \
    && wget -q https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip -d /usr/local/bin/ \
    && rm chromedriver_linux64.zip \
    && chmod +x /usr/local/bin/chromedriver

# Configura el directori de treball
WORKDIR /app

# Copia els fitxers
COPY mundoparquet-bot/requirements.txt .
COPY mundoparquet-bot/scraper.py .

# Verifica que els fitxers s'han copiat
RUN ls -la /app

# Instal·la les dependències de Python
RUN pip install --no-cache-dir -r requirements.txt

# Comanda per defecte
CMD ["python", "scraper.py"]
