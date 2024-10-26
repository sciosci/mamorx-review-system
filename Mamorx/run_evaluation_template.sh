#!/bin/bash
OUTPUT_DIR=__REPLACE_WITH_OUTPUT_DIR__
INPUT_PDF_DIR=__REPLACE_WITH_PDF_DIR__
PROMPT_FILE=config/prompts.json
ANTHROPIC_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0 
WORKERS=8
HUMAN_REVIEW=
OPENAI_API_KEY=
SEMANTIC_SCHOLAR_API_KEY=
OPENAI_MODEL_NAME=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_DEFAULT_REGION=

# Initialize conda
source ~/miniconda3/etc/profile.d/conda.sh

# Activate virtual environment
conda activate mamorx

# Run main script
python main.py \
    -o $OUTPUT_DIR \
    -i $INPUT_PDF_DIR \
    --prompt-file $PROMPT_FILE \
    --anthropic-model-id $ANTHROPIC_MODEL_ID \
    --workers $WORKERS \
    --openai-api-key $OPENAI_API_KEY \
    --semantic-scholar-api-key $SEMANTIC_SCHOLAR_API_KEY \
    --openai-model-name $OPENAI_MODEL_NAME \
    --aws-access-key-id $AWS_ACCESS_KEY_ID \
    --aws-secret-access-key $AWS_SECRET_ACCESS_KEY \
    --aws-default-region $AWS_DEFAULT_REGION
    # --human-review $HUMAN_REVIEW  

# Deactivate virtual environment
conda deactivate