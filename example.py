import requests
import json
import networkx as nx

def send_graph_for_optimal_angles():

    #    url = "http://115.146.94.114:5000/graph/optimal_angles"
    url = "http://localhost:8000"
    endpoints = [
        "/graph/QAOAKit/optimal_angles_kde",
        "/graph/QAOAKit/optimal_angles_lookup",
        "/graph/QIBPI/optimal_angles",
        "/graph/random_initialisation",
    ]

    for endpoint in endpoints:
        print(f"Sending request to {url}{endpoint}")
        send_request(url + endpoint)

def send_request(url):
    for i in range(1):
        # Generate a random graph from networkx
        G = nx.random_regular_graph(3, 8)
        adjacency_matrix = nx.to_numpy_array(G).tolist()
        p = 1

        data = json.dumps({"adjacency_matrix": adjacency_matrix, "p": p,})

        if "QIBPI" in url:
            data = json.dumps({"adjacency_matrix": adjacency_matrix, "p": p, "instance_class": "three_regular_graph"})
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
