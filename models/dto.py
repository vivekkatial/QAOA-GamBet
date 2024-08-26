from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional
from .base import BaseQAOADTO, InstanceClass, WeightType


class RandomInitializationDTO(BaseQAOADTO):
    pass

class QAOAKitKDEDTO(BaseQAOADTO):
    pass

class QAOAKitLookupDTO(BaseQAOADTO):
    pass

class QIBPIDTO(BaseQAOADTO):
    graph_type: InstanceClass = Field(..., example=InstanceClass.UNIFORM_RANDOM, description="The type of graph instance")
    weight_type: WeightType = Field(..., example=WeightType.UNWEIGHTED, description="Whether the graph is weighted or unweighted")

class TQADTO(BaseQAOADTO):
    t_max: float = Field(..., example=1.0, description="Total annealing time for TQA initialization")
    
class FixedAnglesDTO(BaseQAOADTO):
    pass
