import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

import base64
import tempfile
import logging
import requests

from time import sleep
from redis import Redis

from app.config import settings
from app.schemas import ReviewJob, ReviewJobStatus
from MAMORX.schemas import APIConfigs, ReviewResult
from MAMORX.reviewer_workflow import ReviewerWorkflow


# Initialize Redis Client
redis_client = Redis(host=settings.redis_host, port=settings.redis_port, decode_responses=True, db=0)

# Test connection to grobid server
remaining_attempts = 10
connection_success = False
while(remaining_attempts > 0 and connection_success == False):
    response = None
    try:
        response = requests.get(f"{settings.grobid_server_url}/api/isalive")
    except:
        logging.error(f"Failed to connect to grobid server: remaining attempts {remaining_attempts}")
    if(response != None and response.status_code == 200):
        connection_success = True
    else:
        sleep(5)
    remaining_attempts -= 1
    

if(connection_success == False):
    logging.error("Failed to connect to grobid server shutting down now")
    exit(1)


# Initialize reviewer_workflow
reviewer_workflow = ReviewerWorkflow(
    prompt_file_path=settings.prompt_file,
    output_dir=settings.output_dir,
    api_config=APIConfigs(
        anthropic_model_id=settings.anthropic_model_id,
        openai_api_key=settings.openai_api_key,
        semantic_scholar_api_key=settings.semantic_scholar_api_key,
        openai_model_name=settings.openai_model_name,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        aws_default_region=settings.aws_default_region,
        figure_critic_url=settings.figure_critic_url
    ),
    grobid_config_file_path=settings.grobid_config_file_path,
    grobid_server_url=settings.grobid_server_url
)

def main():
    while(True):
        job_list = redis_client.brpop(keys=[settings.redis_queue_name])
        job = ReviewJob.model_validate_json(job_list[1])

        # Modify pdf content for logging purposes
        job_print = job.model_copy()
        job_print.pdf_content = b"abcd"

        # Update status of job to In-progress
        #   Get job status record
        job_status_json = redis_client.get(job.id)
        job_status = ReviewJobStatus.model_validate_json(job_status_json)
        job_status.status = "In-progress"
        #   Save to redis database
        update_result = redis_client.set(job.id, job_status.model_dump_json())
        # If update result is false requeue job
        if(update_result == False):
            redis_client.rpush(settings.redis_queue_name, job.model_dump_json())
            continue

        print(job_status_json, update_result)

        review_result = ReviewResult(
            review_content="",
            time_elapsed=0.0,
            novelty_assessment=None,
            figure_critic_assessment=None
        )
        try:
            # Save pdf_content to temporary file
            pdf_content = base64.b64decode(job.pdf_content)
            print(len(pdf_content))
        
            # Save PDF content to temporary file
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf:
                try:
                    temp_pdf.write(pdf_content)
                    temp_pdf.flush()

                    print(temp_pdf.name)
                    # Generate review based on reviewer_workflow
                    review_result = reviewer_workflow.generate_review(
                        pdf_file_path=temp_pdf.name,
                        review_method=job.review_type
                    )
                
                finally:
                    # Cleanup
                    os.unlink(temp_pdf.name)
        except Exception as e:
            review_result["review_content"] = f"Error analyzing PDF: {str(e)}"

        # Save results to ReviewJobStatus and Update job status to completed
        job_status.result = review_result
        job_status.status = "Completed"
        
        #   Save to redis database
        update_result = redis_client.set(job.id, job_status.model_dump_json())
        if(update_result == True):
            print("Success")
        else:
            print("Failed")
        
        

if __name__ == "__main__":
    main()