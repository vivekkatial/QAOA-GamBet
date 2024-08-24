from fastapi import HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from config import BASIC_AUTH_USERNAME, BASIC_AUTH_PASSWORD

security = HTTPBasic()

async def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != BASIC_AUTH_USERNAME or credentials.password != BASIC_AUTH_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return credentials.username