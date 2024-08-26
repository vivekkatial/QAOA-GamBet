from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List

class InstanceClass(Enum):
    UNIFORM_RANDOM = "uniform_random"
    WATTS_STROGATZ_SMALL_WORLD = "watts_strogatz_small_world"
    GEOMETRIC = "geometric"
    POWER_LAW_TREE = "power_law_tree"
    THREE_REGULAR_GRAPH = "three_regular_graph"
    FOUR_REGULAR_GRAPH = "four_regular_graph"
    NEARLY_COMPLETE_BIPARTITE = "nearly_complete_bi_partite"
    
class WeightType(Enum):
    WEIGHTED = "weighted"
    UNWEIGHTED = "unweighted"

class GraphDTO(BaseModel):
    instance_id: int
    adjacency_matrix: list
    
class OptimalAnglesResponseDTO(BaseModel):
    beta: List[float] = Field(..., example=[0.1])
    gamma: List[float] = Field(..., example=[0.2])
    optimal_angles: bool = Field(False, example=False)
    source: str = Field("Strategy", example="Example")
    
class BaseQAOADTO(BaseModel):
    adjacency_matrix: List[List[int]] = Field(..., example=[[0, 1], [1, 0]])
    p: int = Field(1, example=1, description="Number of QAOA layers")
    