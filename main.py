from fastapi import FastAPI
from routes import qaoakit, qibpi, random, tqa 
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse


app = FastAPI(title="QAOA Forge", description="API for the QAOAKit library.")

# Include the routers
app.include_router(random.router)
app.include_router(qibpi.router)
app.include_router(qaoakit.router)
app.include_router(tqa.router)
# include the routers for `fixed_angles`, `interp`, `fourier`



app.mount("/static", StaticFiles(directory="static"), name="static")