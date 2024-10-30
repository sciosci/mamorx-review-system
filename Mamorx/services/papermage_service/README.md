conda create -n papermage python=3.11

conda activate papermage

pip install poetry

poetry add 'papermage[dev,predictors,visualizers]'

poetry add python-poppler protobuf@4.25.5
