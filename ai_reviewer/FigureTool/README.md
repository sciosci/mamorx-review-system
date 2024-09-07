# Setup Papermage
Commands to install packages
<code>

conda create -n figure-agent python=3.11.9

conda install ipywidgets poppler ipykernel

pip install papermage[dev,predictors,visualizers]

pip install boto3 pillow  

pip install tokenizers==0.19.1 transformers==4.44.2

pip install anthropic  

pip install python-dotenv

pip install langchain_aws

pip install crewai==0.51.1 crewai_tools==0.12.0

pip install ratelimit

pip install lxml
</code>

# Common Error 1
If "ImportError: libGL.so.1": cannot open shared object file: No such file or directory"  
<code>
sudo apt update  
sudo apt install ffmpeg libsm6 libxext6  
</code>

# Removing conda environment
<code>
conda remove -n ENV_NAME --all  
</code>