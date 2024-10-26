from langchain_aws import ChatBedrock
from typing import List
from MAMORX.schemas import APIConfigs, AgentPrompt


def generate_review_with_bedrock(system_prompt: str, user_prompt: str, api_config: APIConfigs) -> str | List[str | dict]:
    # Create llm object based on ChatBedrock
    llm = ChatBedrock(
        model_id=api_config['anthropic_model_id'],
        aws_access_key_id=api_config['aws_access_key_id'],
        aws_secret_access_key=api_config['aws_secret_access_key'],
        region=api_config["aws_default_region"]
    )

    # Construct messages for the model
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    # API call
    response = llm.invoke(messages)
    generated_review = response.content

    return generated_review


def generate_barebones_review(paper: str, prompts: AgentPrompt, api_config: APIConfigs):
    # Loading prompts
    bare_system_prompt = prompts['system_prompt']
    bare_task_prompt = prompts['task_prompt']

    # Format the prompts
    bare_formatted_task_prompt = bare_task_prompt.format(paper=paper)

    generated_review = generate_review_with_bedrock(
        system_prompt=bare_system_prompt,
        user_prompt=bare_formatted_task_prompt,
        api_config=api_config
    )

    return generated_review
    


def generate_liang_etal_review(title: str, paper: str, prompts: AgentPrompt, api_config: APIConfigs):
    # Getting prompts
    system_prompt = prompts['system_prompt']
    task_prompt = prompts['task_prompt']

    # Format the prompts
    formatted_task_prompt = task_prompt.format(title=title, paper=paper)

    generated_review = generate_review_with_bedrock(
        system_prompt=system_prompt,
        user_prompt=formatted_task_prompt,
        api_config=api_config
    )

    return generated_review
    


