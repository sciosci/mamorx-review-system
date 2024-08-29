Setup Papermage

conda create -n figure-agent python=3.11.9
conda install ipywidgets poppler ipykernel
pip install papermage[dev,predictors,visualizers] boto3 crewai crewai_tools pillow
pip install anthropic

Error libs
- dotenv 
- langchain_aws

If "ImportError: libGL.so.1": cannot open shared object file: No such file or directory"
sudo apt update
sudo apt install ffmpeg libsm6 libxext6