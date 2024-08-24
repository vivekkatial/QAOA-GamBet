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
# Build QAOAKit Tables
RUN python -m QAOAKit.build_tables

# Copy trained models into the app folders
COPY ./kde_n=9_p=1_large_bandwidth_range.p /app/data/pretrained_models/kde_n=9_p=1_large_bandwidth_range.p
COPY ./optimal-parameters.csv /app/data/optimal-parameters.csv


# Make port 80 available
EXPOSE 5000

ENV NAME QAOAKit

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]
