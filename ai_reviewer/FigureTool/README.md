Setup Papermage

conda create -n figure-agent python=3.11.9
conda install ipywidgets poppler ipykernel
pip install papermage[dev,predictors,visualizers]
pip install boto3 pillow 
pip instal transformers==4.31.0
pip install crewai crewai_tools 
pip install anthropic

If "ImportError: libGL.so.1": cannot open shared object file: No such file or directory"
sudo apt update
sudo apt install ffmpeg libsm6 libxext6

conda remove -n ENV_NAME --all