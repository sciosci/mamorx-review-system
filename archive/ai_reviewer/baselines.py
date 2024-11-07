import json
from dotenv import load_dotenv
from langchain_aws import ChatBedrock
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
with open(os.path.join(BASE_DIR, 'data/prompts.json'), "r", encoding="utf-8") as f:
    prompts = json.load(f)

def generate_barebones_review(paper: str, prompt_file: str = "prompts.json"):
    # Loading prompts
    with open(prompt_file, "r", encoding="utf-8") as f:
        prompts = json.load(f)

    bare_system_prompt = prompts['barebones']['system_prompt']
    bare_task_prompt = prompts['barebones']['task_prompt']

    # Format the prompts
    bare_formatted_task_prompt = bare_task_prompt.format( paper=paper)

     # Load env
    load_dotenv()
    env_vars = ['OPENAI_API_KEY', 'OPENAI_MODEL_NAME', 'BROWSERBASE_PROJECT_ID', 
                    'AWS_ACCESS_KEY_ID','AWS_SECRET_ACCESS_KEY', 'AWS_DEFAULT_REGION']
    for var in env_vars:
        os.environ[var] = os.getenv(var, '')
    model_id = 'anthropic.claude-3-5-sonnet-20240620-v1:0'
    llm = ChatBedrock(model_id=model_id)

    # Construct messages for the model
    bare_messages = [
        {"role": "system", "content": bare_system_prompt},
        {"role": "user", "content": bare_formatted_task_prompt}
    ]

    # API call
    bare_response = llm.invoke(bare_messages)
    bare_generated_review = bare_response.content

    return bare_generated_review
    


def generate_liang_etal_review(title: str, paper: str, prompt_file: str = "prompts.json"):
    # Loading prompts
    with open(prompt_file, "r", encoding="utf-8") as f:
        prompts = json.load(f)

    # Getting prompts
    system_prompt = prompts['liang_et_al']['system_prompt']
    task_prompt = prompts['liang_et_al']['task_prompt']

    # Format the prompts
    formatted_task_prompt = task_prompt.format(title=title, paper=paper)

    # Load env
    load_dotenv()
    env_vars = ['OPENAI_API_KEY', 'OPENAI_MODEL_NAME', 'BROWSERBASE_PROJECT_ID', 
                    'AWS_ACCESS_KEY_ID','AWS_SECRET_ACCESS_KEY', 'AWS_DEFAULT_REGION']
    for var in env_vars:
        os.environ[var] = os.getenv(var, '')
    model_id = 'anthropic.claude-3-5-sonnet-20240620-v1:0'
    llm = ChatBedrock(model_id=model_id)

    # Construct messages for the model
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": formatted_task_prompt}
    ]

    # API call
    response = llm.invoke(messages)
    generated_review = response.content

    return generated_review

