import requests
import logging

from time import sleep
from app.config import settings
from MAMORX.schemas import APIConfigs
from MAMORX.reviewer_workflow import ReviewerWorkflow


# Test connection to grobid server
remaining_attempts = 10
connection_success = False
while(remaining_attempts > 0 and connection_success == False):
    response = None
    try:
        response = requests.get(f"{settings.grobid_server_url}/api/isalive")
    except:
        logging.error(f"Failed to connect to grobid server: remaining attempts {remaining_attempts}")
    if(response != None and response.status_code == 200):
        connection_success = True
    else:
        sleep(5)
    remaining_attempts -= 1
    

if(connection_success == False):
    logging.error("Failed to connect to grobid server shutting down now")
    exit(1)


reviewer_workflow = ReviewerWorkflow(
    prompt_file_path=settings.prompt_file,
    output_dir=settings.output_dir,
    api_config=APIConfigs(
        anthropic_model_id=settings.anthropic_model_id,
        openai_api_key=settings.openai_api_key,
        semantic_scholar_api_key=settings.semantic_scholar_api_key,
        openai_model_name=settings.openai_model_name,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        aws_default_region=settings.aws_default_region,
        figure_critic_url=settings.figure_critic_url
    ),
    grobid_config_file_path=settings.grobid_config_file_path,
    grobid_server_url=settings.grobid_server_url
)
