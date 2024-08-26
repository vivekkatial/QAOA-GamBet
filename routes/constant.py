from fastapi import APIRouter, HTTPException, Body, Depends
from fastapi.security import HTTPBasic
import numpy as np
from models.dto import FixedAnglesDTO
from models.base import OptimalAnglesResponseDTO
from utils.auth import authenticate_user

router = APIRouter()

@router.post("/graph/fixed_angles", response_model=OptimalAnglesResponseDTO, tags=["Random"],
             summary="Get Fixed Angles.",
             response_description="This returns fixed values of beta and gamma angles for the QAOA algorithm for a specific layer depth $p$.",
             responses={
                 200: {"description": "Successfully calculated and returned the random initialisation angles.",
                       "content": {"application/json": {"example": {"beta": [0.1], "gamma": [0.2], "optimal_angles": False, "source": "QAOAKit_Random"}}}},
                 400: {"description": "Invalid input data."},
                 500: {"description": "Server error during angle calculation."}},
             dependencies=[Depends(authenticate_user)])
def get_fixed_angles_constnat(dto: FixedAnglesDTO = Body(...)):
    """
    Endpoint to serve fixed angles for QAOA.

    - Beta_i should be between [-pi/4, pi/4]
    - Gamma_i should be between [-pi, pi]

    The number of layers is extracted from the input.
    """
    try:
        # extract number of layers from input
        p = dto.p
        
        # Make fixed angles
        beta = [0.1] * p
        gamma = [0.2] * p
        
        # create a dictionary to return
        return OptimalAnglesResponseDTO(beta=list(beta), gamma=list(gamma), optimal_angles=False, source="Random")
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))