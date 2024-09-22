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
from pennylane.optimize import AdamOptimizer
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

def create_power_law_tree(n):
    """Create a power-law tree with n nodes and uniform random weights."""
    G = nx.random_powerlaw_tree(n)
    
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

def run_qaoa_optimization(G, beta_init, gamma_init, method_name, max_cut_value):
    """
    Run QAOA optimization and record convergence data.
    
    Args:
        G: The graph to optimize over
        beta_init: The initial beta values
        gamma_init: The initial gamma values
        method_name: The name of the method used to initialize the angles
        max_cut_value: The optimal MaxCut value for the given graph

    Returns:
        approximation_ratio: The approximation ratio achieved by the QAOA
        total_fevals: The total number of function evaluations
    """
    n_qubits = len(G.nodes)
    p = len(beta_init)
    dev = qml.device('default.qubit', wires=n_qubits)

    cost_h, mixer_h = qml.qaoa.maxcut(G)

    def qaoa_layer(beta, gamma):
        qml.qaoa.cost_layer(gamma, cost_h)
        qml.qaoa.mixer_layer(beta, mixer_h)

    @qml.qnode(dev, interface='autograd')
    def circuit(params):
        # Initialize all qubits in the |+> state
        for i in range(n_qubits):
            qml.Hadamard(wires=i)
        # Apply QAOA layers
        for i in range(p):
            qaoa_layer(params[i], params[i + p])
        return qml.expval(cost_h)

    fevals = [0]  # Use a list to make it mutable in nested functions

    # Wrap the circuit to count function evaluations
    def cost_fn(params):
        fevals[0] += 1
        return circuit(params)

    # Combine initial beta and gamma into a single parameter array
    beta_init = pnp.array(beta_init, requires_grad=True)
    gamma_init = pnp.array(gamma_init, requires_grad=True)
    params_init = pnp.concatenate([beta_init, gamma_init])

    # Choose an optimizer with a larger initial step size
    optimizer = AdamOptimizer(stepsize=0.1)

    # Convergence criteria
    max_steps = 200  # Reduce max steps since we're using a more efficient optimizer
    tol = 1e-5  # Tighten the tolerance

    # Perform optimization until convergence
    params = params_init
    prev_energy = None
    best_energy = float('inf')
    no_improvement_count = 0
    for i in range(max_steps):
        params, energy = optimizer.step_and_cost(cost_fn, params)
        
        # Print optimization progress every 100 iterations
        if i % 100 == 0:
            current_ratio = -energy / max_cut_value
            print(f"  {method_name}: Iteration {i}, Approximation Ratio: {current_ratio:.4f}")
        
        # Check for improvement
        if energy < best_energy:
            best_energy = energy
            no_improvement_count = 0
        else:
            no_improvement_count += 1

        # Early stopping if no improvement for 20 consecutive iterations
        if no_improvement_count >= 20:
            print(f"  {method_name}: Early stopping at iteration {i}")
            break

        if prev_energy is not None:
            delta_energy = abs(energy - prev_energy)
            if delta_energy < tol:
                print(f"  {method_name}: Converged at iteration {i}")
                break
        prev_energy = energy

    # After optimization, compute final approximation ratio
    final_energy = cost_fn(params)
    approximation_ratio = -final_energy / max_cut_value  # Negate the energy to make it positive

    total_fevals = fevals[0]

    return approximation_ratio, total_fevals

def compare_initializations():
    print("Comparing QAOA Initialization Techniques Over Multiple Instances and Graph Types:")
    print("=============================================================================\n")

    num_instances = 30
    num_nodes = 10

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
        ('Power-Law-Tree', create_power_law_tree)
    ]

    # Dictionary to store approximation ratios and fevals over instances
    p_values = [2, 3, 4, 5, 6, 7, 8, 9, 10]
    ar_history = {graph_type: {method_name: {p_value: [] for p_value in p_values} for method_name, _ in methods} for graph_type, _ in graph_types}
    fevals_history = {graph_type: {method_name: {p_value: [] for p_value in p_values} for method_name, _ in methods} for graph_type, _ in graph_types}

    # Ensure the results directory exists
    ensure_results_directory()

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

                        # Run QAOA optimization
                        approximation_ratio, total_fevals = run_qaoa_optimization(G, beta, gamma, method_name, max_cut_value)
                        ar_history[graph_type][method_name][p_value].append(approximation_ratio)
                        fevals_history[graph_type][method_name][p_value].append(total_fevals)
                    else:
                        print(f"Failed to get angles for {method_name}")
                        ar_history[graph_type][method_name][p_value].append(0)
                        fevals_history[graph_type][method_name][p_value].append(0)

    # Compute averages and standard deviations
    avg_ar_history = {graph_type: {method_name: {} for method_name, _ in methods} for graph_type, _ in graph_types}
    std_ar_history = {graph_type: {method_name: {} for method_name, _ in methods} for graph_type, _ in graph_types}
    avg_fevals_history = {graph_type: {method_name: {} for method_name, _ in methods} for graph_type, _ in graph_types}
    std_fevals_history = {graph_type: {method_name: {} for method_name, _ in methods} for graph_type, _ in graph_types}

    for graph_type in ar_history:
        for method_name in ar_history[graph_type]:
            for p_value in p_values:
                ar_list = ar_history[graph_type][method_name][p_value]
                fevals_list = fevals_history[graph_type][method_name][p_value]
                avg_ar_history[graph_type][method_name][p_value] = np.mean(ar_list)
                std_ar_history[graph_type][method_name][p_value] = np.std(ar_list)
                avg_fevals_history[graph_type][method_name][p_value] = np.mean(fevals_list)
                std_fevals_history[graph_type][method_name][p_value] = np.std(fevals_list)

    # Save results to CSV files
    for graph_type, _ in graph_types:
        # Save average approximation ratios
        with open(os.path.join('results', f'{graph_type.lower().replace(" ", "_")}_average_approximation_ratios.csv'), 'w', newline='') as csvfile:
            fieldnames = ['Method'] + [f'p={p}' for p in p_values]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for method_name, _ in methods:
                row = {'Method': method_name}
                row.update({f'p={p}': avg_ar_history[graph_type][method_name][p] for p in p_values})
                writer.writerow(row)

        # Save average number of function evaluations
        with open(os.path.join('results', f'{graph_type.lower().replace(" ", "_")}_average_function_evaluations.csv'), 'w', newline='') as csvfile:
            fieldnames = ['Method'] + [f'p={p}' for p in p_values]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for method_name, _ in methods:
                row = {'Method': method_name}
                row.update({f'p={p}': avg_fevals_history[graph_type][method_name][p] for p in p_values})
                writer.writerow(row)

    # Plot results
    for graph_type, _ in graph_types:
        # Plot average number of function evaluations
        plt.figure(figsize=(12, 6))
        for method_name, _ in methods:
            avg_fevals_list = [avg_fevals_history[graph_type][method_name][p] for p in p_values]
            std_fevals_list = [std_fevals_history[graph_type][method_name][p] for p in p_values]
            plt.errorbar(p_values, avg_fevals_list, yerr=std_fevals_list, marker='o', capsize=5, label=method_name)
        plt.xlabel('QAOA Depth p')
        plt.ylabel('Average Number of Function Evaluations')
        plt.title(f'Average Number of Function Evaluations vs QAOA Depth ({graph_type})')
        plt.legend()
        plt.grid(True)
        plt.xticks(p_values)
        plt.tight_layout()
        plt.savefig(os.path.join('results', f'{graph_type.lower().replace(" ", "_")}_average_function_evaluations.png'), dpi=300)
        plt.close()

        # Plot average approximation ratios
        plt.figure(figsize=(12, 6))
        for method_name, _ in methods:
            avg_ar_list = [avg_ar_history[graph_type][method_name][p] for p in p_values]
            std_ar_list = [std_ar_history[graph_type][method_name][p] for p in p_values]
            plt.errorbar(p_values, avg_ar_list, yerr=std_ar_list, marker='o', capsize=5, label=method_name)
        plt.xlabel('QAOA Depth p')
        plt.ylabel('Average Approximation Ratio')
        plt.title(f'Average Approximation Ratio vs QAOA Depth ({graph_type})')
        plt.legend()
        plt.grid(True)
        plt.xticks(p_values)
        plt.tight_layout()
        plt.savefig(os.path.join('results', f'{graph_type.lower().replace(" ", "_")}_average_approximation_ratios.png'), dpi=300)
        plt.close()

    # Add new plots comparing across all graph types
    graph_types = ['Uniform Random', '3-Regular', 'Power-Law Tree']
    methods = ['Random Initialization', 'QIBPI', 'TQA', 'Fixed Angles']
    p_values = [2, 3, 4, 5, 6, 7, 8, 9, 10]

    # Plot average approximation ratios across all graph types
    plt.figure(figsize=(15, 8))
    for method in methods:
        for graph_type in graph_types:
            avg_ar_list = [avg_ar_history[graph_type][method][p] for p in p_values]
            plt.plot(p_values, avg_ar_list, marker='o', label=f'{method} ({graph_type})')

    plt.xlabel('QAOA Depth p')
    plt.ylabel('Average Approximation Ratio')
    plt.title('Average Approximation Ratio vs QAOA Depth (All Graph Types)')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True)
    plt.xticks(p_values)
    plt.tight_layout()
    plt.savefig(os.path.join('results', 'all_graph_types_average_approximation_ratios.png'), dpi=300, bbox_inches='tight')
    plt.close()

    # Plot average function evaluations across all graph types
    plt.figure(figsize=(15, 8))
    for method in methods:
        for graph_type in graph_types:
            avg_fevals_list = [avg_fevals_history[graph_type][method][p] for p in p_values]
            plt.plot(p_values, avg_fevals_list, marker='o', label=f'{method} ({graph_type})')

    plt.xlabel('QAOA Depth p')
    plt.ylabel('Average Number of Function Evaluations')
    plt.title('Average Number of Function Evaluations vs QAOA Depth (All Graph Types)')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True)
    plt.xticks(p_values)
    plt.tight_layout()
    plt.savefig(os.path.join('results', 'all_graph_types_average_function_evaluations.png'), dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    compare_initializations()
