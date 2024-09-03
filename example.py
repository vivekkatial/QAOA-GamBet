import requests
import json
import networkx as nx
import numpy as np

# Server configuration
BASE_URL = "http://localhost:5000"
AUTH = ('user', 'password')  # Replace with your actual credentials

# Helper function to create a random graph
def create_random_graph(n, p):
    connected = False
    while not connected:
        G = nx.erdos_renyi_graph(n, p)
        connected = nx.is_connected(G)
    return nx.to_numpy_array(G).tolist()

# Helper function to make API requests
def make_request(endpoint, data):
    url = f"{BASE_URL}{endpoint}"
    response = requests.post(url, json=data, auth=AUTH)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

# Test random initialization
def test_random_initialization():
    print("\nTesting Random Initialization:")
    data = {
        "adjacency_matrix": create_random_graph(5, 0.5),
        "p": 2
    }
    result = make_request("/graph/random_initialisation", data)
    if result:
        print(f"Random angles: Beta = {result['beta']}, Gamma = {result['gamma']}")

# Test QAOAKit KDE
def test_qaoakit_kde():
    print("\nTesting QAOAKit KDE:")
    data = {
        "adjacency_matrix": create_random_graph(5, 0.5),
        "p": 1
    }
    result = make_request("/graph/QAOAKit/optimal_angles_kde", data)
    if result:
        print(f"QAOAKit KDE angles: Beta = {result['beta']}, Gamma = {result['gamma']}")


# Test QIBPI
def test_qibpi():
    print("\nTesting QIBPI:")
    data = {
        "adjacency_matrix": create_random_graph(5, 0.5),
        "p": 2,
        "graph_type": "uniform_random",
        "weight_type": "uniform"
    }
    result = make_request("/graph/QIBPI/optimal_angles", data)
    if result:
        print(f"QIBPI angles: Beta = {result['beta']}, Gamma = {result['gamma']}")

# Test TQA
def test_tqa():
    print("\nTesting TQA:")
    data = {
        "adjacency_matrix": create_random_graph(5, 0.5),
        "p": 3,
        "t_max": 1.0
    }
    result = make_request("/graph/tqa_initialisation", data)
    if result:
        print(f"TQA angles: Beta = {result['beta']}, Gamma = {result['gamma']}")

# Test Fixed Angles
def test_fixed_angles():
    print("\nTesting Fixed Angles:")
    data = {
        "adjacency_matrix": create_random_graph(5, 0.5),
        "p": 2,
        "beta": 0.1,
        "gamma": 0.2
    }
    result = make_request("/graph/fixed_angles", data)
    if result:
        print(f"Fixed angles: Beta = {result['beta']}, Gamma = {result['gamma']}")

# Run all tests
if __name__ == "__main__":
    print("Testing QAOA-Param-Server Endpoints")
    print("===================================")
    
    test_random_initialization()
    test_qaoakit_kde()
    test_qibpi()
    test_tqa()
    test_fixed_angles()

    print("\nAll tests completed.")