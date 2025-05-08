FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY check_socket_krx.py .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "check_socket_krx.py"]
