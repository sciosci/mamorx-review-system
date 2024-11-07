from app.config import settings

from MAMORX.schemas import APIConfigs
from MAMORX.reviewer_workflow import ReviewerWorkflow


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
