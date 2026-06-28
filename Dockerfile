FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create volume for database persistence
VOLUME ["/app/data"]

# Run the bot
CMD ["python", "bot.py"]
