from fastapi import APIRouter, HTTPException, Body, Depends
from fastapi.security import HTTPBasic
from pydantic import BaseModel, Field
import networkx as nx
import numpy as np
from QAOAKit import opt_angles_for_graph, angles_to_qaoa_format, beta_to_qaoa_format, gamma_to_qaoa_format
from QAOAKit.parameter_optimization import get_median_pre_trained_kde

from models.base import OptimalAnglesResponseDTO
from models.dto import QAOAKitKDEDTO, QAOAKitLookupDTO
from utils.auth import authenticate_user

router = APIRouter()

@router.post("/graph/QAOAKit/optimal_angles_kde", response_model=OptimalAnglesResponseDTO, tags=["QAOAKit"],
             summary="Get Optimal Angles from QAOAKit using the KDE Estimation",
             response_description="The optimal beta and gamma angles for the QAOA algorithm.",
             responses={
                 200: {"description": "Successfully calculated and returned the optimal angles.",
                       "content": {"application/json": {"example": {"beta": [0.1], "gamma": [0.2], "optimal_angles": False, "source": "QAOAKit"}}}},
                 400: {"description": "Invalid input data."},
                 500: {"description": "Server error during angle calculation."}
             },
             dependencies=[Depends(authenticate_user)])
def get_optimal_angles_kde(dto: QAOAKitKDEDTO = Body(...)):
    """
    QAOAKit is a toolkit for Reproducible Application and Verification of QAOA.
    
    To read more about the QAOAKit method [checkout the paper](https://www.computer.org/csdl/proceedings-article/qcs/2021/867400a064/1zxKuwgiuLS)
    """
    try:
        adjacency_matrix = np.array(dto.adjacency_matrix)
        G = nx.from_numpy_array(adjacency_matrix)
        graph = G
        qaoa_depth = dto.p

        d_w = 0
        no_nodes = 0
        no_weighted_nodes = 0
        w = 0
        no_edges = 0
        for (node, weight) in graph.nodes(data="weight"):
            d_w += graph.degree(node)
            if weight is not None:
                w += abs(weight)
                no_weighted_nodes += 1
            no_nodes += 1
        for (u, v, data) in graph.edges(data=True):
            w += abs(data["weight"])
            no_edges += 1
        
        d_w /= no_nodes  # average node degree
        w /= no_edges  # average edge weight
        median, kde = get_median_pre_trained_kde(qaoa_depth)
        params = {}
        params["beta"] = beta_to_qaoa_format(median[qaoa_depth:])
        params["gamma"] = gamma_to_qaoa_format(median[:qaoa_depth] * np.arctan(1/np.sqrt(d_w-1)) / w)

        return OptimalAnglesResponseDTO(beta=params["beta"], gamma=params["gamma"], source="QAOAKit_KDE", optimal_angles=False)

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
