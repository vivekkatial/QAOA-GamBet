from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional

class InstanceClass(Enum):
    UNIFORM_RANDOM = "uniform_random"
    WATTS_STROGATZ_SMALL_WORLD = "watts_strogatz_small_world"
    GEOMETRIC = "geometric"
    POWER_LAW_TREE = "power_law_tree"
    THREE_REGULAR_GRAPH = "three_regular_graph"
    FOUR_REGULAR_GRAPH = "four_regular_graph"
    NEARLY_COMPLETE_BIPARTITE = "nearly_complete_bi_partite"

class GraphDTO(BaseModel):
    instance_id: int
    adjacency_matrix: list

class OptimalAnglesDTO(BaseModel):
    adjacency_matrix: list = Field(..., example=[[0, 1], [1, 0]])
    p: int = Field(1, example=1)
    instance_class: Optional[str] = Field(None, example="Uniform Random", description="The instance class.")
    t_max: Optional[float] = Field(1.0, example=1.0, description="Total annealing time for TQA initialization.")
    
class OptimalAnglesResponseDTO(BaseModel):
    beta: list = Field(..., example=[0.1])
    gamma: list = Field(..., example=[0.2])
    optimal_angles: bool = Field(False, example=False)
    source: str = Field("Strategy", example="Example")