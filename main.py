import uvicorn
from fastapi import FastAPI
from routes import qaoakit, qibpi, random

app = FastAPI(title="QAOA Forge", description="API for the QAOAKit library.")

# Include the routers
app.include_router(random.router)
app.include_router(qaoakit.router)
app.include_router(qibpi.router)