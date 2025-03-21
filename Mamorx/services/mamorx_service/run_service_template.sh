export OUTPUT_DIR=
export PROMPT_FILE=../../config/prompts.json
export ANTHROPIC_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0 
export OPENAI_API_KEY=
export SEMANTIC_SCHOLAR_API_KEY=
export OPENAI_MODEL_NAME=gpt-4o-mini
export AWS_ACCESS_KEY_ID=
export AWS_SECRET_ACCESS_KEY=
export AWS_DEFAULT_REGION=
export FIGURE_CRITIC_URL=localhost:5001
export GROBID_CONFIG_FILE_PATH=../../config/grobid_config.json
export GROBID_SERVER_URL=http://localhost:8070
export DISABLE_REVIEW=False
export REDIS_HOST=localhost
export REDIS_PORT=6379
export REDIS_QUEUE_NAME=review-queue

fastapi dev app/main.py