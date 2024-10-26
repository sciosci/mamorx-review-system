import re
import json

from langchain_aws import ChatBedrock
from MAMORX.schemas import PaperReviewResult, WorkflowPrompt, GrobidConfig


def text_converter(text:str)->str:
    # A function that takes a text and converts it to a JSONL compatible format
    text = text.replace('\n', '\\n')
    text = text.replace("\'","\\'" )
    text = re.sub(r'([{}\[\]])', r'\\\1', text)
    text = re.sub(r'(?<!\\)\\(?!["\\/bfnrt])', r'\\\\', text)

    return text 


def read_and_process(file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            return text_converter(content)
        except FileNotFoundError:
            print(f"Warning: File not found - {file_path}")
            return ""
        except Exception as e:
            print(f"Error processing file {file_path}: {str(e)}")
            return ""
        

def generate_jsonl_line(paper_id: str, title: str, pdf_path: str, 
                        human_reviewer_path: str, barebones_path: str, 
                        liang_etal_path: str, multi_agent_without_knowledge_path: str, 
                        multi_agent_with_knowledge_path: str) -> str:

    paper = PaperReviewResult(
        paper_id=paper_id,
        title=title,
        pdf_path=pdf_path,
        human_reviewer=human_reviewer_path,
        barebones=read_and_process(barebones_path),
        liang_etal=read_and_process(liang_etal_path),
        multi_agent_without_knowledge=read_and_process(multi_agent_without_knowledge_path),
        multi_agent_with_knowledge=read_and_process(multi_agent_with_knowledge_path)
    )

    # Convert to a single-line JSON string
    jsonl_line = json.dumps(paper, ensure_ascii=False, separators=(',', ':'))
    return jsonl_line


def load_json_file_as_dict(file_path: str):
    prompts = None
    with open(file_path, "r", encoding="utf8") as f:
        prompts = json.load(f)
    return prompts


def load_workflow_prompt(file_path: str) -> WorkflowPrompt:
    return load_json_file_as_dict(file_path)


def load_grobid_config(file_path: str) -> GrobidConfig:
    return load_json_file_as_dict(file_path)


def generate_response_with_bedrock(system_prompt: str, user_prompt: str, api_config: APIConfigs) -> str | List[str | dict]:
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
