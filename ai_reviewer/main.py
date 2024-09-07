from evaluation_data_workflow import ReviewSystemWorkflow
import os
from pathlib import Path
""" This would be the main function that initiate the PDF parsing processing and feed the data to the functions. This is just
    a skeleton of the function. Ideally the system should feed the text, titles, and other information as parameters for the 
    4 systems.
"""



def main(base_dir, pdf_path, human_review_path,  prompts_file, model_id):
    # Initialize & run the ReviewSystemWorkflow
    review_system = ReviewSystemWorkflow(base_dir, os.path.join(BASE_DIR, f"eval/acl_2017_pdfs/{PDF_NAME}"), human_review_path,prompts_file, model_id)
    result = review_system.run_workflow()


if __name__ == "__main__":
    # Define parameters
    BASE_DIR = Path(__file__).parent.parent   # Project dir
    PDF_NAME = '66.pdf' # PDF file name
    HUMAN_REVIER_PATH = ""  # Path to the human review data
    PROMPTS_FILE = os.path.join(BASE_DIR, 'data/prompts.json') # Prompt.json 
    MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"

    # Call the main function with parameters
    main(BASE_DIR, PDF_NAME, HUMAN_REVIER_PATH, PROMPTS_FILE, MODEL_ID)
