# Setup Papermage
Commands to install packages
<code>

conda create -n figure-agent python=3.11.9

conda install ipywidgets poppler ipykernel

pip install papermage[dev,predictors,visualizers]

pip install boto3 pillow  

pip install transformers==4.31.0  

pip install crewai crewai_tools   

pip install anthropic  

pip install python-dotenv

pip install langchain_aws

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