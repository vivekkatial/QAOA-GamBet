FROM python:3.12.2-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    libffi-dev \
    libssl-dev \
    libblas-dev \
    liblapack-dev \
    libopenblas-dev \
    pkg-config \
    libsuitesparse-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Check if umfpack.h is present
RUN find /usr -name "umfpack.h"

# Set environment variables
ENV LD_LIBRARY_PATH=/usr/lib:/usr/local/lib
ENV C_INCLUDE_PATH=/usr/include:/usr/local/include
ENV CPPFLAGS="-I/usr/include/suitesparse"

COPY . /app

RUN pip install .

# Install development dependencies
RUN pip install uvicorn[standard] watchfiles

# Build QAOAKit Tables for that package dependncies
RUN python -m QAOAKit.build_tables

# Copy trained models into the app folders
COPY ./kde_n=9_p=1_large_bandwidth_range.p /app/data/pretrained_models/kde_n=9_p=1_large_bandwidth_range.p
COPY ./optimal-parameters.csv /app/data/optimal-parameters.csv

# Make port 5000 available
EXPOSE 5000

# Create and use an entrypoint script
COPY bin/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]