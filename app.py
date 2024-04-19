import uvicorn
from fastapi import FastAPI, HTTPException, Body, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field
import networkx as nx
import numpy as np
import os
from dotenv import load_dotenv
import logging
from QAOAKit.parameter_optimization import get_median_pre_trained_kde
from QAOAKit import opt_angles_for_graph, angles_to_qaoa_format, beta_to_qaoa_format, gamma_to_qaoa_format

logging.basicConfig(level=logging.WARNING)

load_dotenv()  # Load environment variables from .env file

app = FastAPI(title="QAOAKit", description="API for the QAOAKit library.",)
security = HTTPBasic()

from QAOAKit import opt_angles_for_graph, angles_to_qaoa_format

class GraphDTO(BaseModel):
    instance_id: int
    adjacency_matrix: list

class OptimalAnglesDTO(BaseModel):
    adjacency_matrix: list = Field(..., example=[[0, 1], [1, 0]],
                                   description="Adjacency matrix as a list of lists, each inner list represents a node connection.")
    p: int = Field(..., example=1, description="Number of QAOA layers for the calculation.")

async def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = os.getenv('BASIC_AUTH_USERNAME', 'default_user')
    correct_password = os.getenv('BASIC_AUTH_PASSWORD', 'default_password')
    if credentials.username != correct_username or credentials.password != correct_password:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return credentials.username

@app.post("/graph/optimal_angles", response_model=dict, tags=["QAOAKit"],
          summary="Get Optimal Angles from QAOAKit",
          response_description="The optimal beta and gamma angles for the QAOA algorithm.",
          responses={
              200: {"description": "Successfully calculated and returned the optimal angles.",
                    "content": {"application/json": {"example": {"beta": [0.1], "gamma": [0.2], "optimal_angles": False, "source": "QAOAKit"}}}},
              400: {"description": "Invalid input data."},
              500: {"description": "Server error during angle calculation."}
          },
          dependencies=[Depends(authenticate_user)])
async def get_optimal_angles(optimal_angles_dto: OptimalAnglesDTO = Body(...)):
    try:
        adjacency_matrix = np.array(optimal_angles_dto.adjacency_matrix)
        G = nx.from_numpy_array(adjacency_matrix)
        graph = G
        qaoa_depth = optimal_angles_dto.p

        # Add in Gary work
        d_w = 0
        no_nodes = 0
        no_weighted_nodes = 0
        w = 0
        no_edges = 0
        for (node, weight) in graph.nodes(data = "weight"):
            d_w += graph.degree(node)
            if weight is not None:
                w += abs(weight)
                no_weighted_nodes += 1
            no_nodes += 1
        for (u, v, data) in graph.edges(data=True):
            w += abs(data["weight"])
            no_edges += 1
        
        d_w /= no_nodes # average node degree
        w /= no_edges # average edge weight
        median, kde = get_median_pre_trained_kde(qaoa_depth)
        params = {}
        params["beta"] = beta_to_qaoa_format(median[qaoa_depth:])
        params["gamma"] = gamma_to_qaoa_format(median[:qaoa_depth] * np.arctan(1/np.sqrt(d_w-1)) / w)
        # create a dictionary to return
        qaoa_params_dict = {"beta": list(params["beta"]), "gamma": list(params["gamma"]), "optimal_angles": False, "source": "QAOAKit"}
        print(qaoa_params_dict)
        return qaoa_params_dict

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
