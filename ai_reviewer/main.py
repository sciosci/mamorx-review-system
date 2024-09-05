from review_system_workflow import ReviewSystemWorkflow
import os
""" This would be the main function that initiate the PDF parsing processing and feed the data to the functions. This is just
    a skeleton of the function. Ideally the system should feed the text, titles, and other information as parameters for the 
    4 systems.
"""

def main(base_dir, pdf_path, prompts_file, model_id):
    # Initialize & run the ReviewSystemWorkflow
    review_system = ReviewSystemWorkflow(base_dir, pdf_path, prompts_file, model_id)
    result = review_system.run_workflow()


if __name__ == "__main__":
    # Define parameters
    BASE_DIR = '/'    # Project dir
    PDF_PATH = '/'    # PDF path
    PROMPTS_FILE = '/' # Prompt.json 
    MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"

    # Call the main function with parameters
    main(BASE_DIR, PDF_PATH, PROMPTS_FILE, MODEL_ID)
