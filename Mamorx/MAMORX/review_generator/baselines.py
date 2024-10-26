from MAMORX.schemas import APIConfigs, AgentPrompt
from MAMORX.utils import generate_response_with_bedrock


def generate_barebones_review(paper: str, prompts: AgentPrompt, api_config: APIConfigs):
    # Loading prompts
    bare_system_prompt = prompts['system_prompt']
    bare_task_prompt = prompts['task_prompt']

    # Format the prompts
    bare_formatted_task_prompt = bare_task_prompt.format(paper=paper)

    generated_review = generate_response_with_bedrock(
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

    generated_review = generate_response_with_bedrock(
        system_prompt=system_prompt,
        user_prompt=formatted_task_prompt,
        api_config=api_config
    )

    return generated_review
    


