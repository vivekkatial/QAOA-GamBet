# QAOA-Param-Server: API for QAOA Parameter Optimization

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95.1-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/release/python-390/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Build Status](https://github.com/vivekkatial/QAOA-Param-Server/actions/workflows/main.yml/badge.svg)


QAOA-Param-Server is a FastAPI-based server providing optimized parameters for the Quantum Approximate Optimization Algorithm (QAOA). It offers a simple API to obtain optimal parameters for a given graph and to optimize graphs using QAOA.

## Table of Contents

- [Background](#background)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## Background

The Quantum Approximate Optimization Algorithm (QAOA) is a hybrid quantum-classical algorithm designed to solve combinatorial optimization problems. This project builds upon various studies and research papers on QAOA to provide efficient parameter optimization.

We thank the authors of the following papers for their work on QAOA:

- [QAOAKit: A Toolkit for Quantum Approximate Optimization Algorithm](https://www.computer.org/csdl/proceedings-article/qcs/2021/867400a064/1zxKuwgiuLS)
- [Quantum annealing initialization of the quantum approximate optimization algorithm](https://quantum-journal.org/papers/q-2021-07-01-491/)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/vivekkatial/QAOA-Param-Server.git
cd QAOA-Param-Server
```

2. Build the Docker image:

```bash
docker build -t qaoa-param-server .
```

3. Run the Docker container:

```bash
# Run in development mode
docker run -p 5000:5000 -v $(pwd):/app -e DEV_MODE=true qaoa-param-server

# Run in production mode
docker run -p 5000:5000 qaoa-param-server
```

The API will be available at `http://localhost:5000`.


## Authentication

QAOA-Param-Server uses Basic Authentication to secure the API endpoints. To access the API, you need to provide a username and password with each request.

### Setting up Authentication

1. Create a `.env` file in the root directory of the project.
2. Add the following lines to the `.env` file:

```
BASIC_AUTH_USERNAME=your_username
BASIC_AUTH_PASSWORD=your_password
```

Replace `your_username` and `your_password` with your desired credentials.

### Using Authentication in Requests

When making requests to the API, you need to include the authentication credentials. Here's an example using Python's `requests` library and the `QIBPI` endpoint:

```python
import requests

url = "http://localhost:5000/graph/QIBPI/optimal_angles"
data = {
    "adjacency_matrix": [[0.0, 0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 1.0, 0.0, 0.0], [0.0, 1.0, 0.0, 1.0, 0.0], [1.0, 0.0, 1.0, 0.0, 1.0], [0.0, 0.0, 0.0, 1.0, 0.0]], 
    "p": 3,
    "graph_type": "uniform_random",
    "weight_type": "uniform"
}

response = requests.post(url, json=data, auth=('admin', 'gmkit123'))

if response.status_code == 200:
    print("Success:", response.json())
else:
    print("Error:", response.status_code, response.text)
```

Make sure to replace `'your_username'` and `'your_password'` with the actual credentials you set in the `.env` file.

**Note**: Keep your `.env` file secure and never commit it to version control. Add it to your `.gitignore` file to prevent accidental commits.

## Usage

Here's a basic example of how to use the QAOA-Param-Server API:

```python
import requests
import networkx as nx
import json

# Create a sample graph
G = nx.random_regular_graph(3, 8)
adjacency_matrix = nx.to_numpy_array(G).tolist()

# Prepare the request data
data = {
    "adjacency_matrix": adjacency_matrix,
    "p": 3,
    "instance_class": "three_regular_graph"
}

# Send a request to get optimal angles
response = requests.post(
    "http://localhost:5000/graph/QAOAKit/optimal_angles_lookup",
    json=data,
    auth=('username', 'password')  # Replace with your actual credentials
)

if response.status_code == 200:
    optimal_angles = response.json()
    print("Optimal angles:", json.dumps(optimal_angles, indent=2))
else:
    print("Error:", response.status_code, response.text)
```

## API Documentation

The QAOA-Param-Server provides the following main endpoints:

- `/graph/QAOAKit/optimal_angles_kde`: Get optimal angles using KDE estimation
- `/graph/QAOAKit/optimal_angles_lookup`: Get optimal angles using lookup table
- `/graph/QIBPI/optimal_angles`: Get optimal angles using QIBPI method
- `/graph/random_initialisation`: Get random initialization angles
- `/graph/tqa_initialisation`: Get TQA initialization angles

For full API documentation, run the server and visit `http://localhost:5000/docs` for the Swagger UI or this link for the ReDoc UI: `http://localhost:5000/redoc`.


## Contributing

We welcome contributions to the `QAOA-Param-Server` project! Please follow these steps to contribute:

1. Fork the repository
2. Create a new branch for your feature or bug fix
3. Make your changes and commit them with clear, descriptive messages
4. Push your changes to your fork
5. Submit a pull request to the main repository

Please ensure your code adheres to the project's coding standards (we use Black for formatting) and include appropriate tests for new features.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.