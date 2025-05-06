FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install -y \
    openjdk-17-jdk \
    git zip unzip \
    build-essential \
    python3-pip \
    libffi-dev libssl-dev \
    libsqlite3-dev zlib1g-dev \
    libbz2-dev libreadline-dev \
    libgdbm-dev liblzma-dev \
    libncurses5 libncurses5-dev \
    ffmpeg libjpeg-dev libfreetype6-dev \
    cmake \
    autoconf automake libtool \
    && apt clean

# Instalar Cython y Buildozer
RUN pip install --no-cache-dir cython buildozer

WORKDIR /app
CMD ["/bin/bash"]
