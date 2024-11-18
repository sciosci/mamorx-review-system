import os
import tempfile

from typing import Annotated, Literal, List
from fastapi import APIRouter, UploadFile, File, Header

from MAMORX.schemas import ReviewResult
from app.reviewer import reviewer_workflow
from app.config import settings
from app.schemas import ReviewJobStatus, ReviewType, SessionJobs, ReviewJob
from app.redis import \
    submit_job_to_queue, \
    add_job_data, \
    get_job_data_for_session_id, \
    get_queue_content
from app.helper.utils import create_review_job


router = APIRouter()

@router.post("/review-pdf-paper", response_model=ReviewResult)
async def review_pdf_paper(
    pdf_file: Annotated[UploadFile, File()],
    review_type: Literal["barebones", "liangetal", "multiagent", "mamorx"]
):
    file_content = pdf_file.file

    file_content_bytes = file_content.read()

    if(settings.disable_review):
        return ReviewResult(
            review_content=f"PDF file size : {len(file_content_bytes)}",
            time_elapsed=0,
            novelty_assessment=None,
            figure_critic_assessment=None
        )

    review_result = ReviewResult(
        review_content="",
        time_elapsed=0.0,
        novelty_assessment=None,
        figure_critic_assessment=None
    )

    try:
        # Save PDF content to temporary file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf:
            try:
                temp_pdf.write(file_content_bytes)
                temp_pdf.flush()

                print(temp_pdf.name)
                review_result = reviewer_workflow.generate_review(
                    pdf_file_path=temp_pdf.name,
                    review_method=review_type
                )
            
            finally:
                # Cleanup
                os.unlink(temp_pdf.name)
    except Exception as e:
        return f"Error analyzing PDF: {str(e)}"

    return review_result


@router.post("/submit-pdf-to-queue", response_model=ReviewJobStatus)
async def submit_pdf_to_queue(
    pdf_file: Annotated[UploadFile, File()],
    review_type: ReviewType,
    session_id: Annotated[str, Header()]
):
    # Read file contents
    pdf_data = await pdf_file.read()
    
    job_to_submit = create_review_job(
        pdf_data=pdf_data,
        session_id=session_id,
        review_type=review_type
    )

    # Submit job to queue
    submit_job_to_queue(job_to_submit)

    # Create job status object
    review_status = ReviewJobStatus(
        id=job_to_submit.id,
        status="Queued",
        result=None
    )

    # Add job status to database (using redis for simplicity)
    add_job_data(review_status)

    return review_status


@router.get("/review-jobs", response_model=SessionJobs)
async def get_jobs_for_session_id(
    session_id: Annotated[str, Header()]
):
    # Query jobs with session_id
    job_list = get_job_data_for_session_id(session_id)

    if(job_list == None):
        job_list = list()

    # Create SessionJobs Object
    session_jobs = SessionJobs(
        count=len(job_list),
        jobs=job_list
    )

    return session_jobs


@router.get("/queue", response_model=List[ReviewJob])
async def get_queue():
    queue = get_queue_content()

    return queue