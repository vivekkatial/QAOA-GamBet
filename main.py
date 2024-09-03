from fastapi import FastAPI
from routes import qaoakit, qibpi, random, tqa, constant
from fastapi.responses import HTMLResponse
from fastapi.openapi.utils import get_openapi



app = FastAPI(title="QAOA Forge", description="API for the QAOAKit library.")

# Include the routers
app.include_router(random.router)
app.include_router(qibpi.router)
app.include_router(qaoakit.router)
app.include_router(tqa.router)
app.include_router(constant.router)
# include the routers for `fixed_angles`, `interp`, `fourier`
