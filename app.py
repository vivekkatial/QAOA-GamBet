import uvicorn
from fastapi import FastAPI, HTTPException, Body, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field
import networkx as nx
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

app = FastAPI(title="QAOAKit API", description="API for the QAOAKit library.",)
security = HTTPBasic()


from QAOAKit import opt_angles_for_graph, angles_to_qaoa_format

class GraphDTO(BaseModel):
    """
    Data Transfer Object (DTO) for graph input.
    Attributes:
        instance_id (int): Unique identifier for the graph instance.
        adjacency_matrix (list): Adjacency matrix of the graph as a list of lists.
    """
    instance_id: int
    adjacency_matrix: list

class OptimalAnglesDTO(BaseModel):
    """
    DTO for specifying the graph's adjacency matrix and the number of QAOA layers.
    """
    adjacency_matrix: list = Field(..., example=[[0, 1], [1, 0]], 
                                   description="Adjacency matrix as a list of lists, each inner list represents a node connection.")
    p: int = Field(..., example=1, description="Number of QAOA layers for the calculation.")

def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
    username = os.getenv('QAOAKIT_AUTH_USERNAME')
    password = os.getenv('QAOAKIT_AUTH_PASSWORD')
    if credentials.username != username or credentials.password != password:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return credentials.username

@app.post("/graph/optimal_angles", response_model=dict, tags=["QAOAKit"],
          summary="Get Optimal Angles", 
          response_description="The optimal beta and gamma angles for the QAOA algorithm.",
          responses={
              200: {"description": "Successfully calculated and returned the optimal angles.",
                    "content": {"application/json": {"example": {"beta": [0.1], "gamma": [0.2], "optimal_angles": False, "source": "QAOAKit"}}}},
              400: {"description": "Invalid input data."},
              500: {"description": "Server error during angle calculation."}
          },
          dependencies=[Depends(authenticate_user)])
def get_optimal_angles(optimal_angles_dto: OptimalAnglesDTO = Body(...)):
    """
    Endpoint to calculate the optimal QAOA angles from a given adjacency matrix and QAOA layers.
    """
    try:
        adjacency_matrix = np.array(optimal_angles_dto.adjacency_matrix)
        G = nx.from_numpy_array(adjacency_matrix)
        angles = opt_angles_for_graph(G, p=optimal_angles_dto.p)
        qaoa_angles = angles_to_qaoa_format(angles)
        qaoa_angles['beta'] = qaoa_angles['beta'].tolist()
        qaoa_angles['gamma'] = qaoa_angles['gamma'].tolist()
        return qaoa_angles
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
