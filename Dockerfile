FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
# Collect static files with error handling
RUN python -c "import os; os.makedirs('staticfiles', exist_ok=True)" && \
    python manage.py collectstatic --noinput || echo "Static collection failed, continuing anyway"
    

# Run gunicorn
CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000"]
