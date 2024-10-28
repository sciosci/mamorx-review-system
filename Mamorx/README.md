# MAMORX Review System
Required python version 3.12

## For this release using crewai 0.51.1   
Do the following to setup

conda create -n mamorx python=3.12 

conda activate mamorx  

pip install -r requirements-crewai-0.51.1.txt

## Future release for ollama compatibility and crewai 0.76.2 [Still not fully functional]
Do the following to setup

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
poetry add crewai[tools]
poetry add anthropic grobid-client-python boto3 magic-python lxml bs4 langchain-aws
