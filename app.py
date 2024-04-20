import uvicorn
from enum import Enum
from fastapi import FastAPI, HTTPException, Body, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field
import networkx as nx
import numpy as np
import pandas as pd
import os
from dotenv import load_dotenv
import logging
from QAOAKit.parameter_optimization import get_median_pre_trained_kde
from QAOAKit import opt_angles_for_graph, angles_to_qaoa_format, beta_to_qaoa_format, gamma_to_qaoa_format

# Read from the CSV file
df = pd.read_csv('data/optimal-parameters.csv')

logging.basicConfig(level=logging.WARNING)

load_dotenv()  # Load environment variables from .env file

app = FastAPI(title="QAOAKit", description="API for the QAOAKit library.",)
security = HTTPBasic()

from QAOAKit import opt_angles_for_graph, angles_to_qaoa_format

def get_optimal_parameters(source, n_layers, df):
    """Get optimal parameters for a given source and number of layers."""
    # Check if the dataframe is empty
    if df.empty:
        return "No data available."

    # Allowed source values
    allowed_sources = [
        "four_regular_graph",
        "geometric",
        "nearly_complete_bi_partite",
        "power_law_tree",
        "three_regular_graph",
        "uniform_random",
        "watts_strogatz_small_world",
    ]
    # Check if the source is valid
    if source not in allowed_sources:
        return "Invalid source. Please choose from the allowed values."

    # Filter the dataframe for the specific source and number of layers
    filtered_df = df[(df['Source'] == source) & (df['params.n_layers'] == n_layers)]

    # Check if the filtered dataframe is not empty
    if not filtered_df.empty:
        # Initialize lists for beta and gamma values
        beta_values = []
        gamma_values = []

        # Extract relevant beta and gamma values
        for i in range(1, n_layers + 1):
            beta_key = 'median_beta_' + str(i)
            gamma_key = 'median_gamma_' + str(i)
            beta_values.append(filtered_df.iloc[0][beta_key])
            gamma_values.append(filtered_df.iloc[0][gamma_key])

        # Creating the final result
        params = {
            'beta': beta_values,
            'gamma': gamma_values,
            'Source': source,
            'params.n_layers': n_layers,
        }
        return params
    else:
        return "No data available for the specified source and number of layers."

class InstanceClass(Enum):
    UNIFORM_RANDOM = "uniform_random"
    WATTS_STROGATZ_SMALL_WORLD = "watts_strogatz_small_world"
    GEOMETRIC = "geometric"
    POWER_LAW_TREE = "power_law_tree"
    THREE_REGULAR_GRAPH = "three_regular_graph"
    FOUR_REGULAR_GRAPH = "four_regular_graph"
    NEARLY_COMPLETE_BIPARTITE = "nearly_complete_bi_partite"

class GraphDTO(BaseModel):
    instance_id: int
    adjacency_matrix: list

class OptimalAnglesDTO(BaseModel):
    adjacency_matrix: list = Field(..., example=[[0, 1], [1, 0]],
                                   description="Adjacency matrix as a list of lists, each inner list represents a node connection.")
    # Add the number of QAOA layers as a required field (or default to 1 if not provided)
    p: int = Field(1, example=1, description="The number of QAOA layers to use.")
    # Make this optional
    instance_class: InstanceClass = Field(None, example="Uniform Random", description="The instance class.")

# Create a  DTO for the response of the optimal angles
class OptimalAnglesResponseDTO(BaseModel):
    beta: list = Field(..., example=[0.1], description="The optimal beta angles for the QAOA algorithm.")
    gamma: list = Field(..., example=[0.2], description="The optimal gamma angles for the QAOA algorithm.")
    optimal_angles: bool = Field(False, example=False, description="Whether the angles are optimal or not.")
    source: str = Field("QAOAKit", example="QAOAKit", description="The source of the optimal angles.")

async def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = os.getenv('BASIC_AUTH_USERNAME', 'default_user')
    correct_password = os.getenv('BASIC_AUTH_PASSWORD', 'default_password')
    if credentials.username != correct_username or credentials.password != correct_password:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return credentials.username

@app.post("/graph/QAOAKit/optimal_angles_kde", response_model=OptimalAnglesResponseDTO, tags=["QAOAKit"],
          summary="Get Optimal Angles from QAOAKit using the KDE Estimation",
          response_description="The optimal beta and gamma angles for the QAOA algorithm.",
          responses={
              200: {"description": "Successfully calculated and returned the optimal angles.",
                    "content": {"application/json": {"example": {"beta": [0.1], "gamma": [0.2], "optimal_angles": False, "source": "QAOAKit"}}}},
              400: {"description": "Invalid input data."},
              500: {"description": "Server error during angle calculation."}
          },
          dependencies=[Depends(authenticate_user)])
def get_optimal_angles_kde(optimal_angles_dto: OptimalAnglesDTO = Body(...)):
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

        return OptimalAnglesResponseDTO(beta=params["beta"], gamma=params["gamma"], source="QAOAKit_KDE", optimal_angles=False)


    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/graph/QAOAKit/optimal_angles_lookup", response_model=OptimalAnglesResponseDTO, tags=["QAOAKit"],
          summary="Get Optimal Angles from QAOAKit using the Lookup Table", 
          response_description="The optimal beta and gamma angles for the QAOA algorithm based on the QAOAKit Lookup Table.",
          responses={
              200: {"description": "Successfully calculated and returned the optimal angles.",
                    "content": {"application/json": {"example": {"beta": [0.1], "gamma": [0.2], "optimal_angles": False, "source": "QAOAKit_Lookup"}}}},
              400: {"description": "Invalid input data."},
              500: {"description": "Server error during angle calculation."}
          },
          dependencies=[Depends(authenticate_user)])
def get_optimal_angles_lookup(optimal_angles_dto: OptimalAnglesDTO = Body(...)):
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
    

@app.post("/graph/QIBPI/optimal_angles", response_model=OptimalAnglesResponseDTO, tags=["QIBPI"],
            summary="Get Optimal Angles from QIBPI",
            response_description="The optimal beta and gamma angles for the QIBPI algorithm.",
            responses={
                200: {"description": "Successfully calculated and returned the optimal angles."},
                400: {"description": "Invalid input data."},
                500: {"description": "Server error during angle calculation."}
            },
            dependencies=[Depends(authenticate_user)])
def get_optimal_angles_qibpi(optimal_angles_dto: OptimalAnglesDTO = Body(...)):
    """
    Endpoint to calculate the optimal QIBPI angles from a given adjacency matrix, QAOA layers, and instance class.
    """
    try:
        source = optimal_angles_dto.instance_class
        n_layers = optimal_angles_dto.p
        if source is None:
            raise ValueError("Instance class is required.")
        else:
            source = source.value
            
        params = get_optimal_parameters(source, n_layers, df)

        if isinstance(params, str):
            raise ValueError(params)

        return params
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
def get_optimal_parameters(source, n_layers, df):
    """Get optimal parameters for a given source and number of layers."""
    # Check if the dataframe is empty
    if df.empty:
        return "No data available."

    # Check if the source is valid
    allowed_sources = [src.value for src in InstanceClass]
    if source not in allowed_sources:
        return "Invalid source. Please choose from the allowed values."

    # Filter the dataframe for the specific source and number of layers
    filtered_df = df[(df['Source'] == source) & (df['params.n_layers'] == n_layers)]

    # Check if the filtered dataframe is not empty
    if not filtered_df.empty:
        beta_values = [filtered_df.iloc[0]['median_beta_' + str(i)] for i in range(1, n_layers + 1)]
        gamma_values = [filtered_df.iloc[0]['median_gamma_' + str(i)] for i in range(1, n_layers + 1)]

        params = {
            'beta': beta_values,
            'gamma': gamma_values,
            'Source': source,
            'params.n_layers': n_layers,
        }
        return OptimalAnglesResponseDTO(beta=params["beta"], gamma=params["gamma"], source="QIBPI", optimal_angles=False)
    else:
        return "No data available for the specified source and number of layers."
    
# Make an endpoint for random initialisation (this one should be tagged as random and would only need the number of qaoa layers
# as input).
@app.post("/graph/random_initialisation", response_model=OptimalAnglesResponseDTO, tags=["Random"],
          summary="Get Random Initialisation Angles.",
          response_description="The random initialisation beta and gamma angles for the QAOA algorithm.",
          responses={
              200: {"description": "Successfully calculated and returned the random initialisation angles.",
                    "content": {"application/json": {"example": {"beta": [0.1], "gamma": [0.2], "optimal_angles": False, "source": "QAOAKit_Random"}}}},
              400: {"description": "Invalid input data."},
              500: {"description": "Server error during angle calculation."}},
          dependencies=[Depends(authenticate_user)])
def get_random_initialisation(optimal_angles_dto: OptimalAnglesDTO = Body(...)):
    """
    Endpoint to calculate the random initialisation QAOA angles from a given adjacency matrix and QAOA layers.

    These angles are randomly generated and can be used as an initial guess for the QAOA algorithm.

    The random initialisation angles are generated as follows:
    - Beta_i should be between [-pi/4, pi/4]
    - Gamma_i should be between [-pi, pi]

    The number of layers is extracted from the input.
    """
    try:
        # extract number of layers from input
        p = optimal_angles_dto.p
        # generate random initialisation angles
        # Beta should be between -pi/4 and pi/4
        beta = np.random.uniform(-np.pi/4, np.pi/4, p)
        # Gamma should be between -pi and pi
        gamma = np.random.uniform(-np.pi, np.pi, p)
        # create a dictionary to return
        random_angles_dict = {"beta": list(beta), "gamma": list(gamma), "optimal_angles": False, "source": "Random"}
        return random_angles_dict
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
