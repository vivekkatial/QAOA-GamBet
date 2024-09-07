from setuptools import setup, find_packages

# read the contents of README file
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


setup(
    name="QAOAKit",
    version="0.1.13",
    description="An API for QAOA Parameter Optimization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Vivek Katial",
    python_requires=">=3, <4",
    packages=find_packages("."),
    install_requires=[
        # Fixed version packages: high chance that using other versions might not work.
        "qiskit==1.0.2",
        "qiskit-aer==0.13.3",
        "pynauty==1.1.2",
        "scikit-learn==1.4.1.post1",
        "qiskit-optimization==0.6.1",

        # Fixing version, to have a complete working setup for QAOAKit.
        "pandas==2.2.1",
        "networkx==3.2.1",
        "numpy==1.26.4",
        "pytest==8.1.1",
        "tqdm==4.66.2",
        "cvxgraphalgs==0.1.2",
        "cvxopt==1.3.2",
        "notebook==7.1.2",
        "matplotlib==3.8.3",
        "seaborn==0.13.2",
        # Add stuff needed for the FastAPI server
        "fastapi==0.110.1",
        "uvicorn==0.29.0",
        "pydantic==2.7.0",
        "python-dotenv==1.0.1",
    ],
    zip_safe=True,
)
