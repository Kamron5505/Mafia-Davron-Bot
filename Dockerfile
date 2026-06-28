FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies (all packages have pre-built wheels on amd64)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run the bot
CMD ["python", "bot.py"]
