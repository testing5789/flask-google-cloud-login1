FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create templates directory if it doesn't exist
RUN mkdir -p templates

# Create a non-root user to run the application
RUN adduser --disabled-password --gecos "" appuser
USER appuser

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
