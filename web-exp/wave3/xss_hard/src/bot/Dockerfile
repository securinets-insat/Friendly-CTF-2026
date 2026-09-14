FROM node:22-slim

RUN apt-get update && apt-get install -y \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libxshmfence1 \
    libxfixes3 \
    libx11-6 \
    libxrender1 \
    libxi6 \
    libxtst6 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /bot

COPY package.json . 
RUN npm install

RUN npx playwright install chromium

COPY bot.js .

CMD ["node", "bot.js"]