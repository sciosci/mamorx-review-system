from evaluation_data_workflow import ReviewSystemWorkflow
import os
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import TypedDict
""" This would be the main function that initiate the PDF parsing processing and feed the data to the functions. This is just
    a skeleton of the function. Ideally the system should feed the text, titles, and other information as parameters for the 
    4 systems.
"""

class PDFReviewResult(TypedDict):
    full_path: Path
    name: str
    result: str


def process_pdf(base_dir, pdf_file_path: Path, human_review_path: str, prompts_file, model_id) -> PDFReviewResult:
    # Create output directory for pdf file
    path_segment = "/".join(str(pdf_file_path).split("/")[-2:])[:-4]
    base_pdf_dir = Path(f"{base_dir}/{path_segment}")
    base_pdf_dir.mkdir(parents=True, exist_ok=True) 

    # Initialize & run the ReviewSystemWorkflow
    review_system = ReviewSystemWorkflow(base_pdf_dir, str(pdf_file_path), human_review_path,prompts_file, model_id)
    result = review_system.run_workflow()
    # result = ""

    return PDFReviewResult(full_path=pdf_file_path, name=pdf_file_path.name, result=result)


def main(base_dir, pdf_dir_path, human_review_path,  prompts_file, model_id, max_workers):
    base_path = Path(base_dir)
    base_path.mkdir(parents=True, exist_ok=True)

    # List pdf file paths
    pdf_dir = Path(pdf_dir_path)
    pdf_file_paths = [entry for entry in pdf_dir.glob("*/*.pdf")]

    for e in pdf_file_paths:
        print(e)

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_pdf, base_dir, entry, human_review_path, prompts_file, model_id) for entry in pdf_file_paths]
        for future in as_completed(futures):
            try:
                result = future.result()
                print(f"Completed review for: {result['name']}")
            except Exception as e:
                print(f"An error occured: {str(e)}")
    

if __name__ == "__main__":
    # Define parameters
    BASE_DIR = "_BASE_OUT_DIR_"   # Project dir
    INPUT_PDF_DIR = "_PDF_IN_eval_dir"
    HUMAN_REVIEW_PATH = ""  # Path to the human review data
    PROMPTS_FILE = "_PROMPT_FILE_IN_data/prompts.json" # Prompt.json 
    MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"
    MAX_WORKERS = 8

    # Call the main function with parameters
    main(BASE_DIR, INPUT_PDF_DIR, HUMAN_REVIEW_PATH, PROMPTS_FILE, MODEL_ID, MAX_WORKERS)
