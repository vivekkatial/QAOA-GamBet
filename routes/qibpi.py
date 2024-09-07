import os
import pandas as pd
from fastapi import APIRouter, HTTPException, Body, Depends
from models.base import OptimalAnglesResponseDTO, InstanceClass 
from models.dto import QIBPIDTO
from utils.auth import authenticate_user

router = APIRouter()

# Directory containing QIBPI CSV files
qibpi_dir = 'qibpi/'

def get_optimal_parameters(source, weight_type, n_layers):
    # Read in the CSV file for the given layer
    qibpi_data = pd.read_csv(qibpi_dir + f'qibpi_data_{n_layers}.csv')
    # Filter the dataframe for the given source and weight type
    filtered_df = qibpi_data[(qibpi_data['graph_type'] == source) & (qibpi_data['weight_type'] == weight_type)]
    # Extract the row as a dictionary
    params = filtered_df.iloc[0].to_dict()
    # Extract beta and gamma valuescr
    betas = [params[f'median_beta_{i}'] for i in range(n_layers)]
    gammas = [params[f'median_gamma_{i}'] for i in range(n_layers)]

    # Create and return the OptimalAnglesResponseDTO
    return OptimalAnglesResponseDTO(
        beta=betas,
        gamma=gammas,
        source="QIBPI",
        optimal_angles=False
    )
    return filtered_df

@router.post("/graph/QIBPI", response_model=OptimalAnglesResponseDTO, tags=["QIBPI"],
             summary="Get Optimal Angles from QIBPI",
             response_description="The optimal beta and gamma angles for the QIBPI algorithm.",
             responses={
                 200: {
                     "description": "Successfully calculated and returned the optimal angles.",
                     "content": {
                         "application/json": {
                             "example": {
                                 "beta": [0.1, 0.2],
                                 "gamma": [0.4, 0.5],
                                 "source": "QIBPI"
                             }
                         }
                     }
                 },
                 400: {"description": "Invalid input data."},
                 500: {"description": "Server error during angle calculation."}
             },
             dependencies=[Depends(authenticate_user)])
def get_optimal_angles_qibpi(dto: QIBPIDTO = Body(...)):
    """
    Endpoint to calculate the optimal QIBPI angles from a given adjacency matrix, QAOA layers, and instance class.
    
    To read more about the QIBPI method checkout the paper: https://arxiv.org/abs/2401.08142
    """
    try:
        source = dto.graph_type
        n_layers = dto.p
        weight_type = dto.weight_type
        if source == "erdos_renyi" or source == "uniform_random":
            source = "Uniform Random"
        elif source == "watts_strogatz_small_world":
            source = "Watts-Strogatz small world"
        elif source == "three_regular_graph":
            source = "3-Regular Graph"
        elif source == "four_regular_graph":
            source = "4-Regular Graph"
        elif source == "nearly_complete_bipartite":
            source = "Nearly Complete BiPartite"
        elif source == "power_law_tree":
            source = "Power Law Tree"
            
        return get_optimal_parameters(source, weight_type, n_layers)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
