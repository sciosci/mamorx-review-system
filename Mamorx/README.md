# MAMORX Review System
Required python version 3.12

pip install -r requirements.txt

pip install grobid_client_python

Alternative with poetry
conda create -n mamorx python=3.12

conda activate mamorx

pip install poetry

poetry install --no-root



# Papermage Service

Note : Papermage has conflicting dependencies with many packages of crewai. Therefore, it will be implemented as a seperate service/api server. Potentially use gRPC for communication between papermage service and MAMORX figure assessment

conda create -n mamorx python=3.11   
conda activate mamorx  
sudo apt install -y pkg-config libpoppler-cpp-dev


# Used when pyproject.toml is missing
poetry init  
poetry add anthropic grobid-client-python boto3 magic-python python-poppler crewai[tools] lxml bs4 langchain-aws
