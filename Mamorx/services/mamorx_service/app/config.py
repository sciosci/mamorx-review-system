from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "MAMORX API Service"
    version: str = "0.1.0"
    output_dir: str
    prompt_file: str
    anthropic_model_id: str
    openai_api_key: str
    semantic_scholar_api_key: str
    openai_model_name: str
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_default_region: str
    figure_critic_url: str
    grobid_config_file_path: str
    grobid_server_url: str

settings = Settings()