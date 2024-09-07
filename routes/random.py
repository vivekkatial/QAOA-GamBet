from fastapi import APIRouter, HTTPException, Body, Depends
from fastapi.security import HTTPBasic
import numpy as np
from models.dto import RandomInitializationDTO
from models.base import OptimalAnglesResponseDTO
from utils.auth import authenticate_user

router = APIRouter()

@router.post("/graph/random_initialisation", response_model=OptimalAnglesResponseDTO, tags=["Random"],
             summary="Get Random Initialisation Angles.",
             response_description="The random initialisation beta and gamma angles for the QAOA algorithm.",
             responses={
                 200: {"description": "Successfully calculated and returned the random initialisation angles.",
                       "content": {"application/json": {"example": {"beta": [0.1], "gamma": [0.2], "source": "Random"}}}},
                 400: {"description": "Invalid input data."},
                 500: {"description": "Server error during angle calculation."}},
             dependencies=[Depends(authenticate_user)])
def get_random_initialisation(dto: RandomInitializationDTO = Body(...)):
    """
    Endpoint to calculate the random initialisation QAOA angles from a given adjacency matrix and QAOA layers.

    These angles are randomly generated and can be used as an initial guess for the QAOA algorithm.

    The random initialisation angles are generated as follows:
    - beta_i should be between [-pi/4, pi/4]
    - gamma_i should be between [-pi, pi]

    The number of layers is extracted from the input.
    """
    try:
        # extract number of layers from input
        p = dto.p
        # Beta should be between -pi/4 and pi/4
        beta = np.random.uniform(-np.pi/4, np.pi/4, p)
        # Gamma should be between -pi and pi
        gamma = np.random.uniform(-np.pi, np.pi, p)
        # create a dictionary to return
        return OptimalAnglesResponseDTO(beta=list(beta), gamma=list(gamma), source="Random")
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))