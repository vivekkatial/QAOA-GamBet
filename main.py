from fastapi import FastAPI
from routes import qaoakit, qibpi, random, tqa, constant, interp
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi
from fastapi.responses import FileResponse
import logging
import os

app = FastAPI(
    title="QAOA GamBet API",
    description="This API provides various methods for generating QAOA (Quantum Approximate Optimization Algorithm) angles. For more information, please refer to our paper."
)

# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")


# Include the routers
app.include_router(random.router)
app.include_router(qibpi.router)
app.include_router(qaoakit.router)
app.include_router(tqa.router)
app.include_router(constant.router)
app.include_router(interp.router)

# TODO: If you want to add more routers, add them here.
# e.g. app.include_router(interp.router)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="QAOA Angle Generator API",
        version="1.0.0",
        description="This API provides various methods for generating QAOA (Quantum Approximate Optimization Algorithm) angles.",
        routes=app.routes,
    )

    # Add logo to the OpenAPI schema
    openapi_schema["info"]["x-logo"] = {
        "url": "/static/logo.png",
        "altText": "QAOA Angle Generator API Logo"
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Custom ReDoc route
@app.get("/redoc", include_in_schema=False)
async def custom_redoc():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>QAOA Angle Generator API</title>
        <!-- Favicon -->
        <link rel="icon" type="image/png" href="/static/favicon.png">
        <!-- needed for adaptive design -->
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
        <!-- ReDoc doesn't change outer page styles -->
        <style>
            body {
                margin: 0;
                padding: 0;
            }
            .logo {
                padding: 20px;
                max-width: 200px;
                margin: 0 auto;
                display: block;
            }
        </style>
    </head>
    <body>
        <img src="/static/logo.png" alt="QAOA Angle Generator API Logo" class="logo">
        <redoc spec-url="/openapi.json"></redoc>
        <script src="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"></script>
    </body>
    </html>
    """)

@app.get("/", include_in_schema=False)
async def read_root():
    logging.debug("Attempting to serve index.html")
    file_path = 'static/index.html'
    if os.path.exists(file_path):
        logging.debug(f"File found at {file_path}")
        return FileResponse(file_path)
    else:
        logging.error(f"File not found at {file_path}")
        return {"detail": "Index file not found"}
