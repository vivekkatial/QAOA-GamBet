# QAOA-Param-Server: API for QAOA Parameter Optimization

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


QAOA-Param-Server is a FastAPI-based server providing optimized parameters for the Quantum Approximate Optimization Algorithm (QAOA). It's built on top of various studies and research papers on QAOA and provides a simple API to get optimal parameters for a given graph and to optimize a graph using QAOA.

We thank the authors of the following papers for their work on QAOA:

- [QAOAKit: A Toolkit for Quantum Approximate Optimization Algorithm](https://www.computer.org/csdl/proceedings-article/qcs/2021/867400a064/1zxKuwgiuLS)
- [Quantum annealing initialization of the quantum approximate optimization algorithm](https://quantum-journal.org/papers/q-2021-07-01-491/#)

## API Quick Start

### Installation

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

### API Endpoints

### Example API Usage

```python
import requests

# Get optimal angles for a graph
response = requests.get('http://localhost:5000/optimal-angles', params={
 'graph': 'encoded_graph_structure',
 'p': 3
})
optimal_angles = response.json()

# Submit a graph for optimization
graph_data = {
 'graph': {...},  # Your graph structure
 'p': 3
}
response = requests.post('http://localhost:5000/optimize', json=graph_data)
optimization_result = response.json()
```

## Advanced Usage

For more advanced examples and usage of the underlying QAOAKit, please refer to the examples folder in the repository.

- Development
- Running the Server Locally

For development, you can run the server using Uvicorn:

```
uvicorn QAOAKit.api:app --reload
```

## Testing

Run the test suite with:

```
pytest
```

