# Guide: Extending and Creating a New Endpoint for your own Initialization Strategy

## 1. Create a new endpoint 

In the `routes/` directory, create a new file for your endpoint. For example, if you want to create an endpoint for the `INTERP` initialization strategy, create a file named `interp.py`.


## 2. Create a data model for your strategy

Create a Pydantic model for the request payload. This model will be used to validate the request data. This is stored in the `models/dto.py` file.

For example, if you are creating an endpoint for the `INTERP` initialization strategy you would add the following:

```python
# models/dto.py

class INTERPDTO(BaseQAOADTO):
     # List of betas and gammas for interpolation
     betas: List[float] = Field(..., example=[0.1, 0.2, 0.3], description="The beta angles for the interpolation")
     gammas: List[float] = Field(..., example=[0.4, 0.5, 0.6], description="The gamma angles for the interpolation")
    
     @validator('betas')
     def validate_betas(cls, v):
         if len(v) < 2:
             raise ValueError("At least two beta angles must be provided")
         return v
    
     @validator('p')
     def validate_p(cls, v):
         if v <= 1:
             raise ValueError("Number of layers (p) must be greater than 1")
         return v
    
     @validator('betas')
     def validate_betas(cls, v):
         if len(v) != len(cls.gammas):
             raise ValueError("Betas and gammas must have the same length")
         return v
    
     @validator('gammas')
     def validate_gammas(cls, v):
         if len(v) != len(cls.betas):
             raise ValueError("Betas and gammas must have the same length")
        return v    
```

In this DTO we have outlined the structure of the request payload. We have also added validators to ensure that the request payload is valid.

1. `betas`: A list of beta angles for the interpolation.
2. `gammas`: A list of gamma angles for the interpolation.
3. `p`: The number of QAOA layers.

We also validate that the number of betas and gammas are the same, and that the number of layers is greater than 1.

## 3. Implement the endpoint

Your endpoint should be a FastAPI route that takes in a JSON payload, validates it, and then calls the appropriate initialization strategy.

Here's an example of what the file should look like:

```python
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
                       "content": {"application/json": {"example": {"beta": [0.1, 0.2, 0.3], "gamma": [0.4, 0.3, 0.2], "source": "INTERP"}}}},
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
```

## 4. Add the endpoint to the API

Add the endpoint to the API in the `main.py` file.

```python
# main.py
app.include_router(interp.router)
```

## 5. Run the API

```bash
uvicorn main:app --reload
```
