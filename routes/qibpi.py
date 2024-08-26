from fastapi import APIRouter, HTTPException, Body, Depends
from fastapi.security import HTTPBasic
import pandas as pd
from models.base import OptimalAnglesResponseDTO, InstanceClass 
from models.dto import QIBPIDTO

from utils.auth import authenticate_user

router = APIRouter()

# Read from the CSV file
df = pd.read_csv('data/optimal-parameters.csv')

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

@router.post("/graph/QIBPI/optimal_angles", response_model=OptimalAnglesResponseDTO, tags=["QIBPI"],
             summary="Get Optimal Angles from QIBPI",
             response_description="The optimal beta and gamma angles for the QIBPI algorithm.",
             responses={
                 200: {"description": "Successfully calculated and returned the optimal angles."},
                 400: {"description": "Invalid input data."},
                 500: {"description": "Server error during angle calculation."}
             },
             dependencies=[Depends(authenticate_user)])
def get_optimal_angles_qibpi(dto: QIBPIDTO = Body(...)):
    """
    Endpoint to calculate the optimal QIBPI angles from a given adjacency matrix, QAOA layers, and instance class.
    """
    try:
        source = dto.instance_class
        n_layers = dto.p
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