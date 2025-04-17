FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    zip \
    unzip \
    openjdk-17-jdk \
    libncurses5 \
    libstdc++6 \
    libffi-dev \
    libssl-dev \
    libz-dev \
    libjpeg-dev \
    libfreetype6-dev \
    libgl1-mesa-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    python3-dev \
    && apt-get clean

# Set Java environment
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="$JAVA_HOME/bin:$PATH"

# Install buildozer
RUN pip install --upgrade pip setuptools cython virtualenv
RUN pip install buildozer

# Add non-root user for safer builds
RUN useradd -ms /bin/bash builduser
USER builduser

# Work directory will be bound via docker-compose volume
WORKDIR /home/builduser/app

# Default entrypoint can be overridden
CMD ["buildozer", "--help"]
