import logging
import argparse
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

from MAMORX.schemas import Paper
from MAMORX.ReviewerWorkflow import ReviewerWorkflow


def process_pdf(base_dir, pdf_file_path: Path, human_review_path: str, prompts_file_path: str, model_id) -> Paper:
    # Create output directory for pdf file
    path_segment = "/".join(str(pdf_file_path).split("/")[-2:])[:-4]
    base_pdf_dir = Path(f"{base_dir}/{path_segment}")
    base_pdf_dir.mkdir(parents=True, exist_ok=True) 


    # Parse PDF to JSON

    # Initialize review workflow
    reviewer_workflow = ReviewerWorkflow(
        prompt_file_path=prompts_file_path, 
        output_dir=base_dir)

    prompts = reviewer_workflow.get_prompts()
    

    # 

    # Initialize & run the ReviewSystemWorkflow
    # review_system = ReviewSystemWorkflow(base_pdf_dir, str(pdf_file_path), human_review_path,prompts_file, model_id)
    # result = review_system.run_workflow()
    # result = ""

    return Paper()


def main():
    # parse arguments
    parser = argparse.ArgumentParser(description="""
    An evaluation of AI generated reviews by MAMORX
""")
    parser.add_argument("-o", "--output-dir", help="output directory", required=True)
    parser.add_argument("-i", "--input-dir", help="directory with subdirectories containing pdf files", required=True)
    parser.add_argument("--human-review", help="directory with human reviews", required=False)
    parser.add_argument("--prompt-file", help="path to prompt.json", default="config/prompts.json")
    parser.add_argument("--model-id", help="model id for anthropic claude", default="anthropic.claude-3-5-sonnet-20240620-v1:0")
    parser.add_argument("--workers", help="max number of workers to process all PDFs in parallel", default=8, type=int)

    arg_list= parser.parse_args()
    
    base_dir = arg_list.output_dir   # Project dir
    pdf_dir_path = arg_list.input_dir
    human_review_path = arg_list.human_review  # Path to the human review data
    prompts_file = arg_list.prompt_file # Prompt.json 
    model_id = arg_list.model_id
    max_workers = arg_list.workers

    base_path = Path(base_dir)
    base_path.mkdir(parents=True, exist_ok=True)

    # Create log file
    logging.basicConfig(filename=base_path / "log.out",
                        level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(processName)s %(message)s"
                        )
    
    logging.info("Started Review Generation Process")

    # List pdf file paths
    pdf_dir = Path(pdf_dir_path)
    pdf_file_paths = [entry for entry in pdf_dir.glob("*/*.pdf")][:1]

    for e in pdf_file_paths:
        print(e)

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_pdf, base_dir, entry, human_review_path, prompts_file, model_id) for entry in pdf_file_paths]
        for future in as_completed(futures):
            try:
                result = future.result()
                print(f"Completed review for: {result}")
            except Exception as e:
                print(f"An error occured: {str(e)}")
    
    logging.info("Review Generation Complete")
    

if __name__ == "__main__":
    main()
