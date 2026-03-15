FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY screener/ screener/

EXPOSE 8400

# Default: dictionary-only mode (add --model flag for MLM mode)
CMD ["python", "-m", "screener", "--host", "0.0.0.0", "--no-browser"]
