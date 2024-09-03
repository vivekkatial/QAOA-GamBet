from enum import Enum
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from typing import List
import numpy as np
import networkx as nx

class InstanceClass(Enum):
    UNIFORM_RANDOM = "uniform_random"
    WATTS_STROGATZ_SMALL_WORLD = "watts_strogatz_small_world"
    GEOMETRIC = "geometric"
    POWER_LAW_TREE = "power_law_tree"
    THREE_REGULAR_GRAPH = "three_regular_graph"
    FOUR_REGULAR_GRAPH = "four_regular_graph"
    NEARLY_COMPLETE_BIPARTITE = "nearly_complete_bi_partite"
    
class WeightType(str, Enum):
    UNIFORM = "uniform"
    UNIFORM_PLUS = "uniform_plus"
    NORMAL = "normal"
    EXPONENTIAL = "exponential"
    LOG_NORMAL = "log-normal"
    CAUCHY = "cauchy"

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
    p: int = Field(1, ge=1, le=100, example=1, description="Number of QAOA layers")

    @validator('adjacency_matrix')
    def validate_adjacency_matrix(cls, v):
        matrix = np.array(v)
        if matrix.shape[0] != matrix.shape[1]:
            raise ValueError("Adjacency matrix must be square")
        if not np.allclose(matrix, matrix.T):
            raise ValueError("Adjacency matrix must be symmetric for undirected graphs")
        if not np.allclose(np.diag(matrix), 0):
            raise ValueError("Diagonal elements of adjacency matrix must be zero (no self-loops)")
        # Check if network is connected
        if not nx.is_connected(nx.from_numpy_array(matrix)):
            raise ValueError("Adjacency matrix must correspond to a connected graph")
        return v

    @validator('p')
    def validate_p(cls, v):
        if v <= 0:
            raise ValueError("Number of QAOA layers (p) must be positive")
        if v > 100:  # Example maximum, adjust as needed
            raise ValueError("Number of QAOA layers (p) exceeds maximum allowed value")
        return v
    
    
    