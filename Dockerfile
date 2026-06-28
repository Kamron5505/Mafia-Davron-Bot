FROM python:3.11-slim

WORKDIR /app

# Install build dependencies for aiohttp/aiogram compilation, then clean up
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc build-essential && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run the bot
CMD ["python", "bot.py"]
