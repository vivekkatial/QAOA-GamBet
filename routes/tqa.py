from fastapi import APIRouter, HTTPException, Body, Depends
from fastapi.security import HTTPBasic
import numpy as np
from models import OptimalAnglesDTO, OptimalAnglesResponseDTO
from utils.auth import authenticate_user

router = APIRouter()

@router.post("/graph/tqa_initialisation", response_model=OptimalAnglesResponseDTO, tags=["TQA"],
             summary="Get TQA Initialisation Angles",
             response_description="The TQA initialisation beta and gamma angles for the QAOA algorithm.",
             responses={
                 200: {"description": "Successfully calculated and returned the TQA initialisation angles.",
                       "content": {"application/json": {"example": {"beta": [0.1, 0.2, 0.3, 0.4], "gamma": [0.4, 0.3, 0.2, 0.1], "optimal_angles": False, "source": "TQA"}}}},
                 400: {"description": "Invalid input data."},
                 500: {"description": "Server error during angle calculation."}
             },
             dependencies=[Depends(authenticate_user)])
def get_tqa_initialisation(optimal_angles_dto: OptimalAnglesDTO = Body(...)):
    """
    Endpoint to calculate the TQA initialisation QAOA angles from a given number of QAOA layers and total annealing time.

    These angles are generated using the Trotterised Quantum Annealing schedule and can be used as an initial guess for the QAOA algorithm.

    The TQA initialisation angles are generated as follows:
    - Beta_i = (1 - t_i / t_max) * dt
    - Gamma_i = (t_i / t_max) * dt

    Where t_i is the time at step i, t_max is the total annealing time, and dt is the time step.

    The number of layers and total annealing time are extracted from the input.
    """
    try:
        # Extract number of layers and total annealing time from input
        p = optimal_angles_dto.p
        t_max = optimal_angles_dto.t_max

        # Validate inputs
        if p <= 0:
            raise ValueError("Number of layers (p) must be positive.")
        if t_max <= 0:
            raise ValueError("Total annealing time (t_max) must be positive.")
        
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
            optimal_angles=False,
            source="TQA"
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))