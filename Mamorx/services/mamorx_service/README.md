conda create -n mamorx-service python=3.12

pip install poetry

poetry add "crewai[tools]==0.51.1"
poetry add anthropic langchain-aws==0.1.17 grobid-client-python lxml bs4 ratelimit
poetry add boto3@1.34.162
poetry add "fastapi[standard]"
poetry add pydantic-settings