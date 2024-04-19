import requests
import json
import networkx as nx

def send_graph_for_optimal_angles():

    #    url = "http://115.146.94.114:5000/graph/optimal_angles"
    url = "http://localhost:8000/graph/optimal_angles"

    for i in range(100):
        # Generate a random graph from networkx
        G = nx.random_regular_graph(3, 8)
        # Generate watts_strogatz_graph
        # G = nx.watts_strogatz_graph(8, 3, 0.1)
        adjacency_matrix = nx.to_numpy_array(G).tolist()
        # adjacency_matrix = [[0.0, -1.0, 0.0, 0.0], [-1.0, 0.0, 0.0, 1.0], [0.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0]]

        p = 1

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
