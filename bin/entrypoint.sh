#!/bin/bash

if [ "$DEV_MODE" = "true" ]; then
    echo "Running in development mode"
    uvicorn main:app --host 0.0.0.0 --port 5000 --reload
else
    echo "Running in production mode"
    uvicorn main:app --host 0.0.0.0 --port 5000
fi