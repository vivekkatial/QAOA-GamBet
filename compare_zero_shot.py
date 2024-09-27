import requests
import json
import networkx as nx
import numpy as np
import os
import csv
from dotenv import load_dotenv
import pennylane as qml
from pennylane import numpy as pnp
import matplotlib.pyplot as plt
import random

load_dotenv()
BASE_URL = "http://115.146.94.114:5000"
AUTH = (os.environ.get("BASIC_AUTH_USERNAME"), os.environ.get("BASIC_AUTH_PASSWORD"))

def ensure_results_directory():
    """Create a 'results' directory if it doesn't exist."""
    if not os.path.exists('results'):
        os.makedirs('results')

def create_random_graph(n, p):
    """Create a random graph with n nodes, edge probability p, and uniform random weights."""
    connected = False
    while not connected:
        G = nx.erdos_renyi_graph(n, p)
        connected = nx.is_connected(G)
    
    # Add uniform random weights
    for (u, v) in G.edges():
        G[u][v]['weight'] = random.uniform(0, 1)
    
    return G

def create_three_regular_graph(n):
    """Create a 3-regular graph with n nodes and uniform random weights."""
    G = nx.random_regular_graph(3, n)
    
    # Add uniform random weights
    for (u, v) in G.edges():
        G[u][v]['weight'] = random.uniform(0, 1)
    
    return G

def create_watts_strogatz_small_world(n):
    """Create a Watts-Strogatz small-world graph with n nodes and uniform random weights."""
    k = 4  # Each node is connected to k nearest neighbors in ring topology
    p = 0.3  # Probability of rewiring each edge
    G = nx.watts_strogatz_graph(n, k, p)
    
    # Add uniform random weights
    for (u, v) in G.edges():
        G[u][v]['weight'] = random.uniform(0, 1)
    
    return G

def make_request(endpoint, data):
    """
    Make a request to the API endpoint with the given data.
    """
    url = f"{BASE_URL}{endpoint}"
    response = requests.post(url, json=data, auth=AUTH)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

def maxcut_value(bitstring, w):
    """
    Compute the MaxCut value given a bitstring and a weight matrix.
    """
    obj = 0
    for i in range(len(bitstring)):
        for j in range(len(bitstring)):
            if w[i, j] != 0 and bitstring[i] != bitstring[j]:
                obj += w[i, j]
    return obj / 2

def compute_maxcut_optimal(G):
    """
    Compute the optimal MaxCut value using a brute-force approach.
    """
    num_nodes = len(G.nodes)
    max_cut = 0
    for bits in range(2**num_nodes):
        bitstring = [(bits >> i) & 1 for i in range(num_nodes)]
        value = maxcut_value(bitstring, nx.to_numpy_array(G))
        if value > max_cut:
            max_cut = value
    return max_cut

def run_qaoa_evaluation(G, beta, gamma, method_name, max_cut_value):
    """
    Evaluate QAOA circuit with given beta and gamma angles and compute the approximation ratio.
    
    Args:
        G: The graph to optimize over
        beta: The beta values
        gamma: The gamma values
        method_name: The name of the method used to initialize the angles
        max_cut_value: The optimal MaxCut value for the given graph

    Returns:
        approximation_ratio: The approximation ratio achieved by the QAOA
    """
    n_qubits = len(G.nodes)
    p = len(beta)
    dev = qml.device('default.qubit', wires=n_qubits)

    cost_h, mixer_h = qml.qaoa.maxcut(G)

    def qaoa_layer(beta, gamma):
        qml.qaoa.cost_layer(gamma, cost_h)
        qml.qaoa.mixer_layer(beta, mixer_h)

    @qml.qnode(dev, interface='autograd')
    def circuit(beta, gamma):
        # Initialize all qubits in the |+> state
        for i in range(n_qubits):
            qml.Hadamard(wires=i)
        # Apply QAOA layers
        for i in range(p):
            qaoa_layer(beta[i], gamma[i])
        return qml.expval(cost_h)

    # Evaluate the circuit
    energy = circuit(beta, gamma)
    qaoa_cut_value = -energy / 2  # Convert energy to cut value
    approximation_ratio = qaoa_cut_value / max_cut_value

    return approximation_ratio

def compare_initializations():
    print("Comparing QAOA Initialization Techniques Over Multiple Instances and Graph Types:")
    print("=============================================================================\n")

    num_instances = 100
    num_nodes = 12

    # List of initialization methods and their corresponding API endpoints
    methods = [
        ('QAOAKit', '/graph/QAOAKit/optimal_angles_kde'),
        ('Random Initialization', '/graph/random_initialisation'),
        ('QIBPI', '/graph/QIBPI'),
        ('TQA', '/graph/tqa_initialisation'),
        ('Fixed Angles', '/graph/fixed_angles'),
    ]

    # List of graph types and their creation functions
    graph_types = [
        ('Uniform-Random', create_random_graph),
        ('Three-Regular-Graph', create_three_regular_graph),
        ('Watts-Strogatz-Small-World', create_watts_strogatz_small_world)
    ]

    # Dictionary to store approximation ratios over instances
    p_values = [2, 3, 4, 5, 6, 7, 8, 9, 10]
    ar_history = {graph_type: {method_name: {p_value: [] for p_value in p_values} for method_name, _ in methods} for graph_type, _ in graph_types}

    # Ensure the results directory exists
    ensure_results_directory()
    zero_shot_dir = os.path.join('results', 'zero-shot')
    if not os.path.exists(zero_shot_dir):
        os.makedirs(zero_shot_dir)

    # Loop over graph types
    for graph_type, create_graph in graph_types:
        print(f"\nProcessing {graph_type} graphs:")
        print("=" * (len(graph_type) + 20))

        # Loop over the number of instances
        for instance_index in range(num_instances):
            print(f"  Processing instance {instance_index + 1}/{num_instances}...")

            # Generate a graph based on the current type
            if graph_type == 'Uniform-Random':
                G = create_graph(num_nodes, 0.5)
            else:
                G = create_graph(num_nodes)
            
            adj_matrix = nx.to_numpy_array(G).tolist()
            max_cut_value = compute_maxcut_optimal(G)

            for p_value in p_values:
                print(f"    Processing p = {p_value}")

                # Loop over each initialization method
                for method_name, endpoint in methods:
                    print(f"      Using {method_name}...")

                    # Prepare data for API request
                    data = {
                        "adjacency_matrix": adj_matrix,
                        "p": p_value
                    }
                    if method_name == 'Fixed Angles':
                        data.update({"beta": 0.1, "gamma": 0.2})
                    elif method_name == 'QIBPI':
                        data.update({"graph_type": graph_type.lower().replace("-", "_"), "weight_type": "uniform"})
                    elif method_name == 'TQA':
                        data.update({"t_max": 1.0})

                    # Make API request
                    result = make_request(endpoint, data)
                    if result:
                        beta = result['beta']
                        gamma = result['gamma']

                        # Ensure beta and gamma are lists
                        if isinstance(beta, (float, int)):
                            beta = [beta] * p_value
                        if isinstance(gamma, (float, int)):
                            gamma = [gamma] * p_value

                        # Run QAOA evaluation
                        approximation_ratio = run_qaoa_evaluation(G, beta, gamma, method_name, max_cut_value)
                        ar_history[graph_type][method_name][p_value].append(approximation_ratio)
                    else:
                        print(f"Failed to get angles for {method_name}")
                        ar_history[graph_type][method_name][p_value].append(0)

    # Compute averages and standard deviations
    avg_ar_history = {graph_type: {method_name: {} for method_name, _ in methods} for graph_type, _ in graph_types}
    std_ar_history = {graph_type: {method_name: {} for method_name, _ in methods} for graph_type, _ in graph_types}

    for graph_type in ar_history:
        for method_name in ar_history[graph_type]:
            for p_value in p_values:
                ar_list = ar_history[graph_type][method_name][p_value]
                avg_ar_history[graph_type][method_name][p_value] = np.mean(ar_list)
                std_ar_history[graph_type][method_name][p_value] = np.std(ar_list)

    # Save results to CSV files
    for graph_type, _ in graph_types:
        csv_filename = os.path.join(zero_shot_dir, f'{graph_type.lower().replace(" ", "_")}_approximation_ratios.csv')
        with open(csv_filename, 'w', newline='') as csvfile:
            fieldnames = ['Method', 'p', 'Instance', 'ApproximationRatio']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for method_name, _ in methods:
                for p in p_values:
                    for instance, ar in enumerate(ar_history[graph_type][method_name][p]):
                        writer.writerow({
                            'Method': method_name,
                            'p': p,
                            'Instance': instance,
                            'ApproximationRatio': ar
                        })


if __name__ == "__main__":
    compare_initializations()
