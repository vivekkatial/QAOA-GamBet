from pydantic import BaseModel, Field, validator
from enum import Enum
from typing import List, Optional
from .base import BaseQAOADTO, InstanceClass, WeightType
import math


class RandomInitializationDTO(BaseQAOADTO):
    pass

class QAOAKitBaseDTO(BaseQAOADTO):
    @validator('p')
    def validate_p(cls, v):
        if v not in [1, 2, 3]:
            raise ValueError("QAOAKit only supports p values of 1, 2, or 3")
        return v

class QAOAKitKDEDTO(QAOAKitBaseDTO):
    pass

class QAOAKitLookupDTO(QAOAKitBaseDTO):
    pass

class QIBPIDTO(BaseQAOADTO):
    graph_type: InstanceClass = Field(..., example=InstanceClass.UNIFORM_RANDOM, description="The type of graph instance")
    weight_type: WeightType = Field(..., example=WeightType.UNIFORM, description="The type of weight distribution for the graph edges")
    p: int = Field(..., ge=2, le=20, example=2, description="Number of QAOA layers (must be between 2 and 20)")

    @validator('p')
    def validate_p(cls, v):
        if not 2 <= v <= 20:
            raise ValueError("For QIBPI, p must be between 2 and 20, inclusive")
        return v

    @validator('graph_type')
    def validate_graph_type(cls, v):
        if v not in InstanceClass:
            raise ValueError(f"Invalid graph type. Must be one of: {', '.join([e.value for e in InstanceClass])}")
        return v

    @validator('weight_type')
    def validate_weight_type(cls, v):
        if v not in WeightType:
            raise ValueError(f"Invalid weight type. Must be one of: {', '.join([e.value for e in WeightType])}")
        return v

    class Config:
        use_enum_values = True
        
class TQADTO(BaseQAOADTO):
    t_max: float = Field(..., example=1.0, description="Total annealing time for TQA initialization")
    
    # Validate t_max is greater than 0 
    @validator('t_max')
    def validate_t_max(cls, v):
        if v <= 0:
            raise ValueError("Total annealing time (t_max) must be positive")
        return v
    
    @validator('p')
    def validate_p(cls, v):
        if v <= 0:
            raise ValueError("Number of layers (p) must be positive")
        return v
    
    
class FixedAnglesDTO(BaseQAOADTO):
    beta: float = Field(..., example=0.1, description="The fixed beta angle for QAOA")
    gamma: float = Field(..., example=0.2, description="The fixed gamma angle for QAOA")

    @validator('beta')
    def validate_beta(cls, v):
        if not -math.pi/4 <= v <= math.pi/4:
            raise ValueError("Beta must be between -π/4 and π/4")
        return v

    @validator('gamma')
    def validate_gamma(cls, v):
        if not -math.pi <= v <= math.pi:
            raise ValueError("Gamma must be between -π and π")
        return v
    
    
