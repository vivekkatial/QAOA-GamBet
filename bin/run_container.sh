#!bin/bash

# Run the container and mount the current directory to /app and attach the .env file and expose 5000
# Also run it in detached mode
docker run -v $(pwd):/app --env-file .env -p 5000:5000 -d qaoakit-app
