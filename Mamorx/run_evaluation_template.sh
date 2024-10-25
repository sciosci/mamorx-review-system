#!/bin/bash
OUTPUT_DIR=__REPLACE_WITH_OUTPUT_DIR__
INPUT_PDF_DIR=__REPLACE_WITH_PDF_DIR__
PROMPT_FILE=config/prompts.json
MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0 
WORKERS=8
HUMAN_REVIEW=

# Initialize conda
source ~/miniconda3/etc/profile.d/conda.sh

# Activate virtual environment
conda activate mamorx

# Run main script
python main.py \
    -o $OUTPUT_DIR \
    -i $INPUT_PDF_DIR \
    --prompt-file $PROMPT_FILE \
    --model-id $MODEL_ID \
    --workers $WORKERS \
    # --human-review $HUMAN_REVIEW 

# Deactivate virtual environment
conda deactivate