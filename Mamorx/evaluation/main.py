import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import logging
import argparse
import json
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

from MAMORX.schemas import PaperReviewResult, APIConfigs
from MAMORX.reviewer_workflow import ReviewerWorkflow


def process_pdf_paper(base_dir, pdf_file_path: Path, human_review_path: str, prompts_file_path: str, api_config: APIConfigs, grobid_config_file_path: str, save_to_file: bool=False) -> PaperReviewResult:
    
    # Create output directory for pdf file
    path_segment = "/".join(str(pdf_file_path).split("/")[-2:])[:-4]
    base_pdf_dir = Path(f"{base_dir}/{path_segment}")
    base_pdf_dir.mkdir(parents=True, exist_ok=True) 

    # Initialize review workflow
    reviewer_workflow = ReviewerWorkflow(
        prompt_file_path=prompts_file_path, 
        output_dir=base_dir,
        api_config=api_config,
        grobid_config_file_path=grobid_config_file_path
    )

    # Run review workflow
    review_result = reviewer_workflow.run_workflow(str(pdf_file_path))
    
    # Save results to file
    if(save_to_file):
        output_file_path = "{}/{}.json".format(base_pdf_dir, review_result["paper_id"])
        with open(output_file_path, "w") as f:
            json.dump(review_result, f, ensure_ascii=False, separators=(',', ':'), indent=4)

    return review_result


def main():
    # parse arguments
    parser = argparse.ArgumentParser(description="""
    An evaluation of AI generated reviews by MAMORX
""")
    parser.add_argument("-o", "--output-dir", help="output directory", required=True)
    parser.add_argument("-i", "--input-dir", help="directory with subdirectories containing pdf files", required=True)
    parser.add_argument("--human-review", help="directory with human reviews", required=False)
    parser.add_argument("--prompt-file", help="path to prompt.json", default="config/prompts.json")
    parser.add_argument("--anthropic-model-id", help="model id for anthropic", default="anthropic.claude-3-5-sonnet-20240620-v1:0")
    parser.add_argument("--workers", help="max number of workers to process all PDFs in parallel", default=8, type=int)
    parser.add_argument("--openai-api-key", help="OpenAI API key", required=True)
    parser.add_argument("--semantic-scholar-api-key", help="Semantic Scholar API key", required=True)
    parser.add_argument("--openai-model-name", help="OpenAI model name", default="gpt-4o-mini")
    parser.add_argument("--aws-access-key-id", help="AWS access key id", required=True)
    parser.add_argument("--aws-secret-access-key", help="AWS secret access key", required=True)
    parser.add_argument("--aws-default-region", help="AWS default region", required=True)
    parser.add_argument("--figure-critic-url", help="URL of figure critic service", default="localhost:5001")
    parser.add_argument("--grobid-config", help="Path to grobid_config.json", default="config/grobid_config.json")
    

    arg_list= parser.parse_args()
    
    base_dir = arg_list.output_dir   # Project dir
    pdf_dir_path = arg_list.input_dir
    human_review_path = arg_list.human_review  # Path to the human review data
    prompts_file = arg_list.prompt_file # Prompt.json 
    max_workers = arg_list.workers
    api_config: APIConfigs = APIConfigs(
        anthropic_model_id = arg_list.anthropic_model_id,
        openai_api_key=arg_list.openai_api_key,
        semantic_scholar_api_key=arg_list.semantic_scholar_api_key,
        openai_model_name=arg_list.openai_model_name,
        aws_access_key_id=arg_list.aws_access_key_id,
        aws_secret_access_key=arg_list.aws_secret_access_key,
        aws_default_region=arg_list.aws_default_region,
        figure_critic_url=arg_list.figure_critic_url
    )
    grobid_config_file_path = arg_list.grobid_config

    base_path = Path(base_dir)
    base_path.mkdir(parents=True, exist_ok=True)

    # Create log file
    logging.basicConfig(filename=base_path / "log.out",
                        level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(processName)s %(module)s %(message)s",
                        force=True
                        )
    
    logging.info("Started Review Generation Process")

    # List pdf file paths
    pdf_dir = Path(pdf_dir_path)
    pdf_file_paths = [entry for entry in pdf_dir.glob("*/*.pdf")][:1]

    for e in pdf_file_paths:
        print(e)

    for entry in pdf_file_paths:
        try:
            result = process_pdf_paper(base_dir, entry, human_review_path, prompts_file, api_config, grobid_config_file_path, True)
            logging.info(f"Completed review for: {result['title']}")
        except Exception as e:
            logging.info(f"An error occured: {str(e)}")
        
    # with ProcessPoolExecutor(max_workers=max_workers) as executor:
    #     futures = [executor.submit(process_pdf_paper, base_dir, entry, human_review_path, prompts_file, api_config, grobid_config_file_path, True) for entry in pdf_file_paths]
    #     for future in as_completed(futures):
    #         try:
    #             result = future.result()
    #             logging.info(f"Completed review for: {result['title']}")
    #         except Exception as e:
    #             logging.info(f"An error occured: {str(e)}")
    
    logging.info("Review Generation Complete")
    

if __name__ == "__main__":
    main()
