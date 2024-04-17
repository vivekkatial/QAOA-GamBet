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

RUN pip install --no-cache-dir -e .

# Build QAOAKit Tables
RUN python -m QAOAKit.build_tables

# Make port 80 available
EXPOSE 80

ENV NAME QAOAKit

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]
