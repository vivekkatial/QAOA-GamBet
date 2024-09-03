import pytest
from fastapi.testclient import TestClient
from main import app
import networkx as nx
import numpy as np
from models.base import InstanceClass

client = TestClient(app)

# Test data
TEST_USERNAME = "testuser"
TEST_PASSWORD = "testpass"

# Helper function to create a random graph
def create_random_graph(n, p):
    G = nx.erdos_renyi_graph(n, p)
    return nx.to_numpy_array(G).tolist()

# Fixture for authentication
@pytest.fixture(scope="module")
def auth_headers():
    return {"Authorization": f"Basic {TEST_USERNAME}:{TEST_PASSWORD}"}

# Test cases
def test_random_initialisation(auth_headers):
    graph = create_random_graph(5, 0.5)
    response = client.post("/graph/random_initialisation", 
                           json={"adjacency_matrix": graph, "p": 2},
                           headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "beta" in data and "gamma" in data
    assert len(data["beta"]) == 2 and len(data["gamma"]) == 2
    assert data["optimal_angles"] == False
    assert data["source"] == "Random"

def test_qaoakit_optimal_angles_kde(auth_headers):
    graph = create_random_graph(5, 0.5)
    response = client.post("/graph/QAOAKit/optimal_angles_kde", 
                           json={"adjacency_matrix": graph, "p": 1},
                           headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "beta" in data and "gamma" in data
    assert len(data["beta"]) == 1 and len(data["gamma"]) == 1
    assert data["optimal_angles"] == False
    assert data["source"] == "QAOAKit_KDE"

def test_qaoakit_optimal_angles_lookup(auth_headers):
    graph = create_random_graph(5, 0.5)
    response = client.post("/graph/QAOAKit/optimal_angles_lookup", 
                           json={"adjacency_matrix": graph, "p": 1},
                           headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "beta" in data and "gamma" in data
    assert len(data["beta"]) == 1 and len(data["gamma"]) == 1
    assert data["optimal_angles"] == True
    assert data["source"] == "QAOAKit_Lookup"

def test_qibpi_optimal_angles(auth_headers):
    graph = create_random_graph(5, 0.5)
    response = client.post("/graph/QIBPI/optimal_angles", 
                           json={"adjacency_matrix": graph, "p": 2, "instance_class": InstanceClass.UNIFORM_RANDOM.value},
                           headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "beta" in data and "gamma" in data
    assert len(data["beta"]) == 2 and len(data["gamma"]) == 2
    assert data["optimal_angles"] == False
    assert data["source"] == "QIBPI"

def test_tqa_initialisation(auth_headers):
    graph = create_random_graph(5, 0.5)
    response = client.post("/graph/tqa_initialisation", 
                           json={"adjacency_matrix": graph, "p": 3, "t_max": 1.0},
                           headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "beta" in data and "gamma" in data
    assert len(data["beta"]) == 3 and len(data["gamma"]) == 3
    assert data["optimal_angles"] == False
    assert data["source"] == "TQA"

def test_invalid_input(auth_headers):
    response = client.post("/graph/random_initialisation", 
                           json={"adjacency_matrix": [[0, 1], [1, 0]], "p": 0},
                           headers=auth_headers)
    assert response.status_code == 400

def test_unauthorized_access():
    graph = create_random_graph(5, 0.5)
    response = client.post("/graph/random_initialisation", 
                           json={"adjacency_matrix": graph, "p": 2})
    assert response.status_code == 401

def test_large_graph(auth_headers):
    graph = create_random_graph(20, 0.5)
    response = client.post("/graph/QAOAKit/optimal_angles_kde", 
                           json={"adjacency_matrix": graph, "p": 1},
                           headers=auth_headers)
    assert response.status_code == 200

def test_invalid_instance_class(auth_headers):
    graph = create_random_graph(5, 0.5)
    response = client.post("/graph/QIBPI/optimal_angles", 
                           json={"adjacency_matrix": graph, "p": 2, "instance_class": "invalid_class"},
                           headers=auth_headers)
    assert response.status_code == 400

if __name__ == "__main__":
    pytest.main()