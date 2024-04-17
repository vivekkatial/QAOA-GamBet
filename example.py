import requests
import json
import networkx as nx

def send_graph_for_optimal_angles():

    url = "http://127.0.0.1:8000/graph/optimal_angles"

    # Generate a random graph from networkx
    G = nx.random_regular_graph(3, 8)
    adjacency_matrix = nx.to_numpy_array(G).tolist()

    p = 2

    data = json.dumps({"adjacency_matrix": adjacency_matrix, "p": p})
    headers = {'Content-Type': 'application/json'}
    
    # Set username and password for Basic Authentication
    auth = ('admin', 'gmkit123')

    response = requests.post(url, headers=headers, data=data, auth=auth)

    if response.status_code == 200:
        print("Response from server:")
        print(json.dumps(response.json(), indent=2))
    else:
        print("Failed to get a response:", response.status_code, response.text)

if __name__ == "__main__":
    send_graph_for_optimal_angles()
