# Base image with Python
FROM python:3.11

# Install Node.js and npm
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_16.x | bash - && \
    apt-get install -y nodejs

# Set working directory
WORKDIR /app

# Copy local project files into container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Firebase Admin SDK for Python
RUN pip install firebase-admin

# Set entry point
CMD ["python", "app.py"]
