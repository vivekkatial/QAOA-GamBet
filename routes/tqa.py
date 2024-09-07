from fastapi import APIRouter, HTTPException, Body, Depends
from fastapi.security import HTTPBasic
import numpy as np
from models.dto import TQADTO
from models.base import OptimalAnglesResponseDTO
from utils.auth import authenticate_user

router = APIRouter()

@router.post("/graph/tqa_initialisation", response_model=OptimalAnglesResponseDTO, tags=["TQA"],
             summary="Get TQA Initialisation Angles",
             response_description="The TQA initialisation beta and gamma angles for the QAOA algorithm.",
             responses={
                 200: {"description": "Successfully calculated and returned the TQA initialisation angles.",
                       "content": {"application/json": {"example": {"beta": [0.1, 0.2, 0.3, 0.4], "gamma": [0.4, 0.3, 0.2, 0.1], "source": "TQA"}}}},
                 400: {"description": "Invalid input data."},
                 500: {"description": "Server error during angle calculation."}
             },
             dependencies=[Depends(authenticate_user)])
def get_tqa_initialisation(dto: TQADTO = Body(...)):
    """
    Endpoint to calculate the TQA initialisation QAOA angles from a given number of QAOA layers and total annealing time.

    These angles are generated using the Trotterised Quantum Annealing schedule and can be used as an initial guess for the QAOA algorithm.

    The TQA initialisation angles are generated as follows:
    
    * beta_i = (1 - t_i / t_{max}) * dt
    * gamma_i = (t_i / t_{max}) * dt

    Where:
    * t_i is the time at step i
    * t_{max} is the total annealing time
    * dt is the time step

    The number of layers and total annealing time are extracted from the input.
    
    To read more about the TQA method checkout the paper by Sack et al.: https://arxiv.org/abs/2101.05742
    """
    try:
        # Extract number of layers and total annealing time from input
        p = dto.p
        t_max = dto.t_max
        
        # Calculate time step
        dt = t_max / p
        
        # Calculate time points
        t = dt * (np.arange(1, p + 1) - 0.5)
        
        # Calculate gamma and beta values
        gamma = (t / t_max) * dt
        beta = (1 - (t / t_max)) * dt
        
        # Create response
        return OptimalAnglesResponseDTO(
            beta=list(beta),
            gamma=list(gamma),
            source="TQA"
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))