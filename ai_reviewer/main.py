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

    return PDFReviewResult(full_path=pdf_dir_path, name=pdf_dir_path.name, result=result)

def main(base_dir, pdf_dir_path, prompts_file, model_id, max_workers):
    base_path = Path(base_dir)
    base_path.mkdir(parents=True, exist_ok=True)

    # List pdf file paths
    pdf_dir = Path(pdf_dir_path)
    pdf_file_paths = [entry for entry in pdf_dir.glob("*/*.pdf")][:2]

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_pdf, base_dir, entry, prompts_file, model_id) for entry in pdf_file_paths]
        for future in as_completed(futures):
            try:
                result = future.result()
                print(f"Completed review for: {result['name']}")
            except Exception as e:
                print(f"An error occured: {str(e)}")
    

if __name__ == "__main__":
    # Define parameters
    BASE_DIR = Path(__file__).parent.parent   # Project dir
    PDF_NAME = '66.pdf' # PDF file name
    HUMAN_REVIER_PATH = ""  # Path to the human review data
    PROMPTS_FILE = os.path.join(BASE_DIR, 'data/prompts.json') # Prompt.json 
    MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"
    MAX_WORKERS = 1

    # Call the main function with parameters
    main(BASE_DIR, PDF_NAME, HUMAN_REVIER_PATH, PROMPTS_FILE, MODEL_ID)
