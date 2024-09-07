from fastapi import APIRouter, HTTPException, Body, Depends
from fastapi.security import HTTPBasic
import numpy as np
from models.dto import INTERPInitDTO
from models.base import OptimalAnglesResponseDTO
from utils.auth import authenticate_user

router = APIRouter()

@router.post("/graph/interp", response_model=OptimalAnglesResponseDTO, tags=["INTERP"],
             summary="Get INTERP Initialisation Angles",
             response_description="The INTERP initialisation beta and gamma angles for the next QAOA level.",
             responses={
                 200: {"description": "Successfully calculated and returned the INTERP initialisation angles for the next level.",
                       "content": {"application/json": {"example": {"beta": [0.1, 0.15, 0.2], "gamma": [0.3, 0.35, 0.4], "source": "INTERP"}}}},
                 400: {"description": "Invalid input data."},
                 500: {"description": "Server error during angle calculation."}
             },
             dependencies=[Depends(authenticate_user)])
def get_interp_initialisation(dto: INTERPInitDTO = Body(...)):
    """
    Endpoint to calculate the INTERP initialisation QAOA angles for the next level (p+1) based on the optimized angles from the current level p.

    The INTERP initialisation angles are generated using the method from Zhou et al.: https://arxiv.org/abs/1812.01041
    """
    try:
        # Extract current level and optimized angles from input
        p = dto.p - 1
        gamma_p = np.array(dto.gamma)
        beta_p = np.array(dto.beta)
        
        if len(gamma_p) != p or len(beta_p) != p:
            raise ValueError("The number of provided angles must match 'p'.")
        
        # Calculate angles for the next level
        gamma_next = interp_p_series(gamma_p)
        beta_next = interp_p_series(beta_p)
        
        # Create response
        return OptimalAnglesResponseDTO(
            beta=list(beta_next),
            gamma=list(gamma_next),
            source="INTERP"
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def interp_p_series(angles: np.ndarray) -> np.ndarray:
    """
    Interpolates p-series of QAOA angles at level p to generate good initial guess for level p + 1.
    """
    p = len(angles)
    new_angles = np.zeros(p + 1)
    new_angles[0] = angles[0]
    for i in range(1, p):
        new_angles[i] = i / p * angles[i - 1] + (1 - i / p) * angles[i]
    new_angles[-1] = angles[-1]
    return new_angles