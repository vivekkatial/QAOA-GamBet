import requests
import json
import networkx as nx

def send_graph_for_optimal_angles(data):
    # Base URL for requests
    url = "http://115.146.94.114:5000"
    # List of endpoints to send requests to
    endpoints = [
        "/graph/QAOAKit/optimal_angles_kde",
        "/graph/QIBPI/optimal_angles",
        "/graph/random_initialisation",
    ]

    for endpoint in endpoints:
        print(f"Sending request to {url}{endpoint}")
        send_request(url + endpoint, data)

def send_request(url, data):
    headers = {'Content-Type': 'application/json'}
    auth = ('admin', 'test123')  # Basic Authentication credentials
    
    # Send the request
    response = requests.post(url, headers=headers, data=data, auth=auth)
    
    if response.status_code == 200:
        print("Response from server:")
        print(json.dumps(response.json(), indent=2))
    else:
        print("Failed to get a response:", response.status_code, response.text)

if __name__ == "__main__":
    # Create the graph and data only once
    G = nx.random_regular_graph(3, 8)
    adjacency_matrix = nx.to_numpy_array(G).tolist()
    p = 1
    data = json.dumps({"adjacency_matrix": adjacency_matrix, "p": p, "instance_class": "three_regular_graph"})
    
    send_graph_for_optimal_angles(data)
